#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod handshake;
mod job_object;
mod liveness;
mod proxy;
mod sidecar;
mod single_instance;

use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use tauri::menu::{Menu, MenuItem, Submenu};
use tauri::{AppHandle, Manager, Url, WebviewUrl, WebviewWindow};
use tauri_plugin_clipboard_manager::ClipboardExt;

use windows_sys::Win32::Foundation::{BOOL, HWND};
use windows_sys::Win32::UI::WindowsAndMessaging::{
    EnumWindows, GetWindowTextW, GetWindowThreadProcessId, IsWindowVisible, SetForegroundWindow,
};

struct ShellState {
    state: Mutex<liveness::State>,
    sidecar_port: Mutex<Option<u16>>,
    token: Mutex<Option<String>>,
    proxy_port: Mutex<Option<u16>>,
    proxy: Mutex<Option<Arc<proxy::Proxy>>>,
    sidecar_pid: Mutex<Option<u32>>,
    started_at: Mutex<Option<String>>,
    sidecar_path: Mutex<Option<String>>,
    log_path: Mutex<Option<String>>,
    output: Arc<Mutex<Vec<String>>>,
}

impl ShellState {
    fn new() -> ShellState {
        ShellState {
            state: Mutex::new(liveness::State::Starting),
            sidecar_port: Mutex::new(None),
            token: Mutex::new(None),
            proxy_port: Mutex::new(None),
            proxy: Mutex::new(None),
            sidecar_pid: Mutex::new(None),
            started_at: Mutex::new(None),
            sidecar_path: Mutex::new(None),
            log_path: Mutex::new(None),
            output: Arc::new(Mutex::new(Vec::new())),
        }
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .invoke_handler(tauri::generate_handler![restart_runtime, focus_running_instance])
        .setup(|app| {
            let app_handle = app.handle().clone();
            let window = app
                .get_webview_window("main")
                .ok_or("main window missing")?;
            if std::env::var_os("ITEMBANK_HEADLESS").is_some() {
                let _ = window.hide();
            }

            let app_state = Arc::new(ShellState::new());
            app.manage(app_state.clone());

            match single_instance::SingleInstance::acquire() {
                Some(instance) => {
                    // Kept open for the process lifetime via a leak: closing it
                    // would let a second instance acquire mid-run.
                    let _ = Box::leak(Box::new(instance));
                }
                None => {
                    // Another instance: attach by focusing its window; when
                    // attach fails, refuse by name and never spawn a sidecar.
                    if focus_existing_window() {
                        std::process::exit(0);
                    }
                    show_state(&app_handle, &window, &app_state, liveness::State::PortHeldRefused)?;
                    return Ok(());
                }
            }

            let job = job_object::JobObject::create().ok();
            let banks_dir = banks_dir();
            spawn_and_connect(&app_handle, &window, &app_state, job, &banks_dir)?;
            Ok(())
        })
        .on_menu_event(|app, event| match event.id().as_ref() {
            "runtime_status" => {
                let _ = open_runtime_status(app);
            }
            "copy_cli" => {
                let _ = copy_cli_command(app);
            }
            "runtime_not_running" => {
                let state = app.state::<Arc<ShellState>>();
                let current = *state.state.lock().unwrap();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = show_state(app, &window, &state, current);
                }
            }
            _ => {}
        })
        .build(tauri::generate_context!())
        .expect("error while building the itembank shell")
        .run(|_app, _event| {});
}

fn banks_dir() -> PathBuf {
    std::env::var_os("ITEMBANK_BANKS_DIR")
        .map(PathBuf::from)
        .or_else(|| std::env::var_os("USERPROFILE").map(PathBuf::from))
        .unwrap_or_else(|| PathBuf::from("."))
}

fn spawn_and_connect(
    app: &AppHandle,
    window: &WebviewWindow,
    app_state: &Arc<ShellState>,
    job: Option<job_object::JobObject>,
    banks_dir: &PathBuf,
) -> tauri::Result<()> {
    show_state(app, window, app_state, liveness::State::Starting)?;
    arm_slow_line(app, window, app_state);

    let handle = match sidecar::spawn(banks_dir) {
        Ok(handle) => handle,
        Err(err) => {
            eprintln!("sidecar spawn failed: {err}");
            *app_state.state.lock().unwrap() = liveness::State::Unreachable;
            return show_state(app, window, app_state, liveness::State::Unreachable);
        }
    };

    {
        let mut pid = app_state.sidecar_pid.lock().unwrap();
        *pid = Some(handle.pid);
        let mut path = app_state.sidecar_path.lock().unwrap();
        *path = Some(
            std::env::current_exe()
                .map(|p| p.display().to_string())
                .unwrap_or_else(|_| "unknown".into()),
        );
    }
    {
        let mut out = app_state.output.lock().unwrap();
        *out = handle.output.lock().unwrap().clone();
    }

    if let Some(job) = job {
        if let Err(err) = job.assign_pid(handle.pid) {
            eprintln!("job-object assignment failed (sidecar not job-bound): {err}");
        }
        // Keep the kill-on-close handle open for the app's lifetime: dropping
        // it would terminate the sidecar immediately (that is the point of
        // JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE -- the handle is released when
        // the shell process dies, not when a Rust scope ends).
        let _ = Box::leak(Box::new(job));
    }

    let hs = match handle.wait_handshake(sidecar::HANDSHAKE_TIMEOUT) {
        Ok(hs) => hs,
        Err(err) => {
            eprintln!("sidecar handshake failed: {err}");
            *app_state.state.lock().unwrap() = liveness::State::Unreachable;
            return show_state(app, window, app_state, liveness::State::Unreachable);
        }
    };

    // Version coherence (13-RESEARCH section 2 item 3): never run mismatched
    // halves; the mismatch takes the honest failure path.
    let shell_version = app.package_info().version.to_string();
    if !liveness::versions_match(&shell_version, &hs.version) {
        eprintln!(
            "version mismatch: shell {shell_version}, sidecar {}",
            hs.version
        );
        *app_state.state.lock().unwrap() = liveness::State::Unreachable;
        return show_state(app, window, app_state, liveness::State::Unreachable);
    }

    {
        *app_state.sidecar_port.lock().unwrap() = Some(hs.port);
        *app_state.token.lock().unwrap() = Some(hs.token.clone());
        *app_state.started_at.lock().unwrap() = Some(now_iso());
    }
    // Test seam (headless lifecycle fixture): report the sidecar pid and
    // port on the shell's own stdout so the fixture can taskkill the shell
    // and assert the job object took the sidecar with it. Never the token
    // (T-13-08): the token stays in the shell's memory and the daemon's.
    if std::env::var_os("ITEMBANK_HEADLESS").is_some() {
        println!("shell-sidecar-pid:{}", handle.pid);
        println!("shell-sidecar-port:{}", hs.port);
    }

    let proxy = proxy::Proxy::start(hs.port, hs.token.clone())?;
    let proxy_port = proxy.port();
    *app_state.proxy_port.lock().unwrap() = Some(proxy_port);
    *app_state.proxy.lock().unwrap() = Some(Arc::clone(&proxy));
    // The proxy Arc keeps the listener alive; leak it for the app lifetime.
    std::mem::forget(proxy);

    // The one-disclosure StatusNotice (13-UI-SPEC 7.2): read the daemon-owned
    // disclosure state and arm the proxy to inject it into the FIRST page
    // load. Showing performs no check -- the daemon's policy gate already
    // ran at its startup, and this launch creates no request of its own.
    arm_disclosure_notice(app_state);

    let daemon_url = Url::parse(&format!("http://127.0.0.1:{proxy_port}/"))
        .map_err(|e| tauri::Error::AssetNotFound(e.to_string().into()))?;
    window.navigate(daemon_url)?;

    *app_state.state.lock().unwrap() = liveness::State::Ready;
    show_state(app, window, app_state, liveness::State::Ready)?;

    watch_sidecar(app, window, app_state, handle.child);
    Ok(())
}

fn watch_sidecar(
    app: &AppHandle,
    window: &WebviewWindow,
    app_state: &Arc<ShellState>,
    mut child: std::process::Child,
) {
    let state = Arc::clone(app_state);
    let window = window.clone();
    let app = app.clone();
    std::thread::spawn(move || {
        let status = child.wait();
        let was_ready = *state.state.lock().unwrap() == liveness::State::Ready;
        if !was_ready {
            return;
        }
        let exit = status
            .ok()
            .and_then(|s| s.code())
            .map(|c| c.to_string())
            .unwrap_or_else(|| "?".into());
        *state.state.lock().unwrap() = liveness::State::Crashed;
        let mut stopped = state.started_at.lock().unwrap().clone();
        if stopped.is_none() {
            stopped = Some(now_iso());
        }
        let output = state
            .output
            .lock()
            .unwrap()
            .iter()
            .rev()
            .take(8)
            .cloned()
            .collect::<Vec<_>>()
            .join("\n");
        let _ = show_state_with(
            &app,
            &window,
            &state,
            liveness::State::Crashed,
            &[
                ("exit", &exit),
                ("stopped", stopped.as_deref().unwrap_or("")),
                ("stdout", &output),
            ],
        );
    });
}

fn arm_slow_line(app: &AppHandle, window: &WebviewWindow, app_state: &Arc<ShellState>) {
    let state = Arc::clone(app_state);
    let window = window.clone();
    let app = app.clone();
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_secs(10));
        let still_starting = *state.state.lock().unwrap() == liveness::State::Starting;
        if still_starting {
            let _ = show_state_with(&app, &window, &state, liveness::State::Starting, &[("slow", "1")]);
        }
    });
}

fn show_state(
    app: &AppHandle,
    window: &WebviewWindow,
    app_state: &Arc<ShellState>,
    state: liveness::State,
) -> tauri::Result<()> {
    show_state_with(app, window, app_state, state, &[])
}

fn show_state_with(
    app: &AppHandle,
    window: &WebviewWindow,
    app_state: &Arc<ShellState>,
    state: liveness::State,
    extra: &[(&str, &str)],
) -> tauri::Result<()> {
    window.set_title(state.window_title())?;
    set_menu_for_state(app, state)?;
    if state == liveness::State::Ready {
        return Ok(());
    }
    let mut query = format!("state={}", state.doc_state());
    for (key, value) in extra {
        if !value.is_empty() {
            query.push('&');
            query.push_str(key);
            query.push('=');
            query.push_str(&urlencode(value));
        }
    }
    if let Some(sidecar) = app_state.sidecar_path.lock().unwrap().clone() {
        query.push_str(&format!("&sidecar={}", urlencode(&sidecar)));
    }
    if let Some(log) = app_state.log_path.lock().unwrap().clone() {
        query.push_str(&format!("&log={}", urlencode(&log)));
    }
    let url = Url::parse(&format!("tauri://localhost/runtime-not-ready.html?{query}"))
        .map_err(|e| tauri::Error::AssetNotFound(e.to_string().into()))?;
    window.navigate(url)?;
    Ok(())
}

fn set_menu_for_state(app: &AppHandle, state: liveness::State) -> tauri::Result<()> {
    if state == liveness::State::Ready {
        let status = MenuItem::with_id(app, "runtime_status", "Runtime status", true, Some("Ctrl+Shift+S"))?;
        let copy = MenuItem::with_id(
            app,
            "copy_cli",
            "Copy the CLI command for this view",
            true,
            Some("Ctrl+Shift+C"),
        )?;
        let sub = Submenu::with_items(app, "itembank", true, &[&status, &copy])?;
        app.set_menu(Menu::with_items(app, &[&sub])?)?;
    } else {
        let details = MenuItem::with_id(
            app,
            "runtime_not_running",
            "Runtime is not running \u{2014} show details",
            true,
            None::<&str>,
        )?;
        let sub = Submenu::with_items(app, "itembank", true, &[&details])?;
        app.set_menu(Menu::with_items(app, &[&sub])?)?;
    }
    Ok(())
}

fn open_runtime_status(app: &AppHandle) -> tauri::Result<()> {
    let state = app.state::<Arc<ShellState>>();
    let port = state
        .sidecar_port
        .lock()
        .unwrap()
        .map(|p| p.to_string())
        .unwrap_or_default();
    let pid = state
        .sidecar_pid
        .lock()
        .unwrap()
        .map(|p| p.to_string())
        .unwrap_or_default();
    let started = state.started_at.lock().unwrap().clone().unwrap_or_default();
    let version = app.package_info().version.to_string();
    let log = state.log_path.lock().unwrap().clone().unwrap_or_default();
    let query = format!(
        "port={}&pid={}&started={}&version={}&log={}",
        urlencode(&port),
        urlencode(&pid),
        urlencode(&started),
        urlencode(&version),
        urlencode(&log)
    );
    let url = Url::parse(&format!("tauri://localhost/runtime-status.html?{query}"))
        .map_err(|e| tauri::Error::AssetNotFound(e.to_string().into()))?;
    tauri::WebviewWindowBuilder::new(app, "runtime-status", WebviewUrl::External(url))
        .title("Runtime status")
        .inner_size(480.0, 360.0)
        .build()?;
    Ok(())
}

fn copy_cli_command(app: &AppHandle) -> tauri::Result<()> {
    let state = app.state::<Arc<ShellState>>();
    let Some(proxy_port) = *state.proxy_port.lock().unwrap() else {
        return Ok(());
    };
    let path = state
        .proxy
        .lock()
        .unwrap()
        .as_ref()
        .map(|p| p.last_path())
        .unwrap_or_else(|| "/".to_string());
    let body = serde_json::json!({ "path": path }).to_string();
    let (status, text) =
        proxy::proxy_request(proxy_port, "POST", "/api/cli-twin", body.as_bytes())
            .unwrap_or((0, String::new()));
    if status == 200 {
        if let Some(command) = serde_json::from_str::<serde_json::Value>(&text)
            .ok()
            .and_then(|v| v.get("command").and_then(|c| c.as_str()).map(String::from))
        {
            app.clipboard()
                .write_text(command)
                .map_err(|e| std::io::Error::other(e.to_string()))?;
        }
    }
    Ok(())
}

#[tauri::command]
fn restart_runtime(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let state = app.state::<Arc<ShellState>>();
        let banks = banks_dir();
        let job = job_object::JobObject::create().ok();
        let _ = spawn_and_connect(&app, &window, &state, job, &banks);
    }
}

#[tauri::command]
fn focus_running_instance(app: AppHandle) {
    let _ = focus_existing_window();
    let _ = app;
}

struct FocusCtx {
    own_pid: u32,
    found: bool,
}

unsafe extern "system" fn enum_proc(hwnd: HWND, lparam: isize) -> BOOL {
    let ctx = &mut *(lparam as *mut FocusCtx);
    if IsWindowVisible(hwnd) == 0 {
        return 1;
    }
    let mut pid: u32 = 0;
    GetWindowThreadProcessId(hwnd, &mut pid);
    if pid == ctx.own_pid {
        return 1;
    }
    let mut buf = [0u16; 256];
    let len = GetWindowTextW(hwnd, buf.as_mut_ptr(), buf.len() as i32);
    let title = String::from_utf16_lossy(&buf[..len.max(0) as usize]);
    if title.starts_with("itembank") {
        SetForegroundWindow(hwnd);
        ctx.found = true;
        return 0;
    }
    1
}

fn focus_existing_window() -> bool {
    let mut ctx = FocusCtx {
        own_pid: std::process::id(),
        found: false,
    };
    unsafe {
        EnumWindows(Some(enum_proc), &mut ctx as *mut FocusCtx as isize);
    }
    ctx.found
}

fn urlencode(s: &str) -> String {
    let mut out = String::new();
    for b in s.bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(b as char)
            }
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}


fn html_escape(s: &str) -> String {
    let mut out = String::new();
    for ch in s.chars() {
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            _ => out.push(ch),
        }
    }
    out
}

fn arm_disclosure_notice(app_state: &Arc<ShellState>) {
    let Some(proxy_port) = *app_state.proxy_port.lock().unwrap() else {
        return;
    };
    let (status, text) =
        proxy::proxy_request(proxy_port, "GET", "/disclosure", b"")
            .unwrap_or((0, String::new()));
    if status != 200 {
        return;
    }
    let Ok(value) = serde_json::from_str::<serde_json::Value>(&text) else {
        return;
    };
    if value.get("show").and_then(|s| s.as_bool()) != Some(true) {
        return;
    }
    let copy = value
        .get("copy")
        .and_then(|c| c.as_str())
        .unwrap_or_default();
    let settings_path = value
        .get("settings_path")
        .and_then(|p| p.as_str())
        .unwrap_or_default();
    let notice = format!(
        "<div id=\"itembank-update-disclosure\" role=\"status\" \
         style=\"border:1px solid var(--line);border-radius:8px;padding:12px 16px;\
         margin:16px 0;background:var(--card);\">\
         <p style=\"margin:0 0 8px;\">{copy}</p>\
         <p style=\"margin:0 0 8px;\">Your settings file is at \
         <span style=\"font-family:var(--font-ledger,ui-monospace,Consolas,monospace);\
         font-size:12px;\">{settings_path}</span>.</p>\
         <button type=\"button\" onclick=\"this.parentElement.remove()\" \
         style=\"min-height:44px;padding:0 20px;border-radius:8px;\
         border:1px solid var(--line);background:var(--accent);color:var(--card);\
         font:inherit;font-weight:600;\">Got it</button></div>",
        copy = html_escape(copy),
        settings_path = html_escape(settings_path)
    );
    if let Some(proxy) = app_state.proxy.lock().unwrap().as_ref() {
        proxy.inject_notice(&notice);
    }
}

fn now_iso() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs() as i64;
    let days = secs.div_euclid(86400);
    let rem = secs.rem_euclid(86400);
    let (hour, min, sec) = (rem / 3600, (rem % 3600) / 60, rem % 60);
    let (year, month, day) = civil_from_days(days);
    format!("{year:04}-{month:02}-{day:02}T{hour:02}:{min:02}:{sec:02}Z")
}

fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = (z - era * 146_097) as u64;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe as i64 + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn urlencode_keeps_query_safe() {
        assert_eq!(urlencode("a b&c=d"), "a%20b%26c%3Dd");
        assert_eq!(urlencode("plain"), "plain");
    }

    #[test]
    fn iso_timestamp_is_well_formed() {
        let s = now_iso();
        assert_eq!(s.len(), 20);
        assert!(s.ends_with('Z'));
        assert!(s.starts_with("20"));
    }
}
