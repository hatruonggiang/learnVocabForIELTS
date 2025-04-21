import os
from pdf2image import convert_from_path
import pytesseract
import nltk
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import string
import re
from nltk.corpus import words as nltk_words
from nltk.corpus import wordnet as wn

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

print("Tải xuống tài nguyên hoàn tất.")

# Cấu hình Tesseract nếu cần (nếu đã thêm vào PATH thì không cần)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# đã xong - cấm sửa: chuyển 1 pdf sang dạng ảnh, rồi dùng OCR để đọc pdf
def extract_text_from_image_pdf(pdf_path, max_pages=10):
    print(f"📄 Converting up to {max_pages} pages to images...")
    images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
    text = ""
    for i, img in enumerate(images):
        print(f"🔍 OCR page {i+1}/{len(images)}...")
        text += pytesseract.image_to_string(img)
    return text.strip()

# đã xong - cấm sửa: lọc từ scan nhầm bằng cách check xem xong từ điển tiếng anh có nó k, 
def clean_and_tokenize(text, vi_dict_path):
    if not isinstance(vi_dict_path, str):
        raise ValueError(f"Expected string path, got {type(vi_dict_path)}")

    if not os.path.exists(vi_dict_path):
        raise FileNotFoundError(f"File not found: {vi_dict_path}")

    # Load từ điển từ file
    vi_dict = load_vi_dict_from_txt(vi_dict_path)
    english_words_in_dict = set(vi_dict.keys())

    stop_words = set(stopwords.words('english'))
    text = text.lower()

    words = re.findall(r'\b[a-zA-Z]+\b', text)

    filtered_words = []
    for word in words:
        if len(word) > 2 and word not in stop_words:
            if word in english_words_in_dict and len(word) == len(word.strip()):
                filtered_words.append(word)


    print(f"✅ Từ giữ lại: {filtered_words}")


    return filtered_words






# đã xong - cấm sửa: xếp loại các từ theo tần xuất xuất hiện trong file
def analyze_vocab(words):
    counter = Counter(words)
    vocab_list = list(counter.items())
    df = pd.DataFrame(vocab_list, columns=['word', 'frequency'])
    df = df.sort_values(by="frequency", ascending=False).reset_index(drop=True)
    return df



# dịch tiếng anh sang tiếng việt
def load_vi_dict_from_txt(file_path: str) -> dict:
    vi_dict = {}
    current_word = ""
    current_def = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|"):  # Dòng mới bắt đầu với từ mới
                if current_word and current_def:
                    # Ghép nghĩa theo định dạng "+) nghĩa" trước khi lưu
                    meaning_str = "\n+) " + "\n+) ".join(current_def[:3])  # Giới hạn 3 nghĩa
                    vi_dict[current_word.lower()] = meaning_str.strip()
                current_word = line[1:].strip()
                current_def = []
            elif line.startswith("-") or line.startswith("+"):
                current_def.append(line[1:].strip())
        
        # Đừng quên lưu từ cuối cùng
        if current_word and current_def:
            meaning_str = "\n+) " + "\n+) ".join(current_def[:3])  # Giới hạn 3 nghĩa
            vi_dict[current_word.lower()] = meaning_str.strip()
    
    return vi_dict



# thêm nghĩa tiếng anh và 1 vài ví dụ tệ hại, ví dụ xịn thì duyệt lâu lắm, lâu gấp cỡ 5000 lần
def get_word_details(words: list, vi_dict: dict = None) -> list:
    results = []

    for word in words:
        synsets = wn.synsets(word)

        if not synsets:
            results.append({
                'word': word,
                'meaning': '',
                'part_of_speech': '',
                'examples': '',
                'phonetic': '',
                'count': 0,
                'meaning_vi': vi_dict.get(word.lower(), '') if vi_dict else '',
            })
            continue

        meanings = []
        pos_list = set()
        example_sentences = []
        phonetic = synsets[0].lemmas()[0].name()

        for syn in synsets:
            meanings.append(syn.definition())
            pos_list.add(syn.pos())
            example_sentences.extend(syn.examples())  # ✅ dùng extend thay vì append

        meaning_str = "\n+) " + "\n+) ".join(list(meanings)[:1])
        examples_str = "\n+) " + "\n+) ".join(list(example_sentences)[:3])
        pos_str = ", ".join(pos_list)

        results.append({
            'word': word,
            'meaning': meaning_str,
            'part_of_speech': pos_str,
            'examples': examples_str,
            'phonetic': phonetic,
            'count': 0,
            'meaning_vi': vi_dict.get(word.lower(), '') if vi_dict else ''
        })

    return results



# Kiểm tra nếu file master đã tồn tại
def initialize_master_file(master_file):
    try:
        # Nếu file đã tồn tại thì đọc vào
        master_df = pd.read_csv(master_file)
    except FileNotFoundError:
        # Nếu chưa tồn tại, tạo file trống với các cột: word, meaning, part_of_speech, examples
        master_df = pd.DataFrame(columns=['word', 'meaning', 'part_of_speech', 'examples', 'meaning_vi'])
        master_df.to_csv(master_file, index=False)  # Tạo file mới
    return master_df





def save_to_csv(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"✅ Vocabulary saved to: {output_path}")

def process_pdf(pdf_path,master_file, output_csv,vi_dict_path):
    vi_dict = load_vi_dict_from_txt(vi_dict_path)
    master_df = initialize_master_file(master_file)
    text = extract_text_from_image_pdf(pdf_path, 30)
    words = clean_and_tokenize(text, vi_dict_path)
    vocab_df = analyze_vocab(words)
    # vocab_df = vocab_df[~vocab_df['word'].isin(master_df['word'])]
    # Áp dụng hàm get_word_details cho cột 'word' của vocab_df
    word_details = get_word_details(vocab_df['word'].tolist(), vi_dict=vi_dict)

    # Chuyển thông tin chi tiết thành DataFrame
    details_df = pd.DataFrame(word_details)
    master_df = pd.concat([master_df, details_df], ignore_index=True)
    master_df.to_csv(master_file, index=False)

    # Gộp thông tin chi tiết vào vocab_df
    if not details_df.empty and 'word' in details_df.columns:
        vocab_df = vocab_df.join(details_df.set_index('word'), on='word')
        vocab_df = vocab_df.drop(columns=['frequency'])
    else:
        print("⚠️ Không có chi tiết từ vựng để enrich.")
    save_to_csv(vocab_df, output_csv)
    return vocab_df
    