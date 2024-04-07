import csv

def transfer():
    # 读取原始CSV文件
    with open('thread_info.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        # 过滤掉RIP, RSP, RAX为N/A的行
        filtered_rows = [row for row in reader if row['RIP'] != 'N/A' and row["State"] != "Unknown"]
        
    # 写入新的CSV文件，名称为filtered_thread_info.csv
    with open('filtered_thread_info.csv', mode='w', newline='') as file:
        if filtered_rows:
            writer = csv.DictWriter(file, fieldnames=filtered_rows[0].keys())
            writer.writeheader()
            writer.writerows(filtered_rows)

# 调用函数
transfer()