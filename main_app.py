from src.extract_text import extract_text_from_pdf
from src.word_filter import preprocess_and_count
from src.merge_csv import merge_csv_to_master
from collections import Counter
import pandas as pd

import os



def aggregate_word_freq(master_counter, word_freq):
    master_counter.update(word_freq)  # Cộng thêm từ vựng vào Counter chung
    return master_counter

# ====== 4. Xử lý toàn bộ folder và gộp vào 1 file CSV ======
def process_pdf_to_csv(folder_path, output_folder, max_pages=None):
    """
    Xử lý từng file PDF trong thư mục, và lưu ra file CSV riêng tương ứng.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"\n📘 Đang xử lý: {filename}")

            raw_text = extract_text_from_pdf(pdf_path, max_pages=max_pages)
            word_freq = preprocess_and_count(raw_text)

            df = pd.DataFrame(word_freq.items(), columns=["Word", "Frequency"])
            df.sort_values(by="Frequency", ascending=False, inplace=True)

            # Tạo tên file CSV giống tên PDF
            base_name = os.path.splitext(filename)[0]
            output_csv = os.path.join(output_folder, f"{base_name}.csv")
            df.to_csv(output_csv, index=False)
            print(f"✅ Đã lưu từ vựng ra: {output_csv}")

    # ====== 5. Main chạy chính ======
if __name__ == "__main__":
    input_folder = "./data/pdfs"         # ← Folder chứa tất cả sách PDF CAM
    output_file = "./data/outputs"      # ← Nơi xuất CSV
    master_file = "./data/master/master.csv"
    process_pdf_to_csv(input_folder, output_file, max_pages=10)  # ← test 10 trang đầu
    merge_csv_to_master(output_file, master_file)