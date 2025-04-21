from nltk.corpus import wordnet as wn

def get_word_details(word):
    # Lấy các nghĩa của từ
    synsets = wn.synsets(word)
    
    if not synsets:
        return "Không tìm thấy thông tin cho từ này."
    
    word_details = []
    
    for synset in synsets:
        meaning = synset.definition()  # Nghĩa của từ
        part_of_speech = synset.pos()  # Từ loại (noun, verb, adj, adv)
        examples = synset.examples()  # Ví dụ của từ
        phonetic = synset.lemmas()[0].name()  # Tên chuẩn (dùng trong một số trường hợp)
        
        word_details.append({
            'word': word,
            'meaning': meaning,
            'part_of_speech': part_of_speech,
            'examples': examples,
            'phonetic': phonetic
        })
    
    return word_details

# Ví dụ tra cứu từ "environment"
word_info = get_word_details("environment")
for info in word_info:
    print(f"Word: {info['word']}")
    print(f"Meaning: {info['meaning']}")
    print(f"Part of Speech: {info['part_of_speech']}")
    print(f"Examples: {info['examples']}")
    print(f"Phonetic: {info['phonetic']}")
    print("------")
