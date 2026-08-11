//! Named-mutex single instance (D-06). The CLI path never touches this
//! mutex; it exists only so two shell processes cannot race.

use windows_sys::Win32::Foundation::{CloseHandle, ERROR_ALREADY_EXISTS};
use windows_sys::Win32::System::Threading::CreateMutexW;

/// `Local\` scopes the mutex to the logon session; a per-user name keeps
/// distinct accounts from blocking each other.
pub const MUTEX_NAME: &str = "Local\\itembank-single-instance";

pub struct SingleInstance {
    handle: windows_sys::Win32::Foundation::HANDLE,
}

unsafe impl Send for SingleInstance {}

impl SingleInstance {
    /// `Some` when this process now owns the mutex; `None` when another
    /// instance already holds it (or creation failed -- the caller refuses
    /// rather than racing).
    pub fn acquire() -> Option<SingleInstance> {
        unsafe {
            let wide: Vec<u16> = MUTEX_NAME.encode_utf16().chain(std::iter::once(0)).collect();
            let handle = CreateMutexW(std::ptr::null(), 0, wide.as_ptr());
            if handle.is_null() {
                return None;
            }
            if io_last_error() == ERROR_ALREADY_EXISTS {
                CloseHandle(handle);
                return None;
            }
            Some(SingleInstance { handle })
        }
    }
}

fn io_last_error() -> u32 {
    std::io::Error::last_os_error()
        .raw_os_error()
        .map(|c| c as u32)
        .unwrap_or(0)
}

impl Drop for SingleInstance {
    fn drop(&mut self) {
        unsafe {
            CloseHandle(self.handle);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn second_acquire_fails_while_first_is_held() {
        let first = match SingleInstance::acquire() {
            Some(instance) => instance,
            None => {
                eprintln!("skip: another itembank process holds the mutex");
                return;
            }
        };
        let second = SingleInstance::acquire();
        assert!(second.is_none(), "second acquire must fail while held");
        drop(first);
        let third = SingleInstance::acquire();
        assert!(third.is_some(), "after release the mutex is acquirable again");
    }
}
