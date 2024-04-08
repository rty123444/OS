import pandas as pd

class ProcessScheduler:
    def __init__(self, process_file='test_value_IO.csv', simulation_file='simulation_output.csv', output_file='updated_simulation_output.csv'):
        self.process_file = process_file
        self.simulation_file = simulation_file
        self.output_file = output_file

    class Process:
        def __init__(self, pid, create_time, burst_time):
            self.pid = pid
            self.create_time = create_time
            self.burst_time = burst_time

    def read_data(self):
        simulation_df = pd.read_csv(self.simulation_file)
        process_df = pd.read_csv(self.process_file)
        return simulation_df, process_df

    def update_queues(self, simulation_df, process_df):
        for index, row in simulation_df.iterrows():
            # 更新 Ready 
            if pd.isna(row['Ready']) or row['Ready'] == '':
                self._update_queue_from_suspended(row, 'Ready', 'Ready Suspended', simulation_df, process_df, index)

            # 更新 Waiting 
            if pd.isna(row['Waiting']) or row['Waiting'] == '':
                self._update_queue_from_suspended(row, 'Waiting', 'Waiting Suspended', simulation_df, process_df, index)

        return simulation_df

    def _update_queue_from_suspended(self, row, target_col, source_col, simulation_df, process_df, index):
        suspended_pids = row[source_col].split(", ") if pd.notna(row[source_col]) else []
        if suspended_pids:
            min_rss_pid_df = process_df[process_df['Process ID'].isin(suspended_pids)].nsmallest(1, 'Memory Size (RSS)')
            if not min_rss_pid_df.empty:
                min_rss_pid = min_rss_pid_df['Process ID'].values[0]
                simulation_df.at[index, target_col] = min_rss_pid
                suspended_pids.remove(min_rss_pid)
                simulation_df.at[index, source_col] = ", ".join(suspended_pids)

    def run_simulation_update(self):
        simulation_df, process_df = self.read_data()
        updated_simulation_df = self.update_queues(simulation_df, process_df)
        updated_simulation_df.to_csv(self.output_file, index=False)
        print(f"Updated simulation output has been saved to {self.output_file}")

# 調用函數
'''
if __name__ == "__main__":
    scheduler = ProcessScheduler()
    scheduler.run_simulation_update()
'''

