from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QHBoxLayout, QScrollArea,
                           QDialog, QRadioButton, QButtonGroup, QTextBrowser, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
from PIL import Image, ImageDraw, ImageFont
import io
from TestFuncs import analyzer
import os

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

class StyleSheet:
    """统一的样式定义"""
    MAIN_WINDOW = """
        QMainWindow {
            background-color: #F7E8D0;  /* 米黄色背景 */
        }
    """
    
    CENTRAL_WIDGET = """
        QWidget {
            background-color: #F7E8D0;
        }
    """
    
    BUTTON = """
        QPushButton {
            background-color: #8B4513;  /* 棕色 */
            color: #F7E8D0;  /* 米色文字 */
            border: 2px solid #654321;
            border-radius: 15px;
            padding: 8px 16px;
            font-family: "楷体", KaiTi;
            font-size: 14pt;
            min-width: 120px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #654321;
            border-color: #8B4513;
        }
        QPushButton:pressed {
            background-color: #543210;
        }
        QPushButton:disabled {
            background-color: #A89080;
            border-color: #987654;
        }
    """
    
    KEYWORD_BUTTON = """
        QPushButton {
            background-color: #DEB887;  /* 实木色 */
            color: #4A3728;  /* 深褐色文字 */
            border: 2px solid #BC8F8F;
            border-radius: 12px;
            padding: 5px 10px;
            font-family: "楷体", KaiTi;
            font-size: 12pt;
            margin: 2px;
        }
        QPushButton:hover {
            background-color: #D2B48C;
            border-color: #8B4513;
        }
        QPushButton:checked {
            background-color: #8B4513;
            color: #F7E8D0;
            border-color: #654321;
        }
    """
    
    SCROLL_AREA = """
        QScrollArea {
            border: 2px solid #8B4513;
            border-radius: 10px;
            background-color: #FFF5E6;
        }
        QScrollBar:horizontal {
            border: none;
            background: #F7E8D0;
            height: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background: #8B4513;
            border-radius: 5px;
            min-width: 20px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """
    
    STATUS_LABEL = """
        QLabel {
            color: #4A3728;
            font-family: "楷体", KaiTi;
            font-size: 12pt;
            padding: 5px;
            border: 1px solid #BC8F8F;
            border-radius: 8px;
            background-color: #FFF5E6;
        }
    """
    
    IMAGE_LABEL = """
        QLabel {
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 5px;
            background-color: #FFF5E6;
        }
    """

class KeywordButton(QPushButton):
    """自定义关键词按钮类，支持选中状态"""
    def __init__(self, keyword):
        super().__init__(keyword)
        self.keyword = keyword
        self.selected = False
        self.setCheckable(True)  # 使按钮可切换
        self.setStyleSheet(StyleSheet.KEYWORD_BUTTON)

    def update_style(self):
        """保持使用统一样式"""
        pass  # 样式由StyleSheet.KEYWORD_BUTTON控制

class PoemTypeDialog(QDialog):
    """诗歌类型选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_type = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('选择诗歌体裁')
        layout = QVBoxLayout(self)

        # 创建诗歌类型选项
        self.button_group = QButtonGroup(self)
        poem_types = [
            '五言绝句', '七言绝句',
            '五言律诗', '七言律诗',
            '五言古诗', '七言古诗',
            '词(婉约)', '词(豪放)'
        ]

        for i, type_name in enumerate(poem_types):
            radio = QRadioButton(type_name)
            layout.addWidget(radio)
            self.button_group.addButton(radio, i)

        # 确认按钮
        confirm_button = QPushButton('确认')
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)

    def get_selected_type(self):
        selected_button = self.button_group.checkedButton()
        return selected_button.text() if selected_button else None

class PoemDisplayDialog(QDialog):
    """诗歌展示对话框"""
    def __init__(self, poem_text, parent=None):
        super().__init__(parent)
        self.poem_text = poem_text
        self.parent = parent
        self.initUI()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #F7E8D0;
            }
            QTextBrowser {
                background-color: #FFF5E6;
                border: 2px solid #8B4513;
                border-radius: 15px;
                padding: 20px;
                font-family: "楷体", KaiTi;
                font-size: 16pt;
                color: #4A3728;
            }
            QPushButton {
                background-color: #8B4513;
                color: #F7E8D0;
                border: 2px solid #654321;
                border-radius: 15px;
                padding: 8px 16px;
                font-family: "楷体", KaiTi;
                font-size: 14pt;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #654321;
                border-color: #8B4513;
            }
        """)

    def initUI(self):
        self.setWindowTitle('诗词雅韵')
        self.setMinimumSize(500, 700)
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 使用QTextBrowser来显示诗歌
        text_browser = QTextBrowser()
        text_browser.setText(self.poem_text)
        layout.addWidget(text_browser)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        create_image_button = QPushButton('合成图片')
        create_image_button.clicked.connect(self.show_composite_image)
        close_button = QPushButton('关闭')
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(create_image_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def show_composite_image(self):
        """显示合成图片的新窗口"""
        try:
            composite_image = self.create_poem_image()
            if composite_image:
                image_dialog = ImageDisplayDialog(composite_image, self)
                image_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建图片失败：{str(e)}")

    def create_poem_image(self):
        """将诗歌合成到原始图片上"""
        if not self.parent.current_image:
            raise ValueError("未找到原始图片")

        # 获取原始图片
        original_image = self.parent.current_image.copy()

        # 调整图片大小，确保有足够空间放置文字
        target_width = 800
        target_height = 1000
        
        # 计算调整后的图片尺寸，保持原始比例
        width_ratio = target_width / original_image.width
        height_ratio = (target_height * 0.7) / original_image.height  # 留30%的空间给文字
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(original_image.width * ratio)
        new_height = int(original_image.height * ratio)
        
        # 创建新的白色背景图片
        new_image = Image.new('RGB', (target_width, target_height), 'white')
        
        # 调整原始图片大小
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 将调整后的图片粘贴到新图片的中心位置
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 3  # 将图片放在上部三分之一处
        new_image.paste(resized_image, (x_offset, y_offset))

        # 创建绘图对象
        draw = ImageDraw.Draw(new_image)

        # 尝试加载字体
        try:
            if os.name == 'nt':
                font_path = "C:\\Windows\\Fonts\\simkai.ttf"
            else:
                font_path = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
            font = ImageFont.truetype(font_path, 40)  # 增大字体大小
        except Exception:
            font = ImageFont.load_default()

        # 计算文字位置，从图片下方开始
        text_y = y_offset + new_height + 50  # 增加与图片的间距
        
        # 分行绘制诗歌文本
        lines = self.poem_text.split('\n')
        for line in lines:
            if line.strip():
                # 计算文本宽度以居中显示
                text_width = draw.textlength(line, font=font)
                text_x = (target_width - text_width) // 2
                # 绘制文字阴影效果
                draw.text((text_x+1, text_y+1), line, fill='gray', font=font)
                # 绘制主要文字
                draw.text((text_x, text_y), line, fill='black', font=font)
                text_y += 60  # 增加行间距

        return new_image

class ImageDisplayDialog(QDialog):
    """图片显示对话框"""
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.initUI()

    def initUI(self):
        self.setWindowTitle('合成图片')
        
        # 使用水平布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 创建标签显示图片
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        # 将PIL图像转换为QPixmap
        img_byte_arr = io.BytesIO()
        self.image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        pixmap = QPixmap()
        pixmap.loadFromData(img_byte_arr)

        # 获取屏幕大小
        screen = QApplication.primaryScreen().geometry()
        max_width = screen.width() * 0.8  # 屏幕宽度的80%
        max_height = screen.height() * 0.8  # 屏幕高度的80%

        # 计算缩放比例
        scale_width = max_width / pixmap.width()
        scale_height = max_height / pixmap.height()
        scale = min(scale_width, scale_height)

        # 如果图片太大，进行缩放
        if scale < 1:
            pixmap = pixmap.scaled(
                int(pixmap.width() * scale),
                int(pixmap.height() * scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

        # 设置图片
        label.setPixmap(pixmap)
        main_layout.addWidget(label)

        # 创建右侧按钮布局
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)  # 按钮靠上对齐
        
        # 关闭按钮
        close_button = QPushButton('关闭')
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: #F7E8D0;
                border: 2px solid #654321;
                border-radius: 15px;
                padding: 8px 16px;
                font-family: "楷体", KaiTi;
                font-size: 14pt;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #654321;
                border-color: #8B4513;
            }
        """)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)

        # 设置窗口大小
        self.resize(pixmap.width() + 150, pixmap.height() + 40)  # 增加宽度以容纳按钮

class ImageAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.keywords_buttons = []  # 存储关键词按钮
        self.selected_keywords = set()  # 存储已选中的关键词
        self.init_models()
        self.initUI()
        self.apply_styles()

    def apply_styles(self):
        """应用统一样式"""
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)
        self.centralWidget().setStyleSheet(StyleSheet.CENTRAL_WIDGET)
        self.select_button.setStyleSheet(StyleSheet.BUTTON)
        self.analyze_button.setStyleSheet(StyleSheet.BUTTON)
        self.confirm_keywords_button.setStyleSheet(StyleSheet.BUTTON)
        self.status_label.setStyleSheet(StyleSheet.STATUS_LABEL)
        self.image_label.setStyleSheet(StyleSheet.IMAGE_LABEL)
        self.scroll.setStyleSheet(StyleSheet.SCROLL_AREA)

    def init_models(self):
        """初始化模型"""
        try:
            analyzer.initialize()
            self.status_label = QLabel("模型初始化完成，请选择图片进行分析。")
        except Exception as e:
            self.status_label = QLabel(f"模型初始化失败：{str(e)}")

    def initUI(self):
        self.setWindowTitle('诗画意境')  # 更改标题
        self.setGeometry(100, 100, 1000, 800)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # 增加控件间距
        main_layout.setContentsMargins(30, 30, 30, 30)  # 增加边距

        # 创建图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        main_layout.addWidget(self.image_label)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # 按钮间距
        self.select_button = QPushButton('选择图片')
        self.analyze_button = QPushButton('分析图片')
        self.analyze_button.setEnabled(False)
        self.confirm_keywords_button = QPushButton('创作诗词')
        self.confirm_keywords_button.setEnabled(False)
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.confirm_keywords_button)
        main_layout.addLayout(button_layout)

        # 添加状态标签
        main_layout.addWidget(self.status_label)

        # 创建关键词按钮的滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(100)
        self.keywords_widget = QWidget()
        self.keywords_layout = QHBoxLayout(self.keywords_widget)
        self.keywords_layout.setAlignment(Qt.AlignLeft)  # 关键词左对齐
        self.scroll.setWidget(self.keywords_widget)
        main_layout.addWidget(self.scroll)

        # 连接信号
        self.select_button.clicked.connect(self.select_image)
        self.analyze_button.clicked.connect(self.analyze_image)
        self.confirm_keywords_button.clicked.connect(self.create_poem)

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
        self.selected_keywords.clear()  # 清除选中的关键词记录
        self.confirm_keywords_button.setEnabled(False)

    def create_keyword_button(self, keyword):
        """创建关键词按钮"""
        button = KeywordButton(keyword)
        button.clicked.connect(lambda: self.keyword_clicked(button))
        return button

    def keyword_clicked(self, button):
        """处理关键词按钮点击事件"""
        button.selected = button.isChecked()
        button.update_style()
        
        if button.selected:
            self.selected_keywords.add(button.keyword)
        else:
            self.selected_keywords.discard(button.keyword)
        
        # 更新状态标签显示所有选中的关键词
        if self.selected_keywords:
            selected_text = "已选中: " + ", ".join(sorted(self.selected_keywords))
            self.status_label.setText(selected_text)
        else:
            self.status_label.setText("未选中任何关键词")
        
        # 启用/禁用确定关键词按钮
        self.confirm_keywords_button.setEnabled(len(self.selected_keywords) > 0)

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
        
        try:
            # 解析关键词字符串并创建按钮
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

    def create_poem(self):
        """处理诗歌创作流程"""
        if not self.selected_keywords:
            self.status_label.setText("请先选择关键词")
            return

        # 显示诗歌类型选择对话框
        dialog = PoemTypeDialog(self)
        if dialog.exec_():
            poem_type = dialog.get_selected_type()
            if poem_type:
                self.status_label.setText(f"正在创作{poem_type}...")
                try:
                    # 创建诗歌
                    poem = analyzer.create_poem(self.selected_keywords, poem_type)
                    # 显示诗歌
                    display_dialog = PoemDisplayDialog(poem, self)
                    display_dialog.exec_()
                    self.status_label.setText("诗歌创作完成")
                except Exception as e:
                    self.status_label.setText(f"诗歌创作失败：{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ImageAnalyzerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 