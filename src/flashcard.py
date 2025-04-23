import sys
import random
import pandas as pd
import os
from PyQt6.QtCore import QStringListModel,QTimer
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication,
    QMessageBox, QComboBox, QHBoxLayout,QListView
)
from src.utils import TextToSpeechApp  # Nhập hàm xử lý phát âm từ utils.py

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
class FlashcardApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vocab_list = []
        self.df = None
        self.current_word = ""
        self.init_ui()
        self.apply_flashcard_style()  # Áp dụng QSS riêng cho Flashcard

         # Thiết lập QTimer cho việc phát âm định kỳ
        self.speech_timer = QTimer(self)
        self.speech_timer.setInterval(3000)  # 2 giây
        self.speech_timer.timeout.connect(self.speak_current_word)

    def init_ui(self):
        self.top_labbel = QLabel("📂 Chọn file từ vựng:",self)
        self.word_label = QLabel("", self)
        self.toggle_button = QPushButton("Hiện nghĩa", self)
        self.next_button = QPushButton("Tiếp", self)
        self.remember_button = QPushButton("✓ Nhớ", self)
        self.forget_button = QPushButton("✗ Quên", self)
        self.csv_combo = QComboBox(self)

        self.meaning_label = QListView(self)
        self.model = QStringListModel()  # Dùng QStringListModel để quản lý danh sách nghĩa
        self.text_to_speech = TextToSpeechApp()
        self.meaning_label.setModel(self.model)

        # Tắt các nút khi chưa có dữ liệu
        for btn in [self.toggle_button, self.next_button, self.remember_button, self.forget_button]:
            btn.setEnabled(False)
        self.meaning_label.setVisible(False)


        self.csv_dir = resource_path('datas')
        if not self.csv_dir or not os.path.exists(self.csv_dir):
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thư mục 'datas'.")
            return

        self.is_speaking = False  # Cờ kiểm tra trạng thái phát âm
        # Load danh sách file từ datas
        self.load_csv_files()
        self.csv_combo.currentIndexChanged.connect(self.load_selected_csv)
        self.toggle_button.clicked.connect(self.toggle_meaning)
        self.next_button.clicked.connect(self.show_random_card)
        self.remember_button.clicked.connect(lambda: self.update_count(remembered=True))
        self.forget_button.clicked.connect(lambda: self.update_count(remembered=False))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.top_labbel)
        layout.addWidget(self.csv_combo)
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
        if not os.path.exists(self.csv_dir):
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thư mục chứa file CSV.")
            return

        # Tải danh sách các file CSV trong thư mục 'datas'
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        self.csv_combo.clear()
        self.csv_combo.addItems(csv_files)

    def load_selected_csv(self):
        selected_csv = self.csv_combo.currentText()
        if not selected_csv:
            return
        # path = os.path.abspath(os.path.join("datas", filename))
        path = os.path.abspath(os.path.join(self.csv_dir, selected_csv))
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
        
        self.speak_current_word()
        self.speech_timer.start()



    def toggle_meaning(self):
        if self.meaning_label.isVisible():
            self.meaning_label.setVisible(False)
            self.toggle_button.setText("Hiện nghĩa")
        else:
            # Lấy nghĩa và ví dụ
            word_datas = next((item for item in self.vocab_list if item['word'] == self.current_word), {})
            meaning = word_datas.get('meaning_vi', '(Không có nghĩa)')
            example = word_datas.get('examples', '')
            
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
            file_path = os.path.abspath(os.path.join("datas", self.csv_combo.currentText()))

            # Ghi datasFrame vào tệp CSV
            self.df.to_csv(file_path, index=False)
            # Cập nhật vocab_list
            self.vocab_list = self.df.to_dict('records')
        self.show_random_card()
    
    def apply_flashcard_style(self):
        style_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../styles/flashcard.qss"))

        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

# phát âm
    def speak_current_word(self):
        
        """Phát âm từ hiện tại trong word_label"""
        self.is_speaking = True
        text = self.word_label.text()
        text = text.replace("<h2>", "").replace("</h2>", "")
        print(text)
        self.text_to_speech.speak(text)  # Gọi hàm phát âm từ utils.py            self.is_speaking = False
   
    def stop_speaking(self):
        """Dừng việc phát âm"""
        self.speech_timer.stop()
