import sys
import os
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt
from src.utils import TextToSpeechApp

def resource_path(relative_path):
    """Trả về đường dẫn chính xác cho các tài nguyên, xử lý trường hợp ứng dụng chạy dưới dạng .exe"""
    try:
        if hasattr(sys, '_MEIPASS'):
            # Đường dẫn khi ứng dụng đã được đóng gói thành .exe
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Đường dẫn trong môi trường phát triển
            return os.path.join(os.getcwd(), relative_path)
    except Exception as e:
        print(f"Error resolving resource path: {e}")
        return None

class DataManager(QWidget):
    def __init__(self):
        super().__init__()

        # Sử dụng resource_path để lấy đường dẫn chính xác đến thư mục 'datas'
        self.csv_dir = resource_path('datas')

        if not self.csv_dir or not os.path.exists(self.csv_dir):
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thư mục 'datas'.")
            return

        layout = QVBoxLayout()
        self.csv_combo = QComboBox()

        # Tạo đối tượng TextToSpeechApp
        self.text_to_speech = TextToSpeechApp()
        self.load_csv_files()

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

        layout.addWidget(QLabel("📄 Chọn file CSV:"))
        layout.addWidget(self.csv_combo)
        layout.addWidget(self.view_csv_button)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        # Phát âm khi click vào từ trong bảng
        self.table_widget.cellClicked.connect(self.on_cell_clicked)

    def load_csv_files(self):
        if not os.path.exists(self.csv_dir):
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thư mục chứa file CSV.")
            return

        # Tải danh sách các file CSV trong thư mục 'datas'
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        self.csv_combo.clear()
        self.csv_combo.addItems(csv_files)

    def on_cell_clicked(self, row, column):
        """Khi người dùng ấn vào ô trong bảng, phát âm từ trong cột 'Word'"""
        if column == 0:  # Cột "Word"
            word = self.table_widget.item(row, column).text()
            print(word)
            self.text_to_speech.speak(word)  # Gọi phương thức phát âm

    def load_selected_csv(self):
        selected_csv = self.csv_combo.currentText()
        if not selected_csv:
            QMessageBox.warning(self, "Lỗi", "Không có file CSV nào được chọn.")
            return

        # Lấy đường dẫn đầy đủ đến file CSV
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