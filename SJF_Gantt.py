import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_sjf_and_pcb(file_path='filtered_thread_info.csv', output_gantt='SJF_Gantt.png', output_pcb='PCB_Table.png', output_csv='chosen10.csv',n=10):
    # 读取 CSV 文件
    df = pd.read_csv(file_path)

    # 随机选择10条数据
    df_sampled = df.sample(n)

    # 按 Create Time (UNIX) 排序，以确定进程的抵达顺序
    df_sampled_sorted_by_arrival = df_sampled.sort_values(by='Create Time (UNIX)')

    # 初始化进程执行的开始时间和结束时间
    current_time = 0
    for index, row in df_sampled_sorted_by_arrival.iterrows():
        if current_time < row['Create Time (UNIX)']:
            current_time = row['Create Time (UNIX)']
        df_sampled_sorted_by_arrival.at[index, 'Start Time'] = current_time
        current_time += row['Memory Size (RSS)']
        df_sampled_sorted_by_arrival.at[index, 'End Time'] = current_time

    # 按 Process ID 排序，以确定Y轴的顺序，但保留SJF的执行顺序
    df_sampled_sorted_by_arrival['PID_Order'] = df_sampled_sorted_by_arrival['Process ID'].rank(method='dense').astype(int)

    # 绘制 SJF 调度甘特图
    plt.figure(figsize=(10, 6))
    colors = plt.cm.jet(np.linspace(0, 1, len(df_sampled_sorted_by_arrival)))
    for index, (pid, row) in enumerate(df_sampled_sorted_by_arrival.iterrows()):
        plt.barh(row['PID_Order'], row['End Time']-row['Start Time'], left=row['Start Time'], color=colors[index], edgecolor='black', label=f'PID {row["Process ID"]}')
    plt.xlabel('Time')
    plt.ylabel('Process ID Order')
    plt.title('SJF Scheduling Visualized with PID Order')
    plt.yticks(df_sampled_sorted_by_arrival['PID_Order'], df_sampled_sorted_by_arrival['Process ID'])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_gantt)

    # 绘制 PCB 表格
    fig, ax = plt.subplots(figsize=(12, 2 + 0.5*len(df_sampled_sorted_by_arrival)))
    ax.axis('off')
    the_table = ax.table(cellText=df_sampled_sorted_by_arrival[['State', 'Process ID', 'RIP', 'RSP', 'RAX', 'WorkingSetSize', 'PagefileUsage','Create Time (UNIX)','Memory Size (RSS)']].values, colLabels=['State', 'Process ID', 'RIP', 'RSP', 'RAX', 'WorkingSetSize', 'PagefileUsage','Create Time (UNIX)','Memory Size (RSS)'], cellLoc='center', loc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(10)
    the_table.scale(1.2, 1.2)
    plt.title("Process Control Block (PCB) Information", fontsize=14, weight='bold')
    plt.tight_layout()
    plt.savefig(output_pcb)

    # 保存选择的10个进程的信息到新的CSV文件
    df_sampled.to_csv(output_csv, index=False)
    print("SJF 甘特图、PCB 表格和新的CSV文件已经生成！")

# 调用函数
#generate_sjf_and_pcb()
