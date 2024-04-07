import ctypes
from ctypes import wintypes
import csv
import sys
import psutil  # 导入psutil库

# 定义所需的结构体和API
class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", wintypes.LONG),
        ("tpDeltaPri", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
    ]

class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]

psapi = ctypes.WinDLL('psapi')
GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
GetProcessMemoryInfo.restype = wintypes.BOOL

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Thread32First = ctypes.windll.kernel32.Thread32First
Thread32Next = ctypes.windll.kernel32.Thread32Next
CloseHandle = ctypes.windll.kernel32.CloseHandle

TH32CS_SNAPTHREAD = 0x00000004

# 尝试导入Cython编译的模块
try:
    from GetThreadContext import get_thread_context
except ImportError as e:
    print(f"Error importing Cython module: {e}")
    sys.exit(1)

def get_process_memory_info():
    """获取当前进程的记忆体使用信息"""
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
    process_handle = ctypes.windll.kernel32.GetCurrentProcess()
    
    if GetProcessMemoryInfo(process_handle, ctypes.byref(counters), counters.cb):
        return {
            "WorkingSetSize": counters.WorkingSetSize,
            "PagefileUsage": counters.PagefileUsage,
        }
    else:
        return None

def collect_thread_info():
    # 获取系统中所有线程的快照
    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)

    if hSnapshot != wintypes.HANDLE(-1):
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(THREADENTRY32)
    
        with open('thread_info.csv', 'w', newline='') as csvfile:
            fieldnames = ['Process ID', 'Thread ID', 'State', 'Create Time (UNIX)', 'Memory Size (RSS)', 'RIP', 'RSP', 'RAX', 'WorkingSetSize', 'PagefileUsage']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
            if Thread32First(hSnapshot, ctypes.byref(entry)):
                while True:
                    try:
                        p = psutil.Process(entry.th32OwnerProcessID)
                        process_state = p.status()  # 获取进程状态
                        create_time = p.create_time()  # 直接使用UNIX时间戳
                        memory_info = p.memory_info()
                        memory_size = memory_info.rss  # 获取进程常驻集大小 (RSS)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        process_state = "Unknown"
                        create_time = "Unknown"
                        memory_size = "Unknown"
                
                    print(f"Process ID: {entry.th32OwnerProcessID}, Thread ID: {entry.th32ThreadID}, State: {process_state}")
                
                    # 获取寄存器和记忆体信息...
                    memory_info = get_process_memory_info()
                    context = get_thread_context(entry.th32ThreadID)
                
                    # 填充并写入CSV记录...
                    writer.writerow({
                        'Process ID': entry.th32OwnerProcessID, 
                        'Thread ID': entry.th32ThreadID, 
                        'State': process_state,
                        'Create Time (UNIX)': create_time,
                        'Memory Size (RSS)': memory_size,
                        'RIP': context.get('Rip', 'N/A'),
                        'RSP': context.get('Rsp', 'N/A'),
                        'RAX': context.get('Rax', 'N/A'),
                        'WorkingSetSize': memory_info.get('WorkingSetSize', 'Error') if memory_info else 'Error',
                        'PagefileUsage': memory_info.get('PagefileUsage', 'Error') if memory_info else 'Error'
                    })
                
                    if not Thread32Next(hSnapshot, ctypes.byref(entry)):
                        break

        CloseHandle(hSnapshot)

# 调用函数
#collect_thread_info()