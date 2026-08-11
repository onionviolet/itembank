//! The sidecar stdout handshake parser (plan 13-01 framing constants).
//!
//! The constants mirror `surfaces/daemon.py`'s `SIDECAR_HANDSHAKE`; a framing
//! change is one edit per side, never a silent second protocol (T-13-02).

pub const PORT_PREFIX: &str = "itembank-port:";
pub const TOKEN_PREFIX: &str = "itembank-token:";
pub const VERSION_PREFIX: &str = "itembank-version:";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Handshake {
    pub port: u16,
    pub token: String,
    pub version: String,
}

/// Parse the three handshake lines from raw sidecar stdout. Extra lines are
/// ignored; a missing, empty, or malformed field fails the whole parse --
/// never a silent fallback (T-13-02).
pub fn parse(stdout: &str) -> Option<Handshake> {
    let mut port = None;
    let mut token = None;
    let mut version = None;
    for line in stdout.lines() {
        let line = line.trim_end_matches('\r');
        if let Some(v) = line.strip_prefix(PORT_PREFIX) {
            port = v.trim().parse::<u16>().ok();
        } else if let Some(v) = line.strip_prefix(TOKEN_PREFIX) {
            token = Some(v.trim().to_string());
        } else if let Some(v) = line.strip_prefix(VERSION_PREFIX) {
            version = Some(v.trim().to_string());
        }
    }
    match (port, token, version) {
        (Some(port), Some(token), Some(version))
            if !token.is_empty() && !version.is_empty() =>
        {
            Some(Handshake {
                port,
                token,
                version,
            })
        }
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_the_three_lines() {
        let hs = parse(
            "itembank-port:53114\n\
             itembank-token:abcdef0123456789abcdef0123456789\n\
             itembank-version:0.3.0\n",
        )
        .expect("handshake");
        assert_eq!(hs.port, 53114);
        assert_eq!(hs.token, "abcdef0123456789abcdef0123456789");
        assert_eq!(hs.version, "0.3.0");
    }

    #[test]
    fn ignores_other_lines_and_is_order_independent() {
        let hs = parse(
            "some banner line\n\
             itembank-version:0.3.0\n\
             itembank-port:1\n\
             itembank-token:tok\n",
        )
        .expect("handshake");
        assert_eq!(
            hs,
            Handshake {
                port: 1,
                token: "tok".into(),
                version: "0.3.0".into()
            }
        );
    }

    #[test]
    fn missing_field_fails() {
        assert!(parse("itembank-port:1\nitembank-token:tok\n").is_none());
    }

    #[test]
    fn malformed_port_fails() {
        assert!(
            parse("itembank-port:notaport\nitembank-token:tok\nitembank-version:0.3.0\n")
                .is_none()
        );
    }

    #[test]
    fn empty_values_fail() {
        assert!(
            parse("itembank-port:1\nitembank-token:\nitembank-version:0.3.0\n").is_none()
        );
    }

    #[test]
    fn crlf_tolerated() {
        assert!(
            parse("itembank-port:2\r\nitembank-token:t\r\nitembank-version:v\r\n").is_some()
        );
    }
}
