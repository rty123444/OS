import pandas as pd

class Process:
    def __init__(self, pid, create_time, burst_time):
        self.pid = pid
        self.create_time = create_time
        self.burst_time = burst_time
        self.remaining_time = burst_time

def read_process_data(file_path='test_value.csv'):
    return pd.read_csv(file_path).sort_values(by=['Create Time (UNIX)', 'Memory Size (RSS)'])

def print_current_state(current_time, running, ready, waiting, ready_suspended, waiting_suspended, completed):
    print(f"\nTime: {current_time}")
    print(f"Running: {running.pid if running else 'None'}")
    print(f"Ready: {[p.pid for p in ready]}")
    print(f"Waiting: {[p.pid for p in waiting]}")
    print(f"Ready Suspended: {[p.pid for p in ready_suspended]}")
    print(f"Waiting Suspended: {[p.pid for p in waiting_suspended]}")
    print(f"Completed: {completed}")

def update_queues_for_io_completion(ready, waiting, ready_suspended):
    if waiting:  # Waiting 的进程优先级最高，转移到 Ready
        ready.extend(waiting)
        waiting.clear()
    # 将 Ready 中现有的进程转移到 Ready Suspended
    if ready:
        ready_suspended.extend(ready)
        ready.clear()

def simulate_sjf_with_queues(file_path):
    df = read_process_data(file_path)
    processes = [Process(row['Process ID'], row['Create Time (UNIX)'], row['Memory Size (RSS)']) for _, row in df.iterrows()]

    current_time = 0
    running = None
    ready = []
    waiting = []
    ready_suspended = []
    waiting_suspended = []
    completed = []

    while processes or running or ready or waiting or ready_suspended or waiting_suspended:
        # 处理新到达的进程
        new_arrivals = [process for process in processes if process.create_time <= current_time]
        for process in new_arrivals:
            if process.pid == "IO":
                if running:
                    waiting.append(running)  # 当前运行的进程移至 Waiting
                running = process  # IO 进程立即运行
            else:
                # 新进程非IO，加入 Ready Suspended
                ready_suspended.append(process)
            processes.remove(process)

        if running and running.remaining_time > 0:
            running.remaining_time -= 1  # 更新运行中进程的剩余时间
        elif running:
            if running.pid == "IO":
                update_queues_for_io_completion(ready, waiting, ready_suspended)  # IO 完成，更新队列
            completed.append(running.pid)
            running = None

        # 尝试启动新的进程
        if not running:
            if ready:
                ready.sort(key=lambda x: x.burst_time)
                running = ready.pop(0)
            elif ready_suspended:
                ready_suspended.sort(key=lambda x: x.burst_time)
                running = ready_suspended.pop(0)

        print_current_state(current_time, running, ready, waiting, ready_suspended, waiting_suspended, completed)
        current_time += 1  # 时间前进

if __name__ == "__main__":
    simulate_sjf_with_queues('test_value.csv')
