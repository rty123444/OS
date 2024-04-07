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
    print(f"Ready: {ready.pid if ready else 'None'}")
    print(f"Waiting: {waiting.pid if waiting else 'None'}")
    print(f"Ready Suspended: {[p.pid for p in ready_suspended]}")
    print(f"Waiting Suspended: {[p.pid for p in waiting_suspended]}")
    print(f"Completed: {completed}")

def simulate_sjf_with_queues(file_path):
    df = read_process_data(file_path)
    processes = [Process(row['Process ID'], row['Create Time (UNIX)'], row['Memory Size (RSS)']) for _, row in df.iterrows()]

    current_time = 0
    running = None
    ready = None
    waiting = None
    ready_suspended = []
    waiting_suspended = []
    completed = []

    while processes or running or ready or waiting or ready_suspended or waiting_suspended:
        # Handle new arrivals
        while processes and processes[0].create_time <= current_time:
            process = processes.pop(0)
            if not running and not ready:
                running = process
            elif process.pid == "IO" and running and running.pid != "IO":
                # IO interrupts current running process
                if waiting:
                    waiting_suspended.append(waiting)  # Move current waiting to suspended
                    waiting_suspended.sort(key=lambda p: p.remaining_time)
                waiting = running  # Current running process moves to waiting
                running = process  # IO starts running
            else:
                ready_suspended.append(process)
                ready_suspended.sort(key=lambda p: p.remaining_time)

        # Promote ready to running if running is None
        if not running:
            if ready:
                running = ready
                ready = None
            elif ready_suspended:
                ready = ready_suspended.pop(0)
                running = ready
                ready = None

        # Handle process completion
        if running:
            running.remaining_time -= 1
            if running.remaining_time == 0:
                completed.append(running.pid)
                running = None
                # Promote next process from ready or waiting
                if ready:
                    running = ready
                    ready = None
                elif waiting:
                    running = waiting
                    waiting = None

        # After IO completion, ensure waiting process moves to ready if available
        if not running and not ready and waiting:
            ready = waiting
            waiting = None

        # Adjust queues
        if not ready and ready_suspended:
            ready = ready_suspended.pop(0)
        if not waiting and waiting_suspended:
            waiting = waiting_suspended.pop(0)

        print_current_state(current_time, running, ready, waiting, ready_suspended, waiting_suspended, completed)

        current_time += 1

if __name__ == "__main__":
    simulate_sjf_with_queues('test_value.csv')