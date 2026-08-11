//! Spawns the sidecar (bundled binary or dev python fallback) and reads the
//! stdout handshake on a background thread.

use std::io::BufRead;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::Duration;

use crate::handshake::{self, Handshake};

pub const HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(15);
pub const OUTPUT_HISTORY: usize = 50;

/// The repo root baked at compile time (dev checkout); overridable at
/// runtime via ITEMBANK_ROOT.
const REPO_ROOT: &str = env!("ITEMBANK_REPO_ROOT");

pub struct SidecarHandle {
    pub child: Child,
    pub pid: u32,
    pub output: Arc<Mutex<Vec<String>>>,
    handshake_rx: mpsc::Receiver<Option<Handshake>>,
}

impl SidecarHandle {
    pub fn wait_handshake(&self, timeout: Duration) -> std::io::Result<Handshake> {
        match self.handshake_rx.recv_timeout(timeout) {
            Ok(Some(hs)) => Ok(hs),
            Ok(None) => Err(std::io::Error::new(
                std::io::ErrorKind::UnexpectedEof,
                "sidecar stdout closed before the handshake completed",
            )),
            Err(_) => Err(std::io::Error::new(
                std::io::ErrorKind::TimedOut,
                "sidecar handshake timed out",
            )),
        }
    }
}

fn bundled_sidecar_path() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    let dir = exe.parent()?;
    for triple in ["x86_64-pc-windows-msvc", "x86_64-pc-windows-gnu"] {
        let candidate = dir.join(format!("itembank-sidecar-{triple}.exe"));
        if candidate.exists() {
            return Some(candidate);
        }
    }
    None
}

pub fn spawn(banks_dir: &Path) -> std::io::Result<SidecarHandle> {
    let root = std::env::var_os("ITEMBANK_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(REPO_ROOT));
    let python = std::env::var_os("ITEMBANK_PYTHON").unwrap_or_else(|| "python".into());

    let (program, args) = match bundled_sidecar_path() {
        Some(binary) => (
            binary,
            vec![
                "--no-open".to_string(),
                "--port".to_string(),
                "0".to_string(),
            ],
        ),
        None => (
            PathBuf::from(python),
            vec![
                "-u".to_string(),
                root.join("itembank.py").display().to_string(),
                "sidecar".to_string(),
                banks_dir.display().to_string(),
                "--no-open".to_string(),
                "--port".to_string(),
                "0".to_string(),
            ],
        ),
    };

    let mut cmd = Command::new(&program);
    cmd.args(&args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = cmd.spawn()?;
    let pid = child.id();
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::Other, "sidecar stdout unavailable"))?;

    let output: Arc<Mutex<Vec<String>>> = Arc::new(Mutex::new(Vec::new()));
    let (tx, rx) = mpsc::channel();
    let out = Arc::clone(&output);
    thread::spawn(move || {
        let mut reader = std::io::BufReader::new(stdout);
        let mut line = String::new();
        let mut accumulated = String::new();
        let mut sent = false;
        loop {
            line.clear();
            match reader.read_line(&mut line) {
                Ok(0) => break,
                Ok(_) => {
                    let mut buf = out.lock().unwrap();
                    buf.push(line.trim_end().to_string());
                    if buf.len() > OUTPUT_HISTORY {
                        buf.remove(0);
                    }
                    drop(buf);
                    accumulated.push_str(&line);
                    if !sent {
                        if let Some(hs) = handshake::parse(&accumulated) {
                            sent = true;
                            let _ = tx.send(Some(hs));
                        }
                    }
                }
                Err(_) => break,
            }
        }
        if !sent {
            let _ = tx.send(None);
        }
    });

    Ok(SidecarHandle {
        child,
        pid,
        output,
        handshake_rx: rx,
    })
}
