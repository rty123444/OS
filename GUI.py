import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal
from contextlib import contextmanager
from state2PC import collect_thread_info
from transfer import transfer
from shutil import copyfile
from SJF_Gantt import generate_sjf_and_pcb
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt




# 定义一个上下文管理器，用于临时重定向 sys.stdout
@contextmanager
def redirect_stdout(new_target):
    old_stdout = sys.stdout
    sys.stdout = new_target
    try:
        yield new_target
    finally:
        sys.stdout = old_stdout

# 定义运行长时间任务的线程类
class WorkerThread(QThread):
    update_text = pyqtSignal(str)
    update_status = pyqtSignal(dict)

    def __init__(self, function_to_run, *args):
        super().__init__()
        self.function_to_run = function_to_run
        self.args = args

    def run(self):
        # 使用重定向的上下文管理器
        with redirect_stdout(self):
            self.function_to_run(self.update_process_status, *self.args)

    # 重写 write 方法以发送文本到 GUI
    def write(self, text):
        self.update_text.emit(text)

    # flush 方法为空，因为我们不需要刷新任何东西
    def flush(self):
        pass

    def update_process_status(self, status):
        # 触发更新状态的信号
        self.update_status.emit(status)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 加载UI文件
        uic.loadUi('main_window.ui', self)

        # 获取UI中的控件
        self.textEdit = self.findChild(QtWidgets.QTextEdit, 'textEdit')
        self.button_collect_thread_info = self.findChild(QtWidgets.QPushButton, 'Button_collect_thread_info')
        self.button_download_csv = self.findChild(QtWidgets.QPushButton, 'Button_download_csv')
        self.button_generate_sjf_and_pcb = self.findChild(QtWidgets.QPushButton, 'Button_generate_sjf_and_pcb')
        self.button_test_value = self.findChild(QtWidgets.QPushButton, 'Button_test_value')

        # 连接按钮点击事件
        self.button_collect_thread_info.clicked.connect(self.execute_collect_thread_info_and_transfer)
        self.button_download_csv.clicked.connect(self.download_csv)
        self.button_generate_sjf_and_pcb.clicked.connect(self.generate_sjf_and_pcb_and_display_results)
        self.button_test_value.clicked.connect(self.generate_test_value)
        self.label_PCB_Table.setMinimumSize(1200, 700)
        self.label_SJF_Gantt.setMinimumSize(10000, 600)

        self.thread = WorkerThread(self.run_functions)  # 假设这是您启动线程的方式
        self.thread.update_text.connect(self.textEdit.append)
        self.thread.update_status.connect(self.update_status_labels)

    def execute_collect_thread_info_and_transfer(self):
        # 运行 collect_thread_info 和 transfer 函数的线程
        self.thread = WorkerThread(self.run_functions)
        self.thread.update_text.connect(self.textEdit.append)
        self.thread.start()

    def run_functions(self):
        collect_thread_info()
        transfer()

    def download_csv(self):
        # 打开文件保存对话框
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                        "Save File", "",
                        "CSV Files (*.csv);;All Files (*)", options=options)
        if fileName:
            try:
                # 假设 filtered_thread_info.csv 在您的项目根目录下
                source_file = 'filtered_thread_info.csv'
                # 将文件复制到用户选择的位置
                copyfile(source_file, fileName)
                QtWidgets.QMessageBox.information(self, "下载成功", "文件已成功下载！")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "下载失败", "文件下载出错：" + str(e))

    def generate_sjf_and_pcb_and_display_results(self):
        # 呼叫generate_sjf_and_pcb來生成圖像
        generate_sjf_and_pcb()
        
        # 顯示PCB_Table.png，並調整大小為600x360像素
        pcb_table_pixmap = QPixmap('PCB_Table.png')
        scaled_pcb_table_pixmap = pcb_table_pixmap.scaled(600, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_PCB_Table.setPixmap(scaled_pcb_table_pixmap)
        
        # 顯示SJF_Gantt.png，並調整大小為630x500像素
        sjf_gantt_pixmap = QPixmap('SJF_Gantt.png')
        scaled_sjf_gantt_pixmap = sjf_gantt_pixmap.scaled(630, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_SJF_Gantt.setPixmap(scaled_sjf_gantt_pixmap)

    def generate_test_value(self):
        # 呼叫generate_sjf_and_pcb來生成圖像
        generate_sjf_and_pcb(file_path='test_value.csv',n=7)
        
        # 顯示PCB_Table.png，並調整大小為600x360像素
        pcb_table_pixmap = QPixmap('PCB_Table.png')
        scaled_pcb_table_pixmap = pcb_table_pixmap.scaled(600, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_PCB_Table.setPixmap(scaled_pcb_table_pixmap)
        
        # 顯示SJF_Gantt.png，並調整大小為630x500像素
        sjf_gantt_pixmap = QPixmap('SJF_Gantt.png')
        scaled_sjf_gantt_pixmap = sjf_gantt_pixmap.scaled(630, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_SJF_Gantt.setPixmap(scaled_sjf_gantt_pixmap)

    def update_status_labels(self, status):
        # 根据传入的状态字典更新标签
        # 假设状态字典包含了所有需要的信息
        self.label_New.setText(status.get('New', ''))
        self.label_Ready.setText(status.get('Ready', ''))
        self.label_Waiting.setText(status.get('Waiting', ''))
        self.label_Running.setText(status.get('Running', ''))
        self.label_Completed.setText(status.get('Completed', ''))
        self.label_Ready_Suspended.setText(status.get('Ready_Suspended', ''))
        self.label_Waiting_Suspended.setText(status.get('Waiting_Suspended', ''))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
