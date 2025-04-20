import os
import pandas as pd
from collections import Counter

def merge_csv_to_master(csv_folder, output_file):
    """
    Gộp tất cả các file CSV trong thư mục thành một file master.
    Cộng tần suất của các từ trùng nhau.
    """
    master_counter = Counter()

    for filename in os.listdir(csv_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(csv_folder, filename)
            print(f"📥 Đang gộp file: {filename}")
            df = pd.read_csv(file_path)

            for _, row in df.iterrows():
                word = row["Word"]
                freq = int(row["Frequency"])
                master_counter[word] += freq

    # Tạo DataFrame từ kết quả gộp
    master_df = pd.DataFrame(master_counter.items(), columns=["Word", "Frequency"])
    master_df.sort_values(by="Frequency", ascending=False, inplace=True)

    # Lưu ra file master
    master_df.to_csv(output_file, index=False)
    print(f"\n✅ Đã lưu từ vựng tổng hợp vào: {output_file}")
