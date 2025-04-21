import sys
import random
import pandas as pd
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QApplication,
    QMessageBox, QComboBox, QHBoxLayout
)

class QuizApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vocab_list = []
        self.df = None
        self.current_word = ""
        self.init_ui()

    def init_ui(self):
        self.question_label = QLabel("Câu hỏi sẽ hiển thị ở đây", self)
        self.option_buttons = [QPushButton("", self) for _ in range(4)]  # Tạo 4 nút cho đáp án
        self.file_combo = QComboBox(self)

        # Tắt các nút khi chưa có dữ liệu
        for btn in self.option_buttons:
            btn.setEnabled(False)

        # Load danh sách file từ data/outputs
        self.load_csv_files()
        self.file_combo.currentIndexChanged.connect(self.load_selected_csv)

        # Các nút đáp án
        for btn in self.option_buttons:
            btn.clicked.connect(self.check_answer)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📂 Chọn file từ vựng:", self))
        layout.addWidget(self.file_combo)
        layout.addWidget(self.question_label)

        for btn in self.option_buttons:
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setWindowTitle("📚 Trắc nghiệm Học Từ Vựng")

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
                self.show_question()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file CSV: {str(e)}")

    def show_question(self):
        if not self.vocab_list:
            self.question_label.setText("Không có từ vựng.")
            return

        # Chọn một từ ngẫu nhiên
        selected = random.choice(self.vocab_list)
        self.current_word = selected['word']
        correct_answer = selected['meaning_vi']

        # Tạo câu hỏi và các đáp án ngẫu nhiên
        self.question_label.setText(f"<h2>{self.current_word}</h2>")
        answers = [correct_answer] + self.get_random_answers(correct_answer)
        random.shuffle(answers)

        # Cập nhật các đáp án vào các nút
        for i, btn in enumerate(self.option_buttons):
            btn.setText(answers[i])
            btn.setEnabled(True)

    def get_random_answers(self, correct_answer):
        # Lấy 3 đáp án sai ngẫu nhiên từ từ vựng
        wrong_answers = [item['meaning_vi'] for item in self.vocab_list if item['meaning_vi'] != correct_answer]
        return random.sample(wrong_answers, 3)

    def check_answer(self):
        selected_answer = self.sender().text()
        correct_answer = next(item for item in self.vocab_list if item['word'] == self.current_word)['meaning_vi']

        if selected_answer == correct_answer:
            QMessageBox.information(self, "Đúng!", "Bạn đã chọn đúng!")
        else:
            QMessageBox.warning(self, "Sai!", "Bạn đã chọn sai!")

        # Cập nhật số lần trả lời đúng/sai
        self.update_count(selected_answer == correct_answer)

        # Hiển thị câu hỏi tiếp theo
        self.show_question()

    def update_count(self, correct=True):
        word = self.current_word
        idx = self.df[self.df['word'] == word].index
        if not idx.empty:
            i = idx[0]
            self.df.at[i, 'count'] = self.df.at[i, 'count'] + (1 if correct else -1)
            # Ghi lại file
            self.df.to_csv(os.path.join("data/outputs", self.file_combo.currentText()), index=False)
            # Cập nhật vocab_list
            self.vocab_list = self.df.to_dict('records')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.show()
    sys.exit(app.exec_())
