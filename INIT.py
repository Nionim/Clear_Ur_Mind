import config, os, json, re, csv_build
from datetime import datetime
from clean_data import replace_user_names_with_numbers
from clean_data import remove_empty_formatted_messages
from clean_data import merge_consecutive_messages 
from clean_data import remove_empty_messages
from clean_data import clean_messages
from clean_data import compress_json
from clean_data import extract_users
from clean_data import clean_root
from clean_data import format_messages_data

# -==[ Configuration ]==-

platform = config.platform
platform_name = config.platform_name

working_dir = config.working_dir
    
saved_file = config.saved_file
saved_file_inline = config.saved_file_inline
    
replace  = config.replace
remove_list = config.remove_list
messages_remove = config.messages_remove
message_format = config.message_format;

compress_message_seconds = config.compress_message_seconds
compress_messages = config.compress_messages
format_messages = config.format_messages
inline_json = config.inline_json
# -=====================-

# -==[ Working vars ]==-
global file
file = None

global process_data
process_data = None

global final_data
final_data = None

global users_list
users_list = None

def init():
    global file, final_data
    file = get_file(working_dir)
    if not file: 
        print("Cannot found any .json files!")
        return None
    data = clear_json()
    if format_messages:
        data = format_messages_data(data, message_format)
        data['fmt'] = message_format
    final_data = data
    save()

def clear_json():
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    global users_list
    data, users_list = extract_users(data)

    data = clean_messages(data, messages_remove)
    data = clean_root(data, remove_list)

    data = remove_empty_messages(data)  # Первая фильтрация

    data = merge_consecutive_messages(data, compress_message_seconds)

    data = replace_user_names_with_numbers(data, users_list)

    data['users'] = users_to_field(users_list)
    
    if format_messages:
        data = format_messages_data(data, message_format)
        data['fmt'] = message_format
        
        data = remove_empty_formatted_messages(data)
    data = compress_json(data, replace=replace)
    
    return data

def build_json(data):
    ordered_data = {}
    for key in ['n', 'ty', 'i', 'fmt', 'u', 'ms']:
        if key in data:
            ordered_data[key] = data[key]
    for key in data:
        if key not in ordered_data:
            ordered_data[key] = data[key]

    return ordered_data

def users_to_field(users_list):
    if not users_list:
        return []
    users_array = []
    for user_name, user_info in users_list.items():
        users_array.append([user_info['short_id'], user_name])
    users_array.sort(key=lambda x: x[0])
    return users_array

def save():
    global final_data
    base_name = os.path.splitext(os.path.basename(file))[0]

    if inline_json:
        prefix = saved_file_inline
    else:
        prefix = saved_file

    global saved_file_x
    saved_file_x = working_dir + base_name + prefix

    final_data = remove_final_empty(final_data)

    final_data = build_json(final_data)

    with open(saved_file_x, 'w', encoding='utf-8') as f:
        if inline_json:
            json.dump(final_data, f, separators=(',', ':'), ensure_ascii=False)
        else:
            json.dump(final_data, f, indent='\t', ensure_ascii=False)

    print_stats()

def remove_final_empty(data):
    if 'ms' not in data:
        return data

    filtered = []

    for msg in data['ms']:
        if not isinstance(msg, list):
            continue

        if len(msg) < 3:
            continue

        text = msg[2]

        if text is None:
            continue

        if isinstance(text, str):
            if text.strip() == "":
                continue

        filtered.append(msg)

    data['ms'] = filtered
    return data

def print_stats():
    original_size = os.path.getsize(file)
    new_size = os.path.getsize(saved_file_x)
    reduction = ((original_size - new_size) / original_size) * 100
    csv_build.run_it(saved_file_x, saved_file_x+".csv")

    # Using for dev
    PLACEHOLDER = "TO REPLACE PLACEHOLDER"
    print("                              ")
    print("--=======[ Finnally ]=======--")
    print(f"File saved as:\n{saved_file_x}")
    print(f"Total messages: {len(final_data.get('ms', []))}")
    print(f"Users:          {len(final_data.get('u', {}))}")
    print("==============================")
    print(f"Clear size:     {new_size:,} B")
    print(f"Original size:  {original_size:,} B")
    print(f"Efficiency:     {reduction:.1f}%")
    print("                              ")

def get_file(dir):
    if not os.path.exists(dir): 
        os.makedirs(dir)
        return None
    files = os.listdir(dir)
    for f in files:
        if not f.endswith("_clean.json"):
            if f.endswith(".json"):
                return dir + f
    return None

if __name__ == "__main__":
    init()