import sys
import random
import pandas as pd
import os
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication,
    QMessageBox, QComboBox, QHBoxLayout,QListView
)



class FlashcardApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vocab_list = []
        self.df = None
        self.current_word = ""
        self.init_ui()
        self.apply_flashcard_style()  # Áp dụng QSS riêng cho Flashcard

    def init_ui(self):
        self.top_labbel = QLabel("📂 Chọn file từ vựng:",self)
        self.word_label = QLabel("", self)
        self.toggle_button = QPushButton("Hiện nghĩa", self)
        self.next_button = QPushButton("Tiếp", self)
        self.remember_button = QPushButton("✓ Nhớ", self)
        self.forget_button = QPushButton("✗ Quên", self)
        self.file_combo = QComboBox(self)

        self.meaning_label = QListView(self)
        self.model = QStringListModel()  # Dùng QStringListModel để quản lý danh sách nghĩa
        self.meaning_label.setModel(self.model)

        # Tắt các nút khi chưa có dữ liệu
        for btn in [self.toggle_button, self.next_button, self.remember_button, self.forget_button]:
            btn.setEnabled(False)
        self.meaning_label.setVisible(False)

        # Load danh sách file từ data/outputs
        self.load_csv_files()
        self.file_combo.currentIndexChanged.connect(self.load_selected_csv)
        self.toggle_button.clicked.connect(self.toggle_meaning)
        self.next_button.clicked.connect(self.show_random_card)
        self.remember_button.clicked.connect(lambda: self.update_count(remembered=True))
        self.forget_button.clicked.connect(lambda: self.update_count(remembered=False))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.top_labbel)
        layout.addWidget(self.file_combo)
        layout.addWidget(self.word_label)
        layout.addWidget(self.meaning_label)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.next_button)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.forget_button)
        btn_row.addWidget(self.remember_button)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.setWindowTitle("📘 Flashcard Học Từ Vựng")

    def load_csv_files(self):
        folder = "data/outputs"
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.endswith(".csv")]
            self.file_combo.addItems(files)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy thư mục {folder}")

    def load_selected_csv(self):
        filename = self.file_combo.currentText()
        if not filename:
            return
        path = os.path.join("data/outputs", filename)
        if os.path.exists(path):
            try:
                self.df = pd.read_csv(path)
                if 'word' not in self.df.columns or 'meaning_vi' not in self.df.columns:
                    QMessageBox.warning(self, "Sai định dạng", "File CSV phải có cột 'word' và 'meaning_vi'.")
                    return
                if 'count' not in self.df.columns:
                    self.df['count'] = 0
                self.vocab_list = self.df.to_dict('records')
                for btn in [self.toggle_button, self.next_button, self.remember_button, self.forget_button]:
                    btn.setEnabled(True)
                self.show_random_card()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file CSV: {str(e)}")

    def show_random_card(self):
        if not self.vocab_list:
            self.word_label.setText("Không có từ vựng.")
            return

        # Ưu tiên từ có count thấp
        self.vocab_list.sort(key=lambda x: x.get('count', 0))
        selected = random.choice(self.vocab_list[:min(10, len(self.vocab_list))])
        self.current_word = selected['word']

        word = selected['word']
        meaning = selected.get('meaning_vi', '(Không có nghĩa)')

        # Hiển thị từ
        self.word_label.setText(f"<h2>{word}</h2>")

        # Cập nhật nghĩa vào model của QListView
        self.model.setStringList([meaning])  # Đưa nghĩa vào danh sách
        self.meaning_label.setVisible(False)  # Ban đầu không hiển thị nghĩa
        self.toggle_button.setText("Hiện nghĩa")


    def toggle_meaning(self):
        if self.meaning_label.isVisible():
            self.meaning_label.setVisible(False)
            self.toggle_button.setText("Hiện nghĩa")
        else:
            # Lấy nghĩa và ví dụ
            word_data = next((item for item in self.vocab_list if item['word'] == self.current_word), {})
            meaning = word_data.get('meaning_vi', '(Không có nghĩa)')
            example = word_data.get('examples', '')
            
            text = [meaning]
            if example:
                text.append(f"💬 {example}")  # Thêm ví dụ vào danh sách

            self.model.setStringList(text)  # Cập nhật danh sách nghĩa trong model
            self.meaning_label.setVisible(True)  # Hiển thị nghĩa
            self.toggle_button.setText("Ẩn nghĩa")



    def update_count(self, remembered=True):
        word = self.current_word
        idx = self.df[self.df['word'] == word].index
        if not idx.empty:
            i = idx[0]
            self.df.at[i, 'count'] = self.df.at[i, 'count'] + (1 if remembered else -2)
            # Ghi lại file
            self.df.to_csv(os.path.join("data/outputs", self.file_combo.currentText()), index=False)
            # Cập nhật vocab_list
            self.vocab_list = self.df.to_dict('records')
        self.show_random_card()
    
    def apply_flashcard_style(self):
        style_path = os.path.join(os.path.dirname(__file__), "../../styles/flashcard.qss")

        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec_())
