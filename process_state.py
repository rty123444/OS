import pandas as pd

class SJFSimulation:
    def __init__(self, file_path='test_value_IO.csv'):
        self.file_path = file_path
        self.processes = []
        self.output_data = []

    class Process:
        def __init__(self, pid, create_time, burst_time):
            self.pid = pid
            self.create_time = create_time
            self.burst_time = burst_time
            self.remaining_time = burst_time

    def read_process_data(self):
        df = pd.read_csv(self.file_path).sort_values(by=['Create Time (UNIX)', 'Memory Size (RSS)'])
        self.processes = [self.Process(row['Process ID'], row['Create Time (UNIX)'], row['Memory Size (RSS)']) for _, row in df.iterrows()]

    def update_queues_for_io_completion(self, ready, waiting, ready_suspended):
        if waiting:
            ready.extend(waiting)
            waiting.clear()
        if ready:
            ready_suspended.extend(ready)
            ready.clear()

    def simulate(self):
        self.read_process_data()

        current_time = 0
        running = None
        ready = []
        waiting = []
        ready_suspended = []
        waiting_suspended = []
        completed = []

        while self.processes or running or ready or waiting or ready_suspended or waiting_suspended:
            new_arrivals = [process for process in self.processes if process.create_time <= current_time]
            for process in new_arrivals:
                if process.pid == "IO":
                    if running:
                        waiting.append(running)
                    running = process
                else:
                    ready_suspended.append(process)
                self.processes.remove(process)

            if running and running.remaining_time > 0:
                running.remaining_time -= 1
            elif running:
                if running.pid == "IO":
                    self.update_queues_for_io_completion(ready, waiting, ready_suspended)
                completed.append(running.pid)
                running = None

            if not running:
                if ready:
                    ready.sort(key=lambda x: x.burst_time)
                    running = ready.pop(0)
                elif ready_suspended:
                    ready_suspended.sort(key=lambda x: x.burst_time)
                    running = ready_suspended.pop(0)

            self.output_data.append({
                "Time": current_time,
                "Running": running.pid if running else 'None',
                "Ready": ', '.join([p.pid for p in ready]),
                "Waiting": ', '.join([p.pid for p in waiting]),
                "Ready Suspended": ', '.join([p.pid for p in ready_suspended]),
                "Waiting Suspended": ', '.join([p.pid for p in waiting_suspended]),
                "Completed": ', '.join(completed)
            })

            current_time += 1

        self.save_output()

    def save_output(self):
        output_df = pd.DataFrame(self.output_data)
        output_df.to_csv('simulation_output.csv', index=False)

'''
if __name__ == "__main__":
    simulation = SJFSimulation('test_value_IO.csv')
    simulation.simulate()
'''

