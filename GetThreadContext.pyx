# cython: language_level=3

cimport cython
from libc.stdio cimport printf
from libc.stdint cimport uintptr_t

cdef extern from "Windows.h":
    ctypedef unsigned long DWORD
    ctypedef int BOOL
    ctypedef void* HANDLE

    ctypedef struct CONTEXT:
        DWORD ContextFlags
        uintptr_t Rip  # Instruction Pointer
        uintptr_t Rsp  # Stack Pointer
        uintptr_t Rax  # Accumulator

    BOOL GetThreadContext(HANDLE hThread, CONTEXT* lpContext)
    HANDLE OpenThread(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwThreadId)
    void CloseHandle(HANDLE hObject)
    DWORD GetCurrentThreadId()

    DWORD THREAD_QUERY_INFORMATION = 0x0040
    DWORD THREAD_GET_CONTEXT = 0x0008
    DWORD CONTEXT_FULL = 0x00100000 | 0x00000002 | 0x00000004  # Update this based on the desired registers

def get_thread_context(DWORD thread_id):
    cdef HANDLE hThread = OpenThread(THREAD_QUERY_INFORMATION | THREAD_GET_CONTEXT, False, thread_id)
    if not hThread:
        return {"Error": "Failed to open thread."}

    cdef CONTEXT context = {}
    context.ContextFlags = CONTEXT_FULL

    try:
        if GetThreadContext(hThread, &context):
            return {
                "Rip": context.Rip,
                "Rsp": context.Rsp,
                "Rax": context.Rax
            }
        else:
            return {"Error": "Failed to get context for thread."}
    finally:
        CloseHandle(hThread)
