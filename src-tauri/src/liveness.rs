//! The five liveness states (13-UI-SPEC 3.3) and the version-coherence rule.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Starting,
    Ready,
    Unreachable,
    Crashed,
    PortHeldAttach,
    PortHeldRefused,
}

impl State {
    /// 13-UI-SPEC 2.1: `itembank` when ready; `itembank — runtime not
    /// running` in the unreachable/crashed/port-held states.
    pub fn window_title(self) -> &'static str {
        match self {
            State::Ready => "itembank",
            _ => "itembank \u{2014} runtime not running",
        }
    }

    /// The data-state value the shell-local document selects (3.3).
    pub fn doc_state(self) -> &'static str {
        match self {
            State::Starting => "starting",
            State::Ready => "ready",
            State::Unreachable => "unreachable",
            State::Crashed => "crashed",
            State::PortHeldAttach => "port-held",
            State::PortHeldRefused => "port-held-refused",
        }
    }
}

/// Version coherence (13-RESEARCH section 2, item 3): a handshake version
/// that does not equal the shell's own version must never run mismatched
/// halves -- the shell takes the crashed/unreachable path instead.
pub fn versions_match(shell: &str, sidecar: &str) -> bool {
    shell.trim() == sidecar.trim()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ready_title_is_plain_itembank() {
        assert_eq!(State::Ready.window_title(), "itembank");
    }

    #[test]
    fn every_non_ready_state_announces_the_runtime_is_down() {
        for state in [
            State::Starting,
            State::Unreachable,
            State::Crashed,
            State::PortHeldAttach,
            State::PortHeldRefused,
        ] {
            assert_eq!(state.window_title(), "itembank \u{2014} runtime not running");
        }
    }

    #[test]
    fn doc_state_matches_the_spec_sections() {
        assert_eq!(State::Starting.doc_state(), "starting");
        assert_eq!(State::Ready.doc_state(), "ready");
        assert_eq!(State::Unreachable.doc_state(), "unreachable");
        assert_eq!(State::Crashed.doc_state(), "crashed");
        assert_eq!(State::PortHeldAttach.doc_state(), "port-held");
        assert_eq!(State::PortHeldRefused.doc_state(), "port-held-refused");
    }

    #[test]
    fn version_match_and_mismatch() {
        assert!(versions_match("0.3.0", "0.3.0"));
        assert!(!versions_match("0.3.0", "0.3.1"));
        assert!(!versions_match("0.3.0", ""));
    }
}
