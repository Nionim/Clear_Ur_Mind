import re, os

def get_file(file_dir):
    files = os.listdir(file_dir)
    for f in files:
        if not f.endswith("_minded.txt") and f.endswith(".txt"):
            return os.path.join(file_dir, f)
    return None

the_end = """

Что это?
Какой язык?
Почему оно так написано?
"""

replace_1 = {
    "ь": "",
    "и": "i",
    "а": "и",
    "а": "о",
    "я": "йа",
}

replace_2 = {
    "тся": "тя",
    "ться": "тя",
    "лйа": "лiа",
    "iз-зо": "з"
}

replace_dict = [replace_1, replace_2]

replace_text = True
boustrophedon = False

mirror_even = True
mirror_letters = False

def replace(data, replace_list):
    if not replace_text:  return data
    replace_list = sorted(replace_list.items(), key=lambda x: len(x[0]), reverse=True)

    for old, new in replace_list:
        if len(old) < 5:
            def replace_char(match):
                char = match.group(0)
                if char.isupper():
                    return new.upper()
                else:
                    return new
            data = re.sub(re.escape(old), replace_char, data)
            print(f"\nNew Data: \n{data}")
        else:
            old_escaped = re.escape(old)
            pattern = rf'(?<!\w)({old_escaped})(?!\w)'
        
            def replace_func(match):
                matched = match.group(1)
                if matched.isupper(): return new.upper()
                elif matched[0].isupper(): return new[0].upper() + new[1:]
                else: return new
            data = re.sub(pattern, replace_func, data, flags=re.IGNORECASE)
            print(f"\nNew Data: \n{data}")
    return data

def boustrophedon_text(data):
    if not boustrophedon: 
        return data
    
    lines = data.split('\n')
    result_lines = []
    
    for i, line in enumerate(lines):
        should_mirror = (i % 2 == 1) if mirror_even else (i % 2 == 0)
        
        if should_mirror:
            if mirror_letters:
                result_lines.append(line[::-1])
            else:
                words = line.split(' ')
                # Отделяем знаки препинания от слов
                processed_words = []
                for word in words:
                    if not word:
                        continue
                    # Определяем знаки препинания в конце слова
                    end_punct = ''
                    while word and word[-1] in '.,!?;:—…':
                        end_punct = word[-1] + end_punct
                        word = word[:-1]
                    
                    # Определяем знаки препинания в начале слова
                    start_punct = ''
                    while word and word[0] in '.,!?;:—…':
                        start_punct += word[0]
                        word = word[1:]
                    
                    processed_words.append({
                        'word': word,
                        'start_punct': start_punct,
                        'end_punct': end_punct
                    })
                
                # Переворачиваем порядок слов
                processed_words = list(reversed(processed_words))
                
                # Собираем строку с правильным расположением знаков препинания
                # После переворота знаки, которые были в конце слов, становятся началом следующих слов
                reconstructed = []
                for j, item in enumerate(processed_words):
                    word = item['word']
                    # Знаки препинания, которые были в начале оригинального слова,
                    # теперь будут в конце предыдущего слова после переворота
                    start_punct = item['start_punct']
                    
                    # Знаки препинания, которые были в конце слова,
                    # теперь будут в начале этого слова после переворота
                    end_punct = item['end_punct']
                    
                    # Для первого слова в перевернутой строке используем end_punct как начало
                    if j == 0:
                        reconstructed.append(f"{end_punct}{word}")
                    else:
                        # Для остальных слов: start_punct предыдущего слова становится
                        # концом текущего слова, а end_punct - началом текущего
                        prev_item = processed_words[j-1]
                        if prev_item['start_punct']:
                            reconstructed[-1] = reconstructed[-1] + prev_item['start_punct']
                        reconstructed.append(f"{end_punct}{word}")
                
                # Обрабатываем start_punct последнего слова
                if processed_words and processed_words[-1]['start_punct']:
                    reconstructed[-1] = reconstructed[-1] + processed_words[-1]['start_punct']
                
                result_line = ' '.join(reconstructed)
                result_lines.append(result_line)
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)

if __name__ == "__main__":
    file_name = get_file("to_replace/")
    save_file_path = file_name.replace(".txt", "_minded.txt")

    with open(file_name, 'r', encoding='utf-8') as f:
        data = f.read()

        for r in replace_dict:
            data = replace(data, r)
        data = boustrophedon_text(data)
    
        with open(save_file_path, 'w', encoding='utf-8') as f:
            print(
                "\n\n\n==============================================="
                +
                f"\nSaved: \n\n\n{data+the_end}")
            f.write(data+the_end)