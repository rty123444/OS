import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_processes_data(csv_file_path='processes_data.csv'):
    """
    从CSV文件加载进程数据。
    """
    processes_data_df = pd.read_csv(csv_file_path)
    processes_data_df['burst_time'] = processes_data_df['burst_time'].astype(int)
    processes_data_df['arrival_time'] = processes_data_df['arrival_time'].astype(int)
    return processes_data_df

def fcfs_scheduling_with_gantt(csv_file_path='HW3.csv', output_gantt='FCFS_Gantt.png'):
    # 从CSV文件加载进程数据
    processes = pd.read_csv(csv_file_path)
    # 确保数据类型是整型
    processes['burst_time'] = processes['burst_time'].astype(int)
    processes['arrival_time'] = processes['arrival_time'].astype(int)
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(processes)))
    current_time = 0
    total_waiting_time = 0
    waiting_times = []

    for index, process in processes.iterrows():
        if current_time < process['arrival_time']:
            current_time = process['arrival_time']
        start_time = current_time
        waiting_time = start_time - process['arrival_time']
        waiting_times.append(waiting_time)
        total_waiting_time += waiting_time
        current_time += process['burst_time']
        plt.barh(process['PID'], process['burst_time'], left=start_time, color=colors[index], edgecolor='black', label=f"{process['PID']}")

    average_waiting_time = total_waiting_time / len(processes)

    plt.xlabel('Time')
    plt.ylabel('Processes')
    plt.title('FCFS Scheduling Gantt Chart')
    plt.yticks(processes['PID'], processes['PID'])
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.legend()
    plt.savefig(output_gantt)
    print(f"FCFS甘特图已保存为 {output_gantt}。")

    return average_waiting_time

def rr_scheduling_with_gantt(csv_file_path='HW3.csv', quantum=3, output_gantt='RR_Gantt.png'):
    '''
    processes = pd.read_csv(csv_file_path)
    processes['remaining_time'] = processes['burst_time']
    processes['start_time'] = -1  # 初始时刻未开始
    processes['completed'] = False
    time = 0
    total_waiting_time = 0
    colors = plt.cm.viridis(np.linspace(0, 1, len(processes)))

    plt.figure(figsize=(10, 6))
    while not processes['completed'].all():
        for i, process in processes.iterrows():
            if process['arrival_time'] <= time and not process['completed']:
                if process['start_time'] == -1:
                    processes.at[i, 'start_time'] = time
                exec_time = min(quantum, process['remaining_time'])
                plt.barh(process['PID'], exec_time, left=time, color=colors[i], edgecolor='black', label='PID ' + process['PID'] if process['start_time'] == time else "")
                time += exec_time
                processes.at[i, 'remaining_time'] -= exec_time
                if processes.at[i, 'remaining_time'] == 0:
                    processes.at[i, 'completed'] = True
                    total_waiting_time += time - process['arrival_time'] - process['burst_time']

    average_waiting_time = total_waiting_time / len(processes)
    
    plt.xlabel('Time')
    plt.ylabel('Processes')
    plt.title('Round Robin Scheduling Gantt Chart')
    plt.yticks(np.arange(len(processes)), processes['PID'])
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_gantt)
    print(f"RR Gantt chart saved as {output_gantt}. Average waiting time: {average_waiting_time:.2f}")
    '''
    return 1



def spn_scheduling_with_gantt(csv_file_path='HW3.csv', output_gantt='SPN_Gantt.png'):
    '''
    
    '''
    # 从CSV文件加载进程数据
    processes = pd.read_csv(csv_file_path)
    # 确保数据类型是整型
    processes['burst_time'] = processes['burst_time'].astype(int)
    processes['arrival_time'] = processes['arrival_time'].astype(int)
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(processes)))
    current_time = 0
    total_waiting_time = 0
    processes_completed = 0
    processes['start_time'] = np.nan
    processes['waiting_time'] = np.nan

    while processes_completed < len(processes):
        # 过滤出已到达且未开始的进程
        available_processes = processes[(processes['arrival_time'] <= current_time) & processes['start_time'].isna()]
        
        if not available_processes.empty:
            # 选择最短执行时间的进程
            next_process = available_processes.loc[available_processes['burst_time'].idxmin()]
            next_index = next_process.name
            start_time = max(current_time, processes.loc[next_index, 'arrival_time'])
            processes.at[next_index, 'start_time'] = start_time
            processes.at[next_index, 'waiting_time'] = start_time - processes.loc[next_index, 'arrival_time']
            current_time = start_time + processes.loc[next_index, 'burst_time']
            processes_completed += 1
            
            # 绘制进程的执行段到甘特图
            plt.barh(processes.loc[next_index, 'PID'], processes.loc[next_index, 'burst_time'], left=processes.loc[next_index, 'start_time'], color=colors[next_index], edgecolor='black', label=f"PID {processes.loc[next_index, 'PID']}")
        else:
            current_time += 1  # 如果没有进程可以执行，时间向前推进
    
    total_waiting_time = processes['waiting_time'].sum()
    average_waiting_time = total_waiting_time / len(processes)

    plt.xlabel('Time')
    plt.ylabel('Processes')
    plt.title('SPN Scheduling Gantt Chart')
    plt.yticks(np.arange(1, len(processes) + 1), processes['PID'])
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_gantt)
    print(f"SPN甘特图已保存为 {output_gantt}。")

    return average_waiting_time

def srt_scheduling_with_gantt(csv_file_path='HW3.py', output_gantt='SRT_Gantt.png'):
    # 从CSV文件加载进程数据
    processes = pd.read_csv(csv_file_path)
    # 确保数据类型是整型
    processes['burst_time'] = processes['burst_time'].astype(int)
    processes['arrival_time'] = processes['arrival_time'].astype(int)
    
    plt.figure(figsize=(10, 6))
    n = len(processes)
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    time = 0
    total_waiting_time = 0
    executed_time = [0] * n
    completed = [False] * n

    while any(not c for c in completed):
        # 在当前时间，找到所有已到达且未完成的进程
        valid_processes = [(i, row['PID'], row['burst_time'] - executed_time[i]) for i, row in processes.iterrows() if row['arrival_time'] <= time and not completed[i]]
        
        if not valid_processes:
            time += 1
            continue

        # 选择剩余时间最短的进程
        i, pid, remaining_time = min(valid_processes, key=lambda x: x[2])
        
        # 执行这个进程一个时间单位
        executed_time[i] += 1
        time += 1
        plt.barh(pid, 1, left=time-1, color=colors[i], edgecolor='black')
        
        if executed_time[i] == processes.loc[i, 'burst_time']:
            completed[i] = True
            total_waiting_time += time - processes.loc[i, 'arrival_time'] - processes.loc[i, 'burst_time']

    average_waiting_time = total_waiting_time / n

    plt.xlabel('Time')
    plt.ylabel('Processes')
    plt.title('SRT Scheduling Gantt Chart')
    plt.yticks(processes.index + 1, processes['PID'])  # 修正了这里，以确保y轴标签正确显示
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(output_gantt)
    print(f"SRT甘特图已保存为 {output_gantt}。")

    return average_waiting_time



# FCFS
#fcfs_scheduling_with_gantt(processes_data_df.sort_values(by='arrival_time'))
#print(fcfs_scheduling_with_gantt(processes_data_df.sort_values(by='arrival_time')))

# RR
#avg_waiting_time_rr = rr_scheduling_with_gantt(processes_data_df)
#print(rr_scheduling_with_gantt(processes_data_df))

# SPN
#avg_waiting_time_spn = spn_scheduling_with_gantt(processes_data_df)
#print(spn_scheduling_with_gantt(processes_data_df))

# SRT
#avg_waiting_time_srt = srt_scheduling_with_gantt(processes_data_df)
#print(srt_scheduling_with_gantt(processes_data_df))

#print(fcfs_scheduling_with_gantt('HW3.csv'))
print(rr_scheduling_with_gantt('HW3.csv'))
#print(spn_scheduling_with_gantt('HW3.csv'))
#print(srt_scheduling_with_gantt('HW3.csv'))