import config, os, json
from datetime import datetime
from clean_data import merge_consecutive_messages 
from clean_data import remove_empty_messages
from clean_data import clean_messages
from clean_data import extract_users
from clean_data import clean_root

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
    global file
    file = get_file(working_dir)
    if not file: 
        print("Cannot found any .json files!")
        return None
    data = clear_json()
    data = build_json(data=data)
    global final_data
    final_data = data
    save()

def clear_json():
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    global users_list
    data, users_list = extract_users(data=data)
    data = clean_messages(data=data, 
                    fields=messages_remove)
    data = clean_root(data=data,
                    fields=remove_list)
    data = remove_empty_messages(data=data)
    data = merge_consecutive_messages(data=data,
                    max_seconds_diff=compress_message_seconds)
    return data

def build_json(data):
    data['fmt'] = message_format
    data['users'] = users_to_field(users_list=users_list)
    return data

def users_to_field(users_list):
    if not users_list: return {}

    users_by_number = {}
    for user_name, user_info in users_list.items():
        short_id = user_info['short_id']
        users_by_number[str(short_id)] = [str(short_id), user_name]
    
    return users_by_number

def save():
    base_name = os.path.splitext(os.path.basename(file))[0]
    prefix = None

    if inline_json: prefix = saved_file_inline
    else: prefix = saved_file

    global saved_file_x
    saved_file_x = working_dir + base_name + prefix

    with open(saved_file_x, 'w', encoding='utf-8') as f:
        if inline_json: json.dump(final_data, f, separators=(',', ':'), ensure_ascii=False)
        else: json.dump(final_data, f, indent='\t', ensure_ascii=False)
    print_stats()

def print_stats():
    original_size = os.path.getsize(file)
    new_size = os.path.getsize(saved_file_x)
    reduction = ((original_size - new_size) / original_size) * 100

    # Using for dev
    PLACEHOLDER = "TO REPLACE PLACEHOLDER"
    print(f"File saved as:  {saved_file_x}")
    print(f"Total messages: {len(final_data.get('ms', []))}")
    print(f"Users:          {len(final_data.get('u', {}))}")
    print("==============================")
    print(f"Clear size:     {new_size} B")
    print(f"Original size:  {original_size:,} B")
    print(f"Efficiency:     {reduction:.1f}%")
    
def get_file(dir):
    if not os.path.exists(dir): 
        os.makedirs(dir)
        return None
    files = os.listdir(dir)
    for f in files:
        if f.endswith(".json"):
            return dir + f
    return None

if __name__ == "__main__":
    init()