import os
import re
from collections import Counter
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QFileDialog
)
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from nltk.corpus import wordnet as wn

# Thiết lập pytesseract
possible_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
]
for path in possible_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

class PDFProcessorThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, pdf_path, master_file, output_csv, vi_dict_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.master_file = master_file
        self.output_csv = output_csv
        self.vi_dict_path = vi_dict_path

    def run(self):
        self.update_signal.emit(f"📥 Nhận PDF: {self.pdf_path}")
        vi_dict = self.load_vi_dict_from_txt(self.vi_dict_path)
        master_df = self.initialize_master_file(self.master_file)

        self.update_signal.emit("🔍 Bắt đầu OCR PDF...")
        text = self.extract_text_from_image_pdf(self.pdf_path)
        self.update_signal.emit("✅ Hoàn tất OCR")

        self.update_signal.emit("📊 Đang lọc từ vựng...")
        words = self.clean_and_tokenize(text, vi_dict)
        vocab_df = self.analyze_vocab(words)

        self.update_signal.emit("🔄 So sánh với master.csv...")
        vocab_df = vocab_df[~vocab_df['word'].isin(master_df['word'])]

        self.update_signal.emit("📊 Đang enrich từ vựng...")
        word_details = self.get_word_details(vocab_df['word'].tolist(), vi_dict)
        details_df = pd.DataFrame(word_details)

        master_df = pd.concat([master_df, details_df], ignore_index=True)
        master_df.to_csv(self.master_file, index=False)

        if not details_df.empty and 'word' in details_df.columns:
            vocab_df = vocab_df.join(details_df.set_index('word'), on='word')
            vocab_df = vocab_df.drop(columns=['frequency'])

        self.save_to_csv(vocab_df, self.output_csv)
        self.update_signal.emit("✅ Đã hoàn tất quá trình xử lý!")

    def extract_text_from_image_pdf(self, pdf_path, max_pages=10):
        self.update_signal.emit("📄 Đang chuyển đổi PDF thành ảnh...")
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
        self.update_signal.emit("📝 Bắt đầu OCR từng trang...")
        texts = []
        for i, img in enumerate(images):
            self.update_signal.emit(f"🔠 OCR trang {i+1}/{len(images)}")
            texts.append(pytesseract.image_to_string(img))
        return " ".join(texts).strip()


    def clean_and_tokenize(self, text, vi_dict):
        text = text.lower()
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return [w for w in words if len(w) > 2 and w in vi_dict]

    def analyze_vocab(self, words):
        counter = Counter(words)
        df = pd.DataFrame(counter.items(), columns=['word', 'frequency'])
        return df.sort_values(by="frequency", ascending=False).reset_index(drop=True)

    def get_word_details(self, words, vi_dict):
        results = []
        for word in words:
            synsets = wn.synsets(word)
            if not synsets:
                results.append({'word': word, 'meaning': '', 'part_of_speech': '', 'examples': '', 'phonetic': '', 'meaning_vi': vi_dict.get(word.lower(), '')})
                continue

            syn = synsets[0]
            results.append({
                'word': word,
                'meaning': syn.definition(),
                'part_of_speech': syn.pos(),
                'examples': "\n".join(syn.examples()[:3]),
                'phonetic': syn.lemmas()[0].name(),
                'meaning_vi': vi_dict.get(word.lower(), '')
            })
        return results

    def initialize_master_file(self, path):
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['word', 'meaning', 'part_of_speech', 'examples', 'phonetic', 'meaning_vi'])
            df.to_csv(path, index=False)
            return df

    def save_to_csv(self, df, path):
        df.to_csv(path, index=False)

    def load_vi_dict_from_txt(self, path):
        vi_dict = {}
        current_word, current_def = "", []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("|"):
                    if current_word and current_def:
                        vi_dict[current_word.lower()] = "\n+) " + "\n+) ".join(current_def)
                    current_word, current_def = line[1:].strip(), []
                elif line.startswith("-") or line.startswith("+"):
                    current_def.append(line[1:].strip())
            if current_word and current_def:
                vi_dict[current_word.lower()] = "\n+) " + "\n+) ".join(current_def)
        return vi_dict

class ProcessApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.processor_thread = None

    def init_ui(self):
        self.top_label = QLabel("📂 Chọn file từ vựng:", self)
        self.btnstart = QPushButton("Bắt đầu", self)
        self.btn_choose_file = QPushButton("Chọn file", self)

        self.btnstart.clicked.connect(self.start)
        self.btn_choose_file.clicked.connect(self.choose_file)

        layout = QVBoxLayout()
        layout.addWidget(self.top_label)
        layout.addWidget(self.btnstart)
        layout.addWidget(self.btn_choose_file)
        self.setLayout(layout)

    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn file PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.pdf_path = file_name
            self.top_label.setText(f"📄 Đã chọn: {os.path.basename(file_name)}")

    def start(self):
        if not hasattr(self, 'pdf_path'):
            self.top_label.setText("⚠️ Bạn chưa chọn file PDF!")
            return

        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        datas_folder = os.path.join(basedir, 'datas')
        os.makedirs(datas_folder, exist_ok=True)

        master_file = os.path.join(datas_folder, 'master.csv')
        vi_dict_path = os.path.join(datas_folder, 'data.txt')
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        output_csv = os.path.join(datas_folder, f"{base_name}.csv")

        self.processor_thread = PDFProcessorThread(
            self.pdf_path, master_file, output_csv, vi_dict_path
        )
        self.processor_thread.update_signal.connect(self.top_label.setText)
        self.processor_thread.start()
