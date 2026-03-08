# TODO replace hardcoded values like 'messages' to dynamic values from conf
# or to values from main class

def check(data):
    if 'messages' not in data: return True
    messages = data['messages']
    if not messages: return True

# Remove some fields from "messages" section
def clean_messages(data, fields):
    if check(data): return data
    
    for message in data['messages']:
        for field in fields:
            if field in message: del message[field]
    return data

# Remove some fields from root section
def clean_root(data, fields):
    for field in fields:
        if field in data: del data[field]
    return data

# TODO rewrote lol
# Need list for keeping fields
# Remove messages without content
def remove_empty_messages(data):
    if check(data): return data
    
    filtered_messages = []
    for message in data['messages']:
        keep = False
        if 'text' in message:
            text = message['text']
            if isinstance(text, str) and text.strip(): keep = True
            elif isinstance(text, list):
                for item in text:
                    if isinstance(item, str) and item.strip():
                        keep = True
                        break
        
        if not keep and 'media_type' in message: keep = True
        if keep:
            filtered_messages.append(message)
    
    data['messages'] = filtered_messages
    return data

def merge_consecutive_messages(data, max_seconds_diff):
    if check(data): return data

    messages = data['messages']
    merged_messages = []
    
    i = 0
    while i < len(messages):
        current_message = messages[i].copy()
        j = i + 1
        while j < len(messages):
            if messages[j].get('from') != current_message.get('from'): break
            
            try:
                current_time_str = current_message.get('date_unixtime')
                next_time_str = messages[j].get('date_unixtime')
                
                if current_time_str is None or next_time_str is None: break
                current_time = int(float(current_time_str))
                next_time = int(float(next_time_str))
                time_diff = next_time - current_time

                if time_diff > max_seconds_diff: break
            except (ValueError, TypeError) as e:
                print(f"Ugly date format: {e}")
                break

            if 'text' in messages[j] and messages[j]['text']:
                current_text = current_message.get('text', '')
                next_text = messages[j]['text']
                
                if isinstance(current_text, list):
                    current_text = ' '.join(str(part) for part in current_text if part)
                if isinstance(next_text, list):
                    next_text = ' '.join(str(part) for part in next_text if part)
                
                if current_text and next_text: 
                    current_message['text'] = f"{current_text}\n{next_text}"
                elif next_text: current_message['text'] = next_text
            
            if 'media_type' in messages[j]:
                if 'media_type' not in current_message:
                    current_message['media_type'] = messages[j]['media_type']
                elif isinstance(current_message['media_type'], list) and isinstance(messages[j]['media_type'], list):
                    current_message['media_type'].extend(messages[j]['media_type'])
            j += 1
        merged_messages.append(current_message)
        i = j
    
    data['messages'] = merged_messages
    return data

# Extract users with uuid and names
def extract_users(data):
    if check(data): return data, {}
    
    users = {}
    user_counter = 0
    
    for message in data['messages']:
        if 'from' in message:
            user_name = message['from']
            if user_name not in users:
                user_counter += 1
                users[user_name] = {
                    "id": str(user_counter),
                    "name": user_name,
                    "short_id": user_counter
                }
    return data, users