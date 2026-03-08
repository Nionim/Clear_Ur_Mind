import json, os
from datetime import datetime

dir_file = "to_clean/"
def get_file(i: int):
    files = os.listdir(dir_file)
    for f in files:
        if i == 1:
            if not f.endswith("_clean.json"):
                return dir_file + f
        else:
            if f.endswith("_clean.json"):
                return dir_file + f
    return None

def compress_date(date_str):
    """Сжимает дату из формата '2023-11-29T14:31:30' в '23.11.29T14:31'"""
    try:
        # Парсим дату
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Форматируем в сжатый вид: YY.MM.DDTHH:MM
        return dt.strftime('%y.%m.%dT%H:%M')
    except:
        # Если не удалось распарсить, возвращаем как есть
        return date_str

file = get_file(1)
if file is None:
    print("Не найден файл для очистки")
    exit(1)

# Словарь для замены ключей
replace = {
    "date_unixtime": "d",
    "from": "f",
    "text": "t",
    "name": "n",
    "type": "ty",
    "messages": "ms",
    "media_type": "m",
    "forwarded_from": "ff",
    "id": "i",
    "users": "u"
}

# Поля для удаления
remove_list = [
    "date",
    "media_spoiler",
    "messages.id",
    "messages.type",
    "messages.date",
]

messages_remove = [
    "from_id",
    "text_entities",
    "date",
    "media_spoiler",
    "thumbnail_file_size",
    "height",
    "width",
    "file",
    "file_size",
    "photo_file_size",
    "photo",
    "mime_type",
    "thumbnail",
    "edited_unixtime",
    "edited",
    "file_name",
    "sticker_emoji",
    "duration_seconds",
    "reply_to_message_id",
    "reactions",
    "document_id"
]

def extract_and_map_users(data):
    """Извлекает уникальных пользователей и создает маппинг"""
    if 'messages' not in data:
        return data, {}
    
    users = {}
    user_counter = 0
    
    # Собираем всех уникальных пользователей из сообщений
    for message in data['messages']:
        if 'from' in message:
            user_name = message['from']
            
            # Используем имя пользователя как ключ
            if user_name not in users:
                user_counter += 1
                users[user_name] = {
                    "id": str(user_counter),  # Просто номер как строка
                    "name": user_name,
                    "short_id": user_counter
                }
    
    return data, users

def replace_user_names_with_numbers(data, users_mapping):
    """Заменяет имена пользователей на короткие номера в сообщениях"""
    if 'messages' not in data:
        return data
    
    for message in data['messages']:
        if 'from' in message:
            user_name = message['from']
            if user_name in users_mapping:
                # Заменяем имя на номер
                message['from'] = str(users_mapping[user_name]['short_id'])
    
    return data

def create_users_section(users_mapping):
    """Создает секцию users с маппингом номер->информация о пользователе"""
    if not users_mapping:
        return {}
    
    # Преобразуем в нужный формат
    users_by_number = {}
    for user_name, user_info in users_mapping.items():
        short_id = user_info['short_id']
        users_by_number[str(short_id)] = {
            "id": str(short_id),  # Просто номер как строка
            "name": user_name
        }
    
    return users_by_number

def compress_json(data):
    """Сжимает JSON, заменяя длинные ключи на короткие"""
    
    def compress_dict(obj):
        if not isinstance(obj, dict):
            return obj
        
        compressed = {}
        for key, value in obj.items():
            # Получаем короткий ключ
            new_key = replace.get(key, key)
            
            # Обрабатываем вложенные структуры
            if isinstance(value, dict):
                compressed[new_key] = compress_dict(value)
            elif isinstance(value, list):
                compressed[new_key] = compress_list(value)
            else:
                compressed[new_key] = value
        
        return compressed
    
    def compress_list(lst):
        if not isinstance(lst, list):
            return lst
        
        compressed = []
        for item in lst:
            if isinstance(item, dict):
                compressed.append(compress_dict(item))
            elif isinstance(item, list):
                compressed.append(compress_list(item))
            else:
                compressed.append(item)
        
        return compressed
    
    return compress_dict(data)

def remove_fields_from_messages(data, fields):
    if 'messages' not in data:
        return data
    
    for message in data['messages']:
        for field in fields:
            if field in message:
                del message[field]
    return data

def remove_fields_from_root(data, fields):
    """Удаляет поля из корневого объекта"""
    for field in fields:
        if field in data:
            del data[field]
    return data

def compress_dates(data):
    """Сжимает даты во всех сообщениях"""
    if 'messages' not in data:
        return data
    
    for message in data['messages']:
        if 'date' in message:
            message['date'] = compress_date(message['date'])
    
    return data

def remove_empty_messages(data):
    """Удаляет сообщения с пустым текстом"""
    if 'messages' not in data:
        return data
    
    filtered_messages = []
    for message in data['messages']:
        keep = False
        
        # Проверяем текст
        if 'text' in message:
            text = message['text']
            if isinstance(text, str) and text.strip():
                keep = True
            elif isinstance(text, list):
                for item in text:
                    if isinstance(item, str) and item.strip():
                        keep = True
                        break
        
        # Проверяем наличие медиа
        if not keep and 'media_type' in message:
            keep = True
        
        # Проверяем другие важные поля
        if not keep and 'forwarded_from' in message:
            keep = True
        
        if keep:
            filtered_messages.append(message)
    
    data['messages'] = filtered_messages
    return data

def merge_consecutive_messages(data, max_seconds_diff):
    """Объединяет последовательные сообщения от одного отправителя"""
    if 'messages' not in data:
        return data
        
    messages = data['messages']
    if not messages:
        return data

    merged_messages = []
    i = 0
    
    while i < len(messages):
        current_msg = messages[i].copy()
        j = i + 1
        
        # Находим все сообщения для объединения
        while j < len(messages):
            # Проверяем, тот же ли отправитель
            if messages[j].get('from') != current_msg.get('from'):
                break
            
            # Проверяем разницу во времени
            try:
                # Получаем временные метки и конвертируем в числа
                current_time_str = current_msg.get('date_unixtime')
                next_time_str = messages[j].get('date_unixtime')
                
                # Пропускаем, если нет временных меток
                if current_time_str is None or next_time_str is None:
                    break
                
                # Конвертируем строки в числа для корректного сравнения
                current_time = int(float(current_time_str))
                next_time = int(float(next_time_str))
                
                time_diff = next_time - current_time
                
                # Если разница больше допустимой - прекращаем поиск
                if time_diff > max_seconds_diff:
                    break
                    
            except (ValueError, TypeError) as e:
                print(f"Ошибка при обработке времени: {e}")
                break
            
            # Если дошли сюда - объединяем сообщение
            # Объединяем текст
            if 'text' in messages[j] and messages[j]['text']:
                current_text = current_msg.get('text', '')
                next_text = messages[j]['text']
                
                # Преобразуем в строки для простоты
                if isinstance(current_text, list):
                    current_text = ' '.join(str(part) for part in current_text if part)
                if isinstance(next_text, list):
                    next_text = ' '.join(str(part) for part in next_text if part)
                
                # Объединяем с переносом строки
                if current_text and next_text:
                    current_msg['text'] = f"{current_text}\n{next_text}"
                elif next_text:
                    current_msg['text'] = next_text
                # Если current_text есть, а next_text пустой - оставляем как есть
            
            # Объединяем медиа (если нужно)
            if 'media_type' in messages[j]:
                if 'media_type' not in current_msg:
                    current_msg['media_type'] = messages[j]['media_type']
                elif isinstance(current_msg['media_type'], list) and isinstance(messages[j]['media_type'], list):
                    current_msg['media_type'].extend(messages[j]['media_type'])
            
            # Переходим к следующему сообщению для проверки
            j += 1
        
        # Добавляем объединенное сообщение
        merged_messages.append(current_msg)
        # Продолжаем с первого необработанного сообщения
        i = j
    
    data['messages'] = merged_messages
    return data

def remove(compr_sec):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Извлекаем пользователей и создаем маппинг
    # 1
    data, users_mapping = extract_and_map_users(data)
    
    # 2. Удаляем поля из корня
    data = remove_fields_from_root(data, remove_list)
    
    # 3. Удаляем поля из сообщений
    data = remove_fields_from_messages(data, messages_remove)
    
    # 4. Заменяем имена пользователей на номера в сообщениях
    data = replace_user_names_with_numbers(data, users_mapping)
    
    # 5. Удаляем пустые сообщения
    data = remove_empty_messages(data)
    
    # 6. Объединяем последовательные сообщения
    data = merge_consecutive_messages(data, compr_sec)
    
    # 7. Создаем секцию users
    users_section = create_users_section(users_mapping)
    
    # 8. Собираем финальную структуру
    result = {}
    
    # Основные поля чата
    if 'name' in data:
        result['name'] = data['name']
    if 'type' in data:
        result['type'] = data['type']
    if 'id' in data:
        result['id'] = data['id']
    
    # Секция users
    result['users'] = users_section
    
    # Остальные поля
    for key, value in data.items():
        if key not in ['name', 'type', 'id', 'users', 'messages']:
            result[key] = value
    
    # Сообщения
    if 'messages' in data:
        result['messages'] = data['messages']
    
    # 9. Сжимаем даты
    result = compress_dates(result)
    
    # 10. Сжимаем JSON (заменяем ключи на короткие)
    result = compress_json(result)
    
    return result

def format_data(data, fields):
    """Форматирует сообщения согласно указанным полям"""
    if 'ms' not in data:  # 'messages' -> 'ms'
        return data
    
    # Добавляем информацию о формате в корень JSON
    data['fmt'] = fields.copy()
    
    # Форматируем пользователей (убираем лишние вложения)
    if 'u' in data:  # 'users' -> 'u'
        formatted_users = {}
        for user_id, user_info in data['u'].items():
            # Берем только имя, ID уже есть в ключе
            formatted_users[user_id] = user_info.get('n', '')  # 'name' -> 'n'
        data['u'] = formatted_users
    
    # Форматируем сообщения
    formatted_messages = []
    for msg in data['ms']:  # 'messages' -> 'ms'
        formatted_msg = []
        for field in fields:
            if field in msg:
                formatted_msg.append(msg[field])
            else:
                formatted_msg.append(None)
        formatted_messages.append(formatted_msg)
    
    data['ms'] = formatted_messages  # 'messages' -> 'ms'
    return data

def save():
    # Config
    #   Messages compress time
    compr_sec = 240
    #   Inline messages
    in_line = False
    #   Format messages
    format_msg = True
    format_config = ["d", "f", "t"] 

    cleaned_data = remove(compr_sec)
    if format_msg: 
        cleaned_data = format_data(cleaned_data, format_config)
    
    base_name = os.path.splitext(os.path.basename(file))[0]

    prefix = "_saved.json"

    if in_line: prefix = "_clean_inline.json"
    else: prefix = "_clean.json"

    save_file = dir_file + base_name + prefix

    with open(save_file, 'w', encoding='utf-8') as f:
        if in_line: json.dump(cleaned_data, f, separators=(',', ':'), ensure_ascii=False)
        else: json.dump(cleaned_data, f, indent='\t', ensure_ascii=False)

    # Статистика
    original_size = os.path.getsize(file)
    new_size = os.path.getsize(save_file)
    reduction = ((original_size - new_size) / original_size) * 100

    print(f"Файл сохранен как: {save_file}")
    print(f"Сообщений: {len(cleaned_data.get('ms', []))}")
    print(f"Пользователей: {len(cleaned_data.get('u', {}))}")
    print(f"Исходный размер: {original_size:,} байт")
    print(f"Новый размер: {new_size:,} байт")
    print(f"Сжатие: {reduction:.1f}%")

    # Пример структуры
    print("\nСтруктура файла:")
    for key in ['n', 'ty', 'i', 'u', 'ms']:
        if key in cleaned_data:
            if key == 'u':
                print(f"  {key}: {len(cleaned_data[key])} пользователей")
                # Показываем первых 3 пользователей
                for user_id, user_name in list(cleaned_data[key].items())[:3]:
                    print(f"    {user_id}: {user_name}")
                if len(cleaned_data[key]) > 3:
                    print(f"    ... и ещё {len(cleaned_data[key]) - 3}")
            elif key == 'ms':
                print(f"  {key}: {len(cleaned_data[key])} сообщений")
                # Показываем первые 2 сообщения
                for i, msg in enumerate(cleaned_data[key][:2]):
                    # msg теперь список [d, f, t] согласно format_config
                    d = msg[0] if len(msg) > 0 else ''  # дата
                    f = msg[1] if len(msg) > 1 else '?'  # отправитель
                    t = msg[2] if len(msg) > 2 else ''  # текст
                    print(f"    [{i}] {d} от {f}: {t[0:50]}...")
            else:
                print(f"  {key}: {cleaned_data[key]}")

if __name__ == "__main__":
    save()