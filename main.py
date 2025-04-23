import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,QHBoxLayout, QLabel,
    QFileDialog, QTextEdit,QFrame,QTableWidget,QTableWidgetItem,QStackedWidget,QStyleFactory
)
from PyQt6.QtCore import Qt
import pandas as pd
from src.flashcard import FlashcardApp
# from games.quiz.app import QuizApp
from src.data import DataManager
from src.make_word_form_pdf import ProcessApp
from PyQt6.QtCore import QThread
from src.worker import GenericWorker

class VocabApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocabulary Extractor")
        self.setGeometry(100, 100, 1400, 400)
        self.label = QLabel(self)  # Khởi tạo thuộc tính label
        self.init_ui()

        self.layout = QVBoxLayout()
        self.current_widget = None
        self.show_welcome()



    def init_ui(self):
        # Layout chính: chia dọc (sidebar trái, content phải)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Thêm margin để không dính vào viền

        # === Sidebar trái ===
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Các nút trên sidebar
        self.btn_data = QPushButton("📂 Menu Data")
        self.btn_upload = QPushButton("📤 Upload PDF")
        self.btn_process = QPushButton("⚙️ Xử lý")
        self.btn_flashcard = QPushButton("📚 Flashcard")
        self.btn_quiz = QPushButton("🎮 Quiz")



        # Thêm nút vào layout
        for btn in [self.btn_data, self.btn_upload, self.btn_process, self.btn_flashcard,self.btn_quiz]:
            btn.setMinimumHeight(40)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()  # Đẩy nút lên đầu

        # === Content chính bên phải ===
        self.content = QFrame()
        self.content_layout = QVBoxLayout(self.content)

        # self.label = QLabel("Chào mừng đến với ứng dụng lọc từ PDF!")

        # === QTableWidget để hiển thị kết quả ===
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)  # 4 cột: word, meaning, meaning VN, example
        self.table_widget.setHorizontalHeaderLabels(["Word", "Meaning", "Meaning VN", "Example"])


        # Thêm phần sidebar và content vào layout chính
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content)

        # Kết nối các nút
        self.btn_data.clicked.connect(self.open_data_manager)
        self.btn_upload.clicked.connect(self.choose_file)
        self.btn_process.clicked.connect(self.process_pdf)
        self.btn_flashcard.clicked.connect(self.show_flashcard)
        self.btn_quiz.clicked.connect(self.show_quiz)

        self.pdf_path = None
        self.setLayout(main_layout)

        # Thiết lập kích thước cửa sổ ban đầu
        self.setWindowTitle("Ứng Dụng Lọc Từ Vựng")
        self.setGeometry(100, 100, 1000, 600)  # Kích thước cửa sổ ban đầu
    
    def resource_path(relative_path):
        """ Trả về đường dẫn đúng trong chế độ chạy .exe hoặc khi debug """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def clear_content_layout(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                # Nếu là layout lồng nhau
                sub_layout = item.layout()
                if sub_layout is not None:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.setParent(None)
                            sub_widget.deleteLater()


    def switch_feature(self, new_widget):
        # Dừng widget cũ nếu cần
        if self.current_widget and hasattr(self.current_widget, 'stop'):
            self.current_widget.stop()

        # Xóa sạch layout
        self.clear_content_layout()

        # Thêm widget mới vào
        self.content_layout.addWidget(new_widget)
        self.current_widget = new_widget

    def show_welcome(self):
        self.clear_content_layout()

        label = QLabel("Chào mừng đến với ứng dụng lọc từ PDF!")
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Word", "Meaning", "Meaning VN", "Example"])

        self.content_layout.addWidget(label)
        self.content_layout.addWidget(self.table_widget)

        self.current_widget = self.table_widget  # Gán cho tiện dọn nếu cần

    def open_data_manager(self):


        # Tạo DataManager và chèn vào layout
        self.clear_content_layout()
        self.data_manager = DataManager()
        self.content_layout.addWidget(self.data_manager)

    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn file PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.pdf_path = file_name
            self.label.setText(f"Đã chọn file: {file_name}")

    def process_pdf(self):
        self.clear_content_layout()
        self.process_app = ProcessApp(self)
        self.content_layout.addWidget(self.process_app)

    
    def show_flashcard(self):

        # # Thêm giao diện Flashcard vào content_layout
        self.clear_content_layout()
        self.flashcard_app = FlashcardApp(self)
        self.content_layout.addWidget(self.flashcard_app)

    def show_quiz(self):

        # # Thêm giao diện Flashcard vào content_layout
        vocab_csv = "datas/outputs/sample.csv"  # hoặc file cụ thể bạn muốn chơi
        # self.quiz_app = QuizApp(vocab_csv)
        self.quiz_app.show()
        self.content_layout.addWidget(self.quiz_app)

    def resource_path(relative_path):
        """ Trả về đường dẫn đúng trong chế độ chạy .exe hoặc khi debug """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    def run_with_progress(self, func, *args, **kwargs):
        self.thread = QThread()
        self.worker = GenericWorker(func, *args, **kwargs)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.top_label.setText)
        self.worker.finished.connect(self.handle_step_done)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_step_done(self, result):
        self.top_label.setText("✅ Done!")
        print("✔️ Result:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle(QStyleFactory.create("Fusion"))
    abc = "styles/main.qss"
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    styles_folder = os.path.join(basedir, 'styles')

    qss_path = os.path.join(styles_folder, 'main.qss')

    with open(qss_path, "r", encoding ="utf-8") as f:
        app.setStyleSheet(f.read())
    window = VocabApp()
    window.show()
    sys.exit(app.exec())
