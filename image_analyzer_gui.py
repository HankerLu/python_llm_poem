from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QHBoxLayout, QScrollArea)
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
        florence_text = florence_result.get('<MORE_DETAILED_CAPTION>', '')
        self.finished.emit(florence_text, keywords)

class ImageAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.keywords_buttons = []  # 存储关键词按钮
        self.init_models()
        self.initUI()

    def init_models(self):
        """初始化模型"""
        try:
            analyzer.initialize()
            self.status_label = QLabel("模型初始化完成，请选择图片进行分析。")
        except Exception as e:
            self.status_label = QLabel(f"模型初始化失败：{str(e)}")

    def initUI(self):
        self.setWindowTitle('图像分析器')
        self.setGeometry(100, 100, 1000, 800)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        main_layout.addWidget(self.image_label)

        # 创建操作按钮
        button_layout = QHBoxLayout()
        self.select_button = QPushButton('选择图片')
        self.analyze_button = QPushButton('分析图片')
        self.analyze_button.setEnabled(False)
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.analyze_button)
        main_layout.addLayout(button_layout)

        # 添加状态标签
        main_layout.addWidget(self.status_label)

        # 创建关键词按钮的滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(100)
        self.keywords_widget = QWidget()
        self.keywords_layout = QHBoxLayout(self.keywords_widget)
        scroll.setWidget(self.keywords_widget)
        main_layout.addWidget(scroll)

        # 连接信号
        self.select_button.clicked.connect(self.select_image)
        self.analyze_button.clicked.connect(self.analyze_image)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
        
        if file_name:
            self.current_image = Image.open(file_name).convert('RGB')
            
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            self.analyze_button.setEnabled(True)
            self.clear_keywords()
            self.status_label.setText("图片已加载，请点击分析按钮进行分析。")

    def clear_keywords(self):
        """清除现有的关键词按钮"""
        for button in self.keywords_buttons:
            self.keywords_layout.removeWidget(button)
            button.deleteLater()
        self.keywords_buttons.clear()

    def create_keyword_button(self, keyword):
        """创建关键词按钮"""
        button = QPushButton(keyword)
        button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #c0c0c0;
                border-radius: 10px;
                padding: 5px 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #a0a0a0;
            }
        """)
        button.clicked.connect(lambda: self.keyword_clicked(keyword))
        return button

    def keyword_clicked(self, keyword):
        """处理关键词按钮点击事件"""
        self.status_label.setText(f"选中关键词: {keyword}")

    def analyze_image(self):
        if self.current_image:
            self.analyze_button.setEnabled(False)
            self.status_label.setText("正在分析中，请稍候...")
            self.clear_keywords()
            
            self.analyzer_thread = AnalyzerThread(self.current_image)
            self.analyzer_thread.finished.connect(self.handle_analysis_result)
            self.analyzer_thread.start()

    def handle_analysis_result(self, florence_result, keywords):
        self.status_label.setText("分析完成！")
        
        # 解析关键词字符串并创建按钮
        try:
            # 假设关键词格式为 "[关键词1,关键词2,关键词3...]"
            keywords = keywords.strip('[]').split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    button = self.create_keyword_button(keyword)
                    self.keywords_layout.addWidget(button)
                    self.keywords_buttons.append(button)
        except Exception as e:
            self.status_label.setText(f"关键词解析错误：{str(e)}")
        
        self.analyze_button.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = ImageAnalyzerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 