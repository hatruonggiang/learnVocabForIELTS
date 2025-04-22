import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,QHBoxLayout, QLabel,
    QFileDialog, QTextEdit,QFrame,QTableWidget,QTableWidgetItem,QStackedWidget,QStyleFactory
)
from PyQt5.QtCore import Qt
import pandas as pd
from games.flashcard.app import FlashcardApp
from games.quiz.app import QuizApp
from src.data import DataManager

class VocabApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocabulary Extractor")
        self.setGeometry(100, 100, 1000, 400)
        self.label = QLabel(self)  # Khởi tạo thuộc tính label
        self.init_ui()

        self.layout = QVBoxLayout()

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

        self.label = QLabel("Chào mừng đến với ứng dụng lọc từ PDF!")

        # === QTableWidget để hiển thị kết quả ===
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)  # 4 cột: word, meaning, meaning VN, example
        self.table_widget.setHorizontalHeaderLabels(["Word", "Meaning", "Meaning VN", "Example"])

        # Cài đặt layout cho content
        self.content_layout.addWidget(self.label)
        self.content_layout.addWidget(self.table_widget)

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
        self.setGeometry(100, 100, 800, 600)  # Kích thước cửa sổ ban đầu

    def open_data_manager(self):
    # Xóa widget cũ trong content layout
        for i in reversed(range(self.content_layout.count())):
            widget_to_remove = self.content_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Tạo DataManager và chèn vào layout
        self.data_manager = DataManager()
        self.content_layout.addWidget(self.data_manager)

    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn file PDF", "", "PDF files (*.pdf)")
        if file_name:
            # Tạo thư mục nếu chưa tồn tại
            dest_dir = os.path.join("data", "pdfs")
            os.makedirs(dest_dir, exist_ok=True)

            # Copy file vào thư mục data/pdfs/
            base_name = os.path.basename(file_name)
            dest_path = os.path.join(dest_dir, base_name)
            shutil.copy(file_name, dest_path)

            self.pdf_path = dest_path
            self.label.setText(f"Đã tải vào: {dest_path}")

    def process_pdf(self):
        self.label.setText("Đang xử lý, vui lòng chờ...")

        try:
            from src.make_word_from_pdf import process_pdf,load_vi_dict_from_txt  # Đảm bảo tên hàm này đúng với file bạn có

            input_folder = "data/pdfs"
            output_folder = "data/outputs"
            master_file = "data/master.csv"

            os.makedirs(output_folder, exist_ok=True)  # Đảm bảo thư mục tồn tại

            vocab_list = []

            for filename in os.listdir(input_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(input_folder, filename)
                    base_name = os.path.splitext(filename)[0]
                    output_csv = os.path.join(output_folder, f"{base_name}.csv")
                    vi_dict_path = "data/pdfs/data.txt"

                    if not os.path.exists(output_csv):
                        print(f"\n🚀 Đang xử lý: {filename}")
                        vocab_list = process_pdf(pdf_path, master_file, output_csv, vi_dict_path)
                    else:
                        print(f"⏭️ Bỏ qua (đã có CSV): {filename}")

                        
            
            self.table_widget.clearContents()  # Xóa dữ liệu cũ trong bảng
            self.table_widget.setRowCount(0)  # Đặt lại số dòng
            
            
            if vocab_list.empty:
                print("Không có dữ liệu.")
            else:
                print(f"Dữ liệu có {len(vocab_list)} từ vựng.")

            if not vocab_list.empty:
                self.label.setText("✅ Đã xử lý xong.")
                for idx, row in vocab_list.iterrows():
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)

                    def make_item(text):
                        item = QTableWidgetItem(str(text))
                        item.setToolTip(str(text))  # Hiện toàn bộ khi hover
                        item.setTextAlignment(Qt.AlignTop)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        return item

                    self.table_widget.setItem(row_position, 0, make_item(row['word']))
                    self.table_widget.setItem(row_position, 1, make_item(row['meaning']))
                    self.table_widget.setItem(row_position, 2, make_item(row['meaning_vi']))
                    self.table_widget.setItem(row_position, 3, make_item(row['examples']))

                # Tự động giãn kích thước phù hợp nội dung
                # self.table_widget.resizeColumnsToContents()
                self.table_widget.resizeRowsToContents()

            else:
                self.label.setText("ℹ️ Không có từ vựng mới.")

        except Exception as e:
            self.label.setText(f"❌ Lỗi: {str(e)}")

        except Exception as e:
            self.label.setText(f"❌ Lỗi: {str(e)}")
    
    def show_flashcard(self):
        # Xóa tất cả widget hiện tại trong content_layout
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Thêm giao diện Flashcard vào content_layout
        self.flashcard_app = FlashcardApp(self)
        self.content_layout.addWidget(self.flashcard_app)

    def show_quiz(self):
        # Xóa tất cả widget hiện tại trong content_layout
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Thêm giao diện Flashcard vào content_layout
        vocab_csv = "data/outputs/sample.csv"  # hoặc file cụ thể bạn muốn chơi
        self.quiz_app = QuizApp(vocab_csv)
        self.quiz_app.show()
        self.content_layout.addWidget(self.quiz_app)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create("Fusion"))
    style_path = os.path.join(os.path.dirname(__file__), "styles", "main.qss")
    with open(style_path, "r", encoding ="utf-8") as f:
        app.setStyleSheet(f.read())
    window = VocabApp()
    window.show()
    sys.exit(app.exec_())
