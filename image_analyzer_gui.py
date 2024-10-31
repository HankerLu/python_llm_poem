from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QTextEdit, QFileDialog)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
from PIL import Image
import io
from TestFuncs import analyzer

class AnalyzerThread(QThread):
    """后台处理线程，避免界面卡顿"""
    finished = pyqtSignal(str, str)  # 信号：Florence描述, 关键词列表

    def __init__(self, image):
        super().__init__()
        self.image = image

    def run(self):
        florence_result, keywords = analyzer.analyze_image(self.image)
        # 从字典中提取具体的描述文本
        florence_text = florence_result.get('<MORE_DETAILED_CAPTION>', '')
        self.finished.emit(florence_text, keywords)

class ImageAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None
        # 初始化模型
        self.init_models()
        self.initUI()

    def init_models(self):
        """初始化模型"""
        self.result_text = QTextEdit()
        self.result_text.setText("正在初始化模型，请稍候...")
        try:
            analyzer.initialize()
            self.result_text.setText("模型初始化完成，请选择图片进行分析。")
        except Exception as e:
            self.result_text.setText(f"模型初始化失败：{str(e)}")

    def initUI(self):
        self.setWindowTitle('图像分析器')
        self.setGeometry(100, 100, 800, 800)

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建控件
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)

        self.select_button = QPushButton('选择图片')
        self.analyze_button = QPushButton('分析图片')
        self.analyze_button.setEnabled(False)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)

        # 添加控件到布局
        layout.addWidget(self.image_label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.result_text)

        # 连接信号
        self.select_button.clicked.connect(self.select_image)
        self.analyze_button.clicked.connect(self.analyze_image)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
        
        if file_name:
            # 保存PIL Image对象供分析使用
            self.current_image = Image.open(file_name).convert('RGB')
            
            # 显示图片
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            self.analyze_button.setEnabled(True)
            self.result_text.clear()

    def analyze_image(self):
        if self.current_image:
            self.analyze_button.setEnabled(False)
            self.result_text.setText("正在分析中，请稍候...")
            
            # 创建并启动分析线程
            self.analyzer_thread = AnalyzerThread(self.current_image)
            self.analyzer_thread.finished.connect(self.handle_analysis_result)
            self.analyzer_thread.start()

    def handle_analysis_result(self, florence_result, keywords):
        result_text = f"Florence描述:\n{florence_result}\n\n关键词列表:\n{keywords}"
        self.result_text.setText(result_text)
        self.analyze_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = ImageAnalyzerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 