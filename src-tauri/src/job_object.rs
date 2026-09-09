//! The Windows job-object backstop (D-05, 13-RESEARCH section 1).
//!
//! The shell keeps one `JobObject` with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`
//! for its whole lifetime and assigns the sidecar process to it right after
//! spawn. When the shell dies by any means (including TerminateProcess from
//! Task Manager, where graceful shutdown handlers never run) the OS closes
//! the job's last handle and terminates every assigned process -- no orphaned
//! sidecar, no held port.

use std::io;
#[cfg(target_os = "windows")]
use windows_sys::Win32::Foundation::CloseHandle;
#[cfg(target_os = "windows")]
use windows_sys::Win32::System::JobObjects::{
    AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
    SetInformationJobObject, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
};
#[cfg(target_os = "windows")]
use windows_sys::Win32::System::Threading::{OpenProcess, PROCESS_SET_QUOTA, PROCESS_TERMINATE};

pub struct JobObject {
    #[cfg(target_os = "windows")]
    handle: windows_sys::Win32::Foundation::HANDLE,
}

// The handle is process-owned and only ever used from the owning thread; the
// wrapper is stored for the app's lifetime.
#[cfg(target_os = "windows")]
unsafe impl Send for JobObject {}

impl JobObject {
    pub fn create() -> io::Result<JobObject> {
        #[cfg(target_os = "windows")]
        unsafe {
            let handle = CreateJobObjectW(std::ptr::null(), std::ptr::null());
            if handle.is_null() {
                return Err(io::Error::last_os_error());
            }
            let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            let ok = SetInformationJobObject(
                handle,
                JobObjectExtendedLimitInformation,
                &info as *const _ as *const std::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            );
            if ok == 0 {
                let err = io::Error::last_os_error();
                CloseHandle(handle);
                return Err(err);
            }
            Ok(JobObject { handle })
        }
        #[cfg(not(target_os = "windows"))]
        Err(io::Error::new(
            io::ErrorKind::Unsupported,
            "Windows job objects are unavailable on this platform",
        ))
    }

    /// Assign a running child process to this job. Best-effort backstop: a
    /// child that is already in another job (ERROR_ACCESS_DENIED) is
    /// reported so the shell can log the degraded state rather than pretend
    /// the backstop exists.
    pub fn assign_pid(&self, pid: u32) -> io::Result<()> {
        #[cfg(target_os = "windows")]
        unsafe {
            let proc_handle = OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, 0, pid);
            if proc_handle.is_null() {
                return Err(io::Error::last_os_error());
            }
            let ok = AssignProcessToJobObject(self.handle, proc_handle);
            let err = io::Error::last_os_error();
            CloseHandle(proc_handle);
            if ok == 0 {
                Err(err)
            } else {
                Ok(())
            }
        }
        #[cfg(not(target_os = "windows"))]
        {
            let _ = (self, pid);
            Err(io::Error::new(
                io::ErrorKind::Unsupported,
                "Windows job objects are unavailable on this platform",
            ))
        }
    }
}

#[cfg(target_os = "windows")]
impl Drop for JobObject {
    fn drop(&mut self) {
        unsafe {
            CloseHandle(self.handle);
        }
    }
}

#[cfg(all(test, target_os = "windows"))]
mod tests {
    use super::*;
    use std::process::Command;
    use std::time::{Duration, Instant};

    #[test]
    fn kill_on_close_terminates_an_assigned_child() {
        let job = match JobObject::create() {
            Ok(job) => job,
            Err(err) => {
                eprintln!("skip: could not create a job object ({err})");
                return;
            }
        };
        let mut child = match Command::new("python")
            .args(["-c", "import time; time.sleep(60)"])
            .spawn()
        {
            Ok(child) => child,
            Err(err) => {
                eprintln!("skip: could not spawn a sleeper ({err})");
                return;
            }
        };
        if let Err(err) = job.assign_pid(child.id()) {
            if err.raw_os_error() == Some(5) {
                // ERROR_ACCESS_DENIED: the child is already in a job; the
                // backstop cannot apply here -- not a KILL_ON_JOB_CLOSE failure.
                let _ = child.kill();
                eprintln!("skip: child already in a job (access denied)");
                return;
            }
            let _ = child.kill();
            panic!("assign child to job failed: {err}");
        }
        drop(job); // closing the last handle must terminate the child
        let deadline = Instant::now() + Duration::from_secs(10);
        loop {
            match child.try_wait() {
                Ok(Some(_)) => break,
                Ok(None) => {
                    if Instant::now() > deadline {
                        let _ = child.kill();
                        panic!("child survived job close; KILL_ON_JOB_CLOSE failed");
                    }
                    std::thread::sleep(Duration::from_millis(50));
                }
                Err(err) => {
                    let _ = child.kill();
                    panic!("try_wait failed: {err}");
                }
            }
        }
    }
}
