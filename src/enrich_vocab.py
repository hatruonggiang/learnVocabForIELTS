import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.corpus import wordnet as wn
from deep_translator import GoogleTranslator
import nltk
import time

nltk.download('wordnet')

def get_cambridge_data(word):
    url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        ipa = soup.find('span', class_='ipa')
        ipa_text = ipa.text.strip() if ipa else ""

        audio_tag = soup.find('source')
        audio_link = "https://dictionary.cambridge.org" + audio_tag['src'] if audio_tag else ""

        return ipa_text, url if audio_link == "" else audio_link
    except:
        return "", ""

def get_wordnet_info(word):
    synsets = wn.synsets(word)
    if not synsets:
        return "", ""
    first = synsets[0]
    pos = first.pos()
    example = first.examples()[0] if first.examples() else ""
    return pos, example

def translate_word(word):
    try:
        return GoogleTranslator(source='en', target='vi').translate(word)
    except:
        return ""

def enrich_words_from_csv(input_csv, output_excel):
    df = pd.read_csv(input_csv)
    enriched_data = []

    for idx, row in df.iterrows():
        word = row['Word']
        freq = row['Frequency']

        print(f"🔍 Đang xử lý từ: {word} ({idx+1}/{len(df)})")

        ipa, audio_link = get_cambridge_data(word)
        pos, example = get_wordnet_info(word)
        meaning_vi = translate_word(word)

        enriched_data.append({
            "Từ": word,
            "Phát âm (IPA)": ipa,
            "Loại từ": pos,
            "Nghĩa (TV)": meaning_vi,
            "Ví dụ": example,
            "Link phát âm": audio_link,
            "Tần suất": freq
        })

        time.sleep(1.5)  # Tránh bị block khi gọi Cambridge

    enriched_df = pd.DataFrame(enriched_data)
    enriched_df.to_excel(output_excel, index=False)
    print(f"\n✅ Đã lưu kết quả vào: {output_excel}")

# ===== Main =====
if __name__ == "__main__":
    input_csv = "IT.csv"
    output_excel = "IT_enriched.xlsx"
    enrich_words_from_csv(input_csv, output_excel)
