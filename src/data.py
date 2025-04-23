import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import pandas as pd
from src.utils import TextToSpeechApp
from PyQt6.QtWidgets import QHeaderView,QSizePolicy

class DataManager(QWidget):
    def __init__(self):
        super().__init__()

        self.pdf_dir = 'data/pdfs'
        self.csv_dir = 'data/outputs'

        layout = QVBoxLayout()

        self.pdf_combo = QComboBox()
        self.csv_combo = QComboBox()
        
        # Tạo đối tượng TextToSpeechApp
        self.text_to_speech = TextToSpeechApp()
        self.load_pdf_files()
        self.load_csv_files()

        # Nút xoá file PDF đã chọn
        self.remove_pdf_button = QPushButton("🗑️ Xóa PDF đã chọn")
        self.remove_pdf_button.clicked.connect(self.remove_selected_pdf)

        # Nút hiển thị CSV
        self.view_csv_button = QPushButton("📄 Xem dữ liệu CSV")
        self.view_csv_button.clicked.connect(self.load_selected_csv)

        # Bảng hiển thị CSV
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Word", "Meaning", "Meaning VN", "Example"])

        # Dãn đều các cột theo chiều ngang
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Hàng tự dãn theo nội dung
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Cho phép bảng chiếm toàn bộ không gian layout
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(QLabel("📂 Chọn file PDF:"))
        layout.addWidget(self.pdf_combo)
        layout.addWidget(self.remove_pdf_button)
        layout.addSpacing(10)

        layout.addWidget(QLabel("📄 Chọn file CSV:"))
        layout.addWidget(self.csv_combo)
        layout.addWidget(self.view_csv_button)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        # Phát âm khi click vào từ trong bảng
        self.table_widget.cellClicked.connect(self.on_cell_clicked)

    def load_pdf_files(self):
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        self.pdf_combo.clear()
        self.pdf_combo.addItems(pdf_files)

    def load_csv_files(self):
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        self.csv_combo.clear()
        self.csv_combo.addItems(csv_files)


    def on_cell_clicked(self, row, column):
        """Khi người dùng ấn vào ô trong bảng, phát âm từ trong cột 'Word'"""
        if column == 0:  # Cột "Word"
            word = self.table_widget.item(row, column).text()
            print(word)
            self.text_to_speech.speak(word, use_online=False)  # Gọi phương thức phát âm

    def remove_selected_pdf(self):
        selected_pdf = self.pdf_combo.currentText()
        if not selected_pdf:
            QMessageBox.warning(self, "Lỗi", "Không có file PDF nào được chọn.")
            return

        reply = QMessageBox.question(
            self, "Xác nhận xoá",
            f"Bạn có chắc muốn xoá file '{selected_pdf}' không?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            file_path = os.path.abspath(os.path.join(self.pdf_dir, selected_pdf))
            try:
                os.remove(file_path)
                QMessageBox.information(self, "Thành công", f"Đã xoá {selected_pdf}")
                self.load_pdf_files()  # Cập nhật lại danh sách
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xoá file: {e}")

    def load_selected_csv(self):
        selected_csv = self.csv_combo.currentText()
        if not selected_csv:
            QMessageBox.warning(self, "Lỗi", "Không có file CSV nào được chọn.")
            return

        csv_path = os.path.abspath(os.path.join(self.csv_dir, selected_csv))
        try:
            df = pd.read_csv(csv_path)
            self.table_widget.setRowCount(0)

            for idx, row in df.iterrows():
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)

                def make_item(text):
                    item = QTableWidgetItem(str(text))
                    item.setToolTip(str(text))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignTop)
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    return item

                self.table_widget.setItem(row_position, 0, make_item(row['word']))
                self.table_widget.setItem(row_position, 1, make_item(row['meaning']))
                self.table_widget.setItem(row_position, 2, make_item(row['meaning_vi']))
                self.table_widget.setItem(row_position, 3, make_item(row['examples']))

            self.table_widget.resizeRowsToContents()
            self.table_widget.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file CSV: {e}")
