"""Own a Windows build process tree, including children left after the launcher exits."""
import ctypes
from ctypes import wintypes
import os
import subprocess
import threading

from processes import hidden_options


class ProcessTree:
    def __init__(self):
        self.lock = threading.RLock()
        self.handle = None
        self.assigned = False
        if os.name != 'nt':
            return
        class Limits(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64),
                        ('flags', wintypes.DWORD), ('minimum', ctypes.c_size_t), ('maximum', ctypes.c_size_t),
                        ('active', wintypes.DWORD), ('affinity', ctypes.c_size_t),
                        ('priority', wintypes.DWORD), ('scheduling', wintypes.DWORD)]
        class Counters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ('read_ops', 'write_ops', 'other_ops',
                                                          'read_bytes', 'write_bytes', 'other_bytes')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Limits), ('io', Counters), ('process_memory', ctypes.c_size_t),
                        ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t),
                        ('peak_job', ctypes.c_size_t)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.SetInformationJobObject.restype = wintypes.BOOL
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        self.kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.TerminateJobObject.restype = wintypes.BOOL
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if self.handle:
            limits = Extended()
            limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
                self.close()

    def assign(self, process):
        with self.lock:
            if self.handle:
                self.assigned = bool(self.kernel.AssignProcessToJobObject(self.handle, int(process._handle)))
            return self.assigned

    def stop(self, process):
        with self.lock:
            if self.handle and self.assigned and self.kernel.TerminateJobObject(self.handle, 130):
                return
            if process and process.poll() is None:
                if os.name == 'nt':
                    executable = os.path.join(os.environ.get('SystemRoot', 'C:/Windows'), 'System32/taskkill.exe')
                    subprocess.run([executable, '/PID', str(process.pid), '/T', '/F'], check=False,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **hidden_options())
                if process.poll() is None:
                    process.kill()

    def close(self):
        with self.lock:
            if self.handle:
                self.kernel.CloseHandle(self.handle)
                self.handle = None
