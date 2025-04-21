import pandas as pd
import random

def load_vocab_data(csv_path):
    return pd.read_csv(csv_path)

def generate_question(vocab_df):
    # Chọn 1 từ làm câu hỏi
    row = vocab_df.sample(1).iloc[0]
    correct_word = row['meaning_vi']
    correct_meaning = row['word']

    # Chọn 3 nghĩa sai từ các từ khác
    distractors = vocab_df[vocab_df['word'] != correct_word].sample(3)
    choices = [correct_meaning] + distractors['word'].tolist()
    random.shuffle(choices)

    return {
        'question': f"Từ nào có nghĩa là: \"{correct_word}\"?",
        'choices': choices,
        'answer': correct_meaning,
        'word': correct_word
    }
