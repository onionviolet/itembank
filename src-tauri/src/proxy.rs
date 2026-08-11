//! The loopback HTTP proxy (D-02 plumbing, not a second protocol).
//!
//! The WebView talks to the shell's own loopback port; the proxy forwards
//! every request to the sidecar's daemon, adding the per-launch token header
//! and stripping `Origin` and hop-by-hop headers. One HTTP transport end to
//! end -- the token gate stays the daemon's own, and the shell holds no
//! route knowledge (the daemon owns the routes).

use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::sync::{Arc, Mutex};
use std::thread;

const MAX_HEAD: usize = 64 * 1024;

pub struct Proxy {
    port: u16,
    target: SocketAddr,
    token: String,
    last_path: Arc<Mutex<String>>,
    notice: Arc<Mutex<Option<String>>>,
}

impl Proxy {
    /// Bind a loopback listener and start the forward loop on a background
    /// thread. The returned `Arc` keeps the proxy alive.
    pub fn start(target_port: u16, token: String) -> std::io::Result<Arc<Proxy>> {
        let listener = TcpListener::bind(("127.0.0.1", 0))?;
        let port = listener.local_addr()?.port();
        let target = SocketAddr::from(([127, 0, 0, 1], target_port));
        let proxy = Arc::new(Proxy {
            port,
            target,
            token,
            last_path: Arc::new(Mutex::new("/".to_string())),
            notice: Arc::new(Mutex::new(None)),
        });
        let shared = Arc::clone(&proxy);
        thread::spawn(move || {
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        let proxy = Arc::clone(&shared);
                        let last_path = Arc::clone(&shared.last_path);
                        let notice = Arc::clone(&shared.notice);
                        thread::spawn(move || {
                            let _ = handle_connection(
                                stream, proxy.target, &proxy.token, &last_path, &notice);
                        });
                    }
                    Err(_) => break,
                }
            }
        });
        Ok(proxy)
    }

    pub fn port(&self) -> u16 {
        self.port
    }

    /// The last path the window requested -- the shell's view pointer for
    /// the CLI-twin menu item (the daemon still owns the mapping).
    pub fn last_path(&self) -> String {
        self.last_path.lock().unwrap().clone()
    }

    /// Inject a StatusNotice into the next HTML response the proxy serves,
    /// exactly once (the one-disclosure render-once rule, 13-UI-SPEC 7.2).
    pub fn inject_notice(&self, html: &str) {
        *self.notice.lock().unwrap() = Some(html.to_string());
    }
}

/// Issue a request through a running proxy (used by the shell's own menu
/// calls, e.g. the CLI-twin query). Returns `(status, body_text)`.
pub fn proxy_request(
    proxy_port: u16,
    method: &str,
    path: &str,
    body: &[u8],
) -> std::io::Result<(u16, String)> {
    let mut stream = TcpStream::connect(("127.0.0.1", proxy_port))?;
    write!(
        stream,
        "{} {} HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        method,
        path,
        body.len()
    )?;
    stream.write_all(body)?;
    let (status_line, _headers, body) = read_response(&mut stream)?;
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|code| code.parse::<u16>().ok())
        .unwrap_or(0);
    Ok((status, body))
}

fn handle_connection(
    mut client: TcpStream,
    target: SocketAddr,
    token: &str,
    last_path: &Arc<Mutex<String>>,
    notice: &Arc<Mutex<Option<String>>>,
) {
    let head = match read_head(&mut client) {
        Ok(head) => head,
        Err(_) => return,
    };
    let (request_line, headers, body) = match parse_request(&head, &mut client) {
        Ok(parsed) => parsed,
        Err(_) => return,
    };
    let path = request_line.split_whitespace().nth(1).unwrap_or("/").to_string();
    *last_path.lock().unwrap() = path;

    let mut out: Vec<u8> = Vec::with_capacity(1024);
    out.extend_from_slice(request_line.as_bytes());
    out.extend_from_slice(b"\r\n");
    for (name, value) in &headers {
        let lower = name.to_ascii_lowercase();
        if matches!(
            lower.as_str(),
            "host"
                | "origin"
                | "connection"
                | "keep-alive"
                | "proxy-connection"
                | "transfer-encoding"
                | "upgrade"
                | "te"
        ) {
            continue;
        }
        out.extend_from_slice(format!("{}: {}\r\n", name, value).as_bytes());
    }
    out.extend_from_slice(format!("Host: {}\r\n", target).as_bytes());
    out.extend_from_slice(format!("X-Itembank-Token: {}\r\n", token).as_bytes());
    out.extend_from_slice(format!("Content-Length: {}\r\n", body.len()).as_bytes());
    out.extend_from_slice(b"Connection: close\r\n\r\n");
    out.extend_from_slice(&body);

    if let Ok(mut upstream) = TcpStream::connect(target) {
        if upstream.write_all(&out).is_err() {
            return;
        }
        if let Ok((status_line, headers, resp_body)) = read_response(&mut upstream) {
            let is_html = headers.iter().any(|(name, value)| {
                name.eq_ignore_ascii_case("content-type")
                    && value.to_ascii_lowercase().contains("html")
            });
            let mut body = resp_body;
            if is_html {
                if let Some(n) = notice.lock().unwrap().take() {
                    if let Some(idx) = body.rfind("</body>") {
                        let mut injected = body[..idx].to_string();
                        injected.push_str(&n);
                        injected.push_str(&body[idx..]);
                        body = injected;
                    }
                }
            }
            let mut reply: Vec<u8> = Vec::with_capacity(1024);
            reply.extend_from_slice(status_line.as_bytes());
            for (name, value) in &headers {
                let lower = name.to_ascii_lowercase();
                if lower == "connection" || lower == "keep-alive" {
                    continue;
                }
                if lower == "content-length" {
                    reply.extend_from_slice(
                        format!("{}: {}\r\n", name, body.len()).as_bytes());
                    continue;
                }
                reply.extend_from_slice(format!("{}: {}\r\n", name, value).as_bytes());
            }
            reply.extend_from_slice(b"Connection: close\r\n\r\n");
            reply.extend_from_slice(body.as_bytes());
            let _ = client.write_all(&reply);
            let _ = client.flush();
        }
    }
}

fn read_head(stream: &mut TcpStream) -> std::io::Result<Vec<u8>> {
    let mut buf = Vec::with_capacity(4096);
    let mut tmp = [0u8; 4096];
    loop {
        let n = stream.read(&mut tmp)?;
        if n == 0 {
            break;
        }
        buf.extend_from_slice(&tmp[..n]);
        if buf.windows(4).any(|w| w == b"\r\n\r\n") {
            break;
        }
        if buf.len() > MAX_HEAD {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "request head too large",
            ));
        }
    }
    Ok(buf)
}

fn parse_request(
    head: &[u8],
    stream: &mut TcpStream,
) -> std::io::Result<(String, Vec<(String, String)>, Vec<u8>)> {
    let text = String::from_utf8_lossy(head);
    let (head_text, rest) = match text.find("\r\n\r\n") {
        Some(idx) => (&text[..idx], &head[idx + 4..]),
        None => return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, "no head")),
    };
    let mut lines = head_text.split("\r\n");
    let request_line = lines.next().unwrap_or("").to_string();
    let mut headers = Vec::new();
    let mut content_length = 0usize;
    for line in lines {
        if let Some((name, value)) = line.split_once(':') {
            headers.push((name.trim().to_string(), value.trim().to_string()));
            if name.eq_ignore_ascii_case("content-length") {
                content_length = value.trim().parse().unwrap_or(0);
            }
        }
    }
    let mut body = rest.to_vec();
    if body.len() < content_length {
        let mut tmp = vec![0u8; content_length - body.len()];
        stream.read_exact(&mut tmp)?;
        body.extend_from_slice(&tmp);
    }
    Ok((request_line, headers, body))
}

fn read_response(stream: &mut TcpStream) -> std::io::Result<(String, Vec<(String, String)>, String)> {
    let head = read_head(stream)?;
    let text = String::from_utf8_lossy(&head);
    let (head_text, rest) = match text.find("\r\n\r\n") {
        Some(idx) => (&text[..idx], &head[idx + 4..]),
        None => return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, "no response head")),
    };
    let mut lines = head_text.split("\r\n");
    let status_line = lines.next().unwrap_or("").to_string();
    let mut headers = Vec::new();
    let mut content_length: Option<usize> = None;
    let mut chunked = false;
    for line in lines {
        if let Some((name, value)) = line.split_once(':') {
            headers.push((name.trim().to_string(), value.trim().to_string()));
            if name.eq_ignore_ascii_case("content-length") {
                content_length = value.trim().parse().ok();
            }
            if name.eq_ignore_ascii_case("transfer-encoding")
                && value.to_ascii_lowercase().contains("chunked")
            {
                chunked = true;
            }
        }
    }
    let mut body = rest.to_vec();
    if chunked {
        // Read the chunked body from the (already partially read) stream.
        let mut rest_buf = Vec::new();
        let mut tmp = [0u8; 4096];
        loop {
            match stream.read(&mut tmp) {
                Ok(0) => break,
                Ok(n) => rest_buf.extend_from_slice(&tmp[..n]),
                Err(_) => break,
            }
        }
        body.extend_from_slice(&rest_buf);
    } else if let Some(len) = content_length {
        if body.len() < len {
            let mut tmp = vec![0u8; len - body.len()];
            let _ = stream.read_exact(&mut tmp);
            body.extend_from_slice(&tmp);
        }
    } else {
        let mut tmp = [0u8; 4096];
        loop {
            match stream.read(&mut tmp) {
                Ok(0) => break,
                Ok(n) => body.extend_from_slice(&tmp[..n]),
                Err(_) => break,
            }
        }
    }
    Ok((status_line, headers, String::from_utf8_lossy(&body).into_owned()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::sync::mpsc;
    use std::time::Duration;

    fn capture_server() -> (u16, mpsc::Receiver<String>) {
        let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let (tx, rx) = mpsc::channel();
        thread::spawn(move || {
            if let Ok(mut stream) = listener.accept().map(|(s, _)| s) {
                let mut buf = Vec::new();
                let mut tmp = [0u8; 1024];
                loop {
                    match stream.read(&mut tmp) {
                        Ok(0) => break,
                        Ok(n) => {
                            buf.extend_from_slice(&tmp[..n]);
                            if buf.windows(4).any(|w| w == b"\r\n\r\n") {
                                break;
                            }
                        }
                        Err(_) => break,
                    }
                }
                let _ = tx.send(String::from_utf8_lossy(&buf).to_string());
                let _ = stream.write_all(b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok");
                let _ = stream.flush();
            }
        });
        (port, rx)
    }

    fn html_capture_server() -> (u16, mpsc::Receiver<String>) {
        let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let (tx, rx) = mpsc::channel();
        thread::spawn(move || {
            if let Ok(mut stream) = listener.accept().map(|(s, _)| s) {
                let mut buf = Vec::new();
                let mut tmp = [0u8; 1024];
                loop {
                    match stream.read(&mut tmp) {
                        Ok(0) => break,
                        Ok(n) => {
                            buf.extend_from_slice(&tmp[..n]);
                            if buf.windows(4).any(|w| w == b"\r\n\r\n") {
                                break;
                            }
                        }
                        Err(_) => break,
                    }
                }
                let _ = tx.send(String::from_utf8_lossy(&buf).to_string());
                let body = b"<html><body>ok</body></html>";
                let _ = stream.write_all(
                    format!("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n", body.len()).as_bytes());
                let _ = stream.write_all(body);
                let _ = stream.flush();
            }
        });
        (port, rx)
    }

    #[test]
    fn forwards_with_token_and_strips_origin() {
        let (cap_port, rx) = capture_server();
        let proxy = Proxy::start(cap_port, "sekrit-token".into()).unwrap();
        let mut stream = TcpStream::connect(("127.0.0.1", proxy.port())).unwrap();
        stream
            .write_all(
                b"POST /api/start HTTP/1.1\r\n\
                  Host: itembank\r\n\
                  Origin: http://itembank\r\n\
                  Content-Length: 5\r\n\r\nhello",
            )
            .unwrap();
        let mut resp = String::new();
        stream.read_to_string(&mut resp).unwrap();
        assert!(resp.contains("200 OK"), "response: {resp}");
        assert!(resp.contains("ok"), "response: {resp}");
        let captured = rx.recv_timeout(Duration::from_secs(5)).expect("capture");
        assert!(
            captured.contains("X-Itembank-Token: sekrit-token"),
            "captured: {captured}"
        );
        assert!(!captured.contains("Origin:"), "captured: {captured}");
        assert!(
            captured.contains(&format!("Host: 127.0.0.1:{cap_port}")),
            "captured: {captured}"
        );
        assert!(captured.starts_with("POST /api/start"), "captured: {captured}");
    }

    #[test]
    fn proxy_request_round_trips() {
        let (cap_port, rx) = capture_server();
        let proxy = Proxy::start(cap_port, "t".into()).unwrap();
        let (status, body) = proxy_request(proxy.port(), "POST", "/x", b"data").unwrap();
        assert_eq!(status, 200);
        assert_eq!(body, "ok");
        let captured = rx.recv_timeout(Duration::from_secs(5)).expect("capture");
        assert!(captured.contains("Content-Length: 4"));
    }

    #[test]
    fn status_notice_injects_once_into_html() {
        let (cap_port, _rx) = html_capture_server();
        let proxy = Proxy::start(cap_port, "t".into()).unwrap();
        proxy.inject_notice("<p id=\"notice\">disclosure</p>");

        let mut stream = TcpStream::connect(("127.0.0.1", proxy.port())).unwrap();
        stream
            .write_all(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
            .unwrap();
        let mut resp = String::new();
        stream.read_to_string(&mut resp).unwrap();
        assert!(resp.contains("disclosure"), "first response: {resp}");
        assert!(resp.contains("</body>"), "injection point kept: {resp}");

        let mut stream2 = TcpStream::connect(("127.0.0.1", proxy.port())).unwrap();
        stream2.write_all(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n").unwrap();
        let mut resp2 = String::new();
        stream2.read_to_string(&mut resp2).unwrap();
        assert!(!resp2.contains("disclosure"), "second response re-injected: {resp2}");
    }
}
