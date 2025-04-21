def clean_and_tokenize(text, vi_dict_path):
    # Kiểm tra vi_dict_path có phải là đường dẫn tệp hay không
    if not isinstance(vi_dict_path, str):
        raise ValueError(f"Expected string path, got {type(vi_dict_path)}")
    
    # Kiểm tra nếu file không tồn tại
    if not os.path.exists(vi_dict_path):
        raise FileNotFoundError(f"File not found: {vi_dict_path}")

    vi_dict = load_vi_dict_from_txt(vi_dict_path)  # Nạp từ điển từ tệp
    english_keys = set(vi_dict.keys())  # Lấy danh sách các từ tiếng Anh từ vi_dict

    stop_words = set(stopwords.words('english'))
    text = text.lower()  # Chuyển văn bản thành chữ thường

    # Sử dụng regex để lọc từ hợp lệ (chỉ từ chứa chữ cái a-z)
    words = re.findall(r'\b[a-zA-Z]+\b', text)

    filtered_words = []
    word_dict = {}  # Tạo biến lưu trữ từ đã tìm thấy trong từ điển
    word_lengths = {}  # Lưu trữ độ dài của từ trong word_dict

    word_dict = {}

    for word in words:
        if len(word) > 1 and word not in stop_words:
            for dict_word in vi_dict:
                if word == dict_word:  # Chỉ lấy nếu từ khớp hoàn toàn
                    word_dict[word] = dict_word  # Lưu lại key từ điển
                    filtered_words.append(word)
                    break

    
    return filtered_words

