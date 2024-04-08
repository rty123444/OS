import sys
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal,QTimer
from contextlib import contextmanager
from state2PC import collect_thread_info
from transfer import transfer
from shutil import copyfile
from SJF_Gantt import generate_sjf_and_pcb
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from simulation_process import ProcessScheduler
from process_state import SJFSimulation
import pandas as pd
from HW3 import fcfs_scheduling_with_gantt,rr_scheduling_with_gantt, spn_scheduling_with_gantt, srt_scheduling_with_gantt
from PyQt5.QtWidgets import  QLabel




# 定義一個上下文管理器，用於臨時重定向 sys.stdout
@contextmanager
def redirect_stdout(new_target):
    old_stdout = sys.stdout
    sys.stdout = new_target
    
    try:
        yield new_target
    finally:
        sys.stdout = old_stdout

# 長時間任務線程
class WorkerThread(QThread):
    update_text = pyqtSignal(str)
    update_status = pyqtSignal(dict)
    finished_signal = pyqtSignal()

    def __init__(self, function_to_run, *args):
        super().__init__()
        self.function_to_run = function_to_run
        self.args = args

    def run(self):
        # 重新定向的上下文管理器
        with redirect_stdout(self):
            self.function_to_run(self.update_process_status, *self.args)
        simulation = SJFSimulation('test_value_IO.csv')
        simulation.simulate()

        # 執行更新過程
        scheduler = ProcessScheduler()
        scheduler.run_simulation_update()

        # 發送完成信號
        self.finished_signal.emit()
        
    # 重寫 write 方法以發送文本到 GUI
    def write(self, text):
        self.update_text.emit(text)

    # flush 方法為空，不需要刷新
    def flush(self):
        pass

    def update_process_status(self, status):
        # 觸發更新狀態信號
        self.update_status.emit(status)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 加載UI文件
        uic.loadUi('main_window.ui', self)

        # 獲取UI中的控件
        self.textEdit = self.findChild(QtWidgets.QTextEdit, 'textEdit')
        self.button_collect_thread_info = self.findChild(QtWidgets.QPushButton, 'Button_collect_thread_info')
        self.button_download_csv = self.findChild(QtWidgets.QPushButton, 'Button_download_csv')
        self.button_generate_sjf_and_pcb = self.findChild(QtWidgets.QPushButton, 'Button_generate_sjf_and_pcb')
        self.button_test_value = self.findChild(QtWidgets.QPushButton, 'Button_test_value')

        # 連接按鈕點及事件
        self.button_collect_thread_info.clicked.connect(self.execute_collect_thread_info_and_transfer)
        self.button_download_csv.clicked.connect(self.download_csv)
        self.button_generate_sjf_and_pcb.clicked.connect(self.generate_sjf_and_pcb_and_display_results)
        self.button_test_value.clicked.connect(self.generate_test_value)
        self.label_PCB_Table.setMinimumSize(1200, 700)
        self.label_SJF_Gantt.setMinimumSize(10000, 600)

        self.thread = WorkerThread(self.run_functions)  
        self.thread.update_text.connect(self.textEdit.append)
        self.thread.update_status.connect(self.update_status_labels)

        # 按鈕事件連接
        self.button_generate_sjf_and_pcb = self.findChild(QtWidgets.QPushButton, 'Button_generate_sjf_and_pcb')
        self.button_generate_sjf_and_pcb.clicked.connect(self.start_simulation_and_update)

        self.button_start = self.findChild(QtWidgets.QPushButton, 'Button_Start')
        self.button_start.clicked.connect(self.start_simulation_and_update)

        self.timer = QTimer(self)  # 創建定時器
        self.timer.timeout.connect(self.update_labels_from_csv)
        self.current_row = 0  # 追蹤當前顯示的行數
        self.df = pd.DataFrame()  # 存儲從CSV讀取的數據

        # HW2標籤
        self.labels = {
            'Time': self.findChild(QtWidgets.QLabel, 'label_Time'),
            'New': self.findChild(QtWidgets.QLabel, 'label_New'),
            'Ready': self.findChild(QtWidgets.QLabel, 'label_Ready'),
            'Waiting': self.findChild(QtWidgets.QLabel, 'label_Waiting'),
            'Running': self.findChild(QtWidgets.QLabel, 'label_Running'),
            'Completed': self.findChild(QtWidgets.QLabel, 'label_Completed'),
            'Ready Suspended': self.findChild(QtWidgets.QLabel, 'label_Ready_Suspended'),
            'Waiting Suspended': self.findChild(QtWidgets.QLabel, 'label_Waiting_Suspended'),
        }

        # 將按鈕的點及事連接到 execute_scheduling_algorithms 
        self.pushButton_HW3.clicked.connect(self.execute_scheduling_algorithms)


    def execute_collect_thread_info_and_transfer(self):
        # 執行 collect_thread_info 和 transfer 函数的線程
        self.thread = WorkerThread(self.run_functions)
        self.thread.update_text.connect(self.textEdit.append)
        self.thread.start()

    def run_functions(self):
        collect_thread_info()
        transfer()

    def download_csv(self):
        # 保存對話框
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                        "Save File", "",
                        "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            try:
                source_file = 'filtered_thread_info.csv'
                # 複製文件代替下載
                copyfile(source_file, fileName)
                QtWidgets.QMessageBox.information(self, "下載成功", "文件已成功下載！")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "下載失敗", "文件下載出錯：" + str(e))

    def generate_sjf_and_pcb_and_display_results(self):
        # 呼叫generate_sjf_and_pcb生成圖像
        generate_sjf_and_pcb()
        
        # 顯示PCB_Table.png，並調整大小
        pcb_table_pixmap = QPixmap('PCB_Table.png')
        scaled_pcb_table_pixmap = pcb_table_pixmap.scaled(600, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_PCB_Table.setPixmap(scaled_pcb_table_pixmap)
        
        # 顯示SJF_Gantt.png，並調整大小
        sjf_gantt_pixmap = QPixmap('SJF_Gantt.png')
        scaled_sjf_gantt_pixmap = sjf_gantt_pixmap.scaled(630, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_SJF_Gantt.setPixmap(scaled_sjf_gantt_pixmap)
    
    # 寫死的測試值
    def generate_test_value(self):
        # 呼叫generate_sjf_and_pcb生成圖像
        generate_sjf_and_pcb(file_path='test_value.csv',n=7)
        
        # 顯示PCB_Table.png，並調整大小
        pcb_table_pixmap = QPixmap('PCB_Table.png')
        scaled_pcb_table_pixmap = pcb_table_pixmap.scaled(600, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_PCB_Table.setPixmap(scaled_pcb_table_pixmap)
        
        # 顯示SJF_Gantt.png，並調整大小
        sjf_gantt_pixmap = QPixmap('SJF_Gantt.png')
        scaled_sjf_gantt_pixmap = sjf_gantt_pixmap.scaled(630, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_SJF_Gantt.setPixmap(scaled_sjf_gantt_pixmap)

    def update_status_labels(self, status):
        # 根据傳入的狀態字典更新標籤
        self.label_Time.setText(status.get('Time', ''))
        self.label_New.setText(status.get('New', ''))
        self.label_Ready.setText(status.get('Ready', ''))
        self.label_Waiting.setText(status.get('Waiting', ''))
        self.label_Running.setText(status.get('Running', ''))
        self.label_Completed.setText(status.get('Completed', ''))
        self.label_Ready_Suspended.setText(status.get('Ready_Suspended', ''))
        self.label_Waiting_Suspended.setText(status.get('Waiting_Suspended', ''))

    def start_simulation_and_update(self):
        self.thread = SimulationThread()
        self.thread.finished_signal.connect(self.update_labels_from_csv)
        self.thread.start()
        self.df = pd.read_csv('updated_simulation_output.csv')  # 加載CSV數據
        self.current_row = 0  
        self.timer.start(500)  # 等待時間

    def update_labels_from_csv(self):
        if self.current_row < len(self.df):
            row = self.df.iloc[self.current_row]
            for key, label in self.labels.items():
                label.setText(str(row.get(key, '')))
            self.current_row += 1  # 移動到下一行
        else:
            self.timer.stop()  # 如果所有行都已顯示，則停止定時器

    def execute_scheduling_algorithms(self):
        csv_file_path = 'HW3.csv'  

        # FCFS
        try:
            result_fcfs = fcfs_scheduling_with_gantt(csv_file_path, 'FCFS_Gantt.png')
            self.label_FCFS.setText(f"{result_fcfs:.2f}")
            self.label_FCFS_image.setPixmap(QPixmap('FCFS_Gantt.png'))
        except Exception as e:
            print(f"FCFS error: {e}")

        # RR
        try:
            #result_rr = rr_scheduling_with_gantt(csv_file_path, 'RR_Gantt.png')
            rr_scheduling_with_gantt()
            #將stupid_rr.txt的值寫入label_RR
            with open('stupid_rr.txt', 'r') as f:
                result_rr = f.read()
            self.label_RR.setText(result_rr)
            self.label_RR_image.setPixmap(QPixmap('RR_Gantt.png'))
        except Exception as e:
            print(f"RR error: {e}")

        # SPN
        try:
            result_spn = spn_scheduling_with_gantt(csv_file_path, 'SPN_Gantt.png')
            self.label_SPN.setText(f"{result_spn:.2f}")
            self.label_SPN_image.setPixmap(QPixmap('SPN_Gantt.png'))
        except Exception as e:
            print(f"SPN error: {e}")

        # SRT
        try:
            result_srt = srt_scheduling_with_gantt(csv_file_path, 'SRT_Gantt.png')
            self.label_SRT.setText(f"{result_srt:.2f}")
            self.label_SRT_image.setPixmap(QPixmap('SRT_Gantt.png'))
        except Exception as e:
            print(f"SRT error: {e}")

        # 調整並顯示圖表
        self.resize_and_display_charts()

    def resize_and_display_charts(self):
        # 圖表文件名和對應的標籤
        chart_files = {
            'FCFS_Gantt.png': self.findChild(QLabel, 'label_FCFS_image'),
            'RR_Gantt.png': self.findChild(QLabel, 'label_RR_image'),
            'SPN_Gantt.png': self.findChild(QLabel, 'label_SPN_image'),
            'SRT_Gantt.png': self.findChild(QLabel, 'label_SRT_image'),
        }

        for file_name, label in chart_files.items():
            pixmap = QPixmap(file_name)
            # 圖片大小調整
            scaled_pixmap = pixmap.scaled(500, 290, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)


# 模擬線程
class SimulationThread(QThread):
    finished_signal = pyqtSignal()

    def run(self):
        simulation = SJFSimulation('test_value_IO.csv')
        simulation.simulate()

        scheduler = ProcessScheduler()
        scheduler.run_simulation_update()

        self.finished_signal.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
