import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,QHBoxLayout, QLabel,
    QFileDialog, QTextEdit,QFrame,QTableWidget,QTableWidgetItem,
)
from PyQt5.QtCore import Qt
import pandas as pd

class VocabApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocabulary Extractor")
        self.setGeometry(100, 100, 1000, 400)

        self.init_ui()

        self.layout = QVBoxLayout()

    def init_ui(self):
            # Layout chính: chia dọc (sidebar trái, content phải)
            main_layout = QHBoxLayout(self)

            # === Sidebar trái ===
            self.sidebar = QFrame()
            self.sidebar.setFixedWidth(200)
            self.sidebar.setStyleSheet("background-color: #f0f0f0;")
            sidebar_layout = QVBoxLayout(self.sidebar)

            # Các nút trên sidebar
            self.btn_data = QPushButton("📂 Menu Data")
            self.btn_upload = QPushButton("📤 Upload PDF")
            self.btn_process = QPushButton("⚙️ Xử lý")

            # Thêm nút vào layout
            for btn in [self.btn_data, self.btn_upload, self.btn_process]:
                btn.setMinimumHeight(40)
                sidebar_layout.addWidget(btn)

            sidebar_layout.addStretch()  # Đẩy nút lên đầu

            # === Content chính bên phải ===
            self.content = QFrame()
            content_layout = QVBoxLayout(self.content)

            self.label = QLabel("Chào mừng đến với ứng dụng lọc từ PDF!")

            # === QTableWidget để hiển thị kết quả ===
            self.table_widget = QTableWidget(self)
            self.table_widget.setColumnCount(4)  # 4 cột: word, meaning, meaning VN, example
            self.table_widget.setHorizontalHeaderLabels(["Word", "Meaning", "Meaning VN", "Example"])

            content_layout.addWidget(self.label)
            content_layout.addWidget(self.table_widget)

            main_layout.addWidget(self.sidebar)
            main_layout.addWidget(self.content)

            # Kết nối các nút
            self.btn_upload.clicked.connect(self.choose_file)
            self.btn_process.clicked.connect(self.process_pdf)
            self.pdf_path = None

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



            if not vocab_list.empty:  # ✅ Đúng cách để kiểm tra DataFrame có dữ liệu không
                self.label.setText("✅ Đã xử lý xong.")
                # Điền dữ liệu vào bảng
                for idx, row in vocab_list.iterrows():  # ✅ Duyệt từng dòng trong DataFrame
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)

                    word_item = QTableWidgetItem(str(row['word']))
                    meaning_item = QTableWidgetItem(str(row['meaning']))
                    meaning_vn_item = QTableWidgetItem(str(row['meaning_vi']))
                    example_item = QTableWidgetItem(str(row['examples']))

                    self.table_widget.setItem(row_position, 0, word_item)
                    self.table_widget.setItem(row_position, 1, meaning_item)
                    self.table_widget.setItem(row_position, 2, meaning_vn_item)
                    self.table_widget.setItem(row_position, 3, example_item)

            else:
                self.label.setText("ℹ️ Không có từ vựng mới.")

        except Exception as e:
            self.label.setText(f"❌ Lỗi: {str(e)}")

        except Exception as e:
            self.label.setText(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VocabApp()
    window.show()
    sys.exit(app.exec_())
