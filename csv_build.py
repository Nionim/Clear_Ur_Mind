import json
import csv

def extract_content(content_elem):
    """Convert message content to plain string."""
    if isinstance(content_elem, str):
        return content_elem
    if isinstance(content_elem, list):
        parts = []
        for item in content_elem:
            if isinstance(item, str):
                if item.strip():
                    parts.append(item)
            elif isinstance(item, dict):
                ty = item.get("ty")
                if ty == "custom_emoji":
                    parts.append(item.get("document_id", ""))
                elif ty == "link":
                    parts.append(item.get("t", ""))
                elif ty == "text_link":
                    parts.append(item.get("href", ""))
                else:
                    parts.append(str(item))
        return " ".join(parts)
    return str(content_elem)

def convert_json_to_csv(json_path, csv_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chat_id = data.get("i")
    users = data.get("u", [])  # list of [user_id, username]
    
    rows = []
    
    # 1. Header
    #rows.append(["chatid", "user", "username", "unix", "type", "content"])
    rows.append(["chatid", "user", "username", "unix", "content"])
    
    # 2. One row per user (chatid, user, username, rest empty)
    for uid, name in users:
        rows.append([chat_id, uid, name, "", "", ""])
    
    # 3. Messages
    last_unix = None
    size = len(data.get("ms", []))
    i = 0
    for msg in data.get("ms", []):
        i = i + 1
        if len(msg) < 3:
            continue
        unix_abs, user_id, content_raw = msg[0], msg[1], msg[2]
        
        # Compute time field
        if last_unix is None:
            # First message: absolute unix time
            time_field = unix_abs
        else:
            delta = unix_abs - last_unix
            # Show positive delta with '+', negative as is (should not happen)
            time_field = f"+{delta}" if delta >= 0 else str(delta)
        last_unix = unix_abs
        
        content_str = extract_content(content_raw)
        # For messages: chatid empty, username empty, type 'txt'
        #rows.append(["", user_id, "", time_field, "txt", content_str])
        if i == size:
            rows.append(["", user_id, "", unix_abs, content_str])
        else:
            rows.append(["", user_id, "", time_field, content_str])
    
    # Write CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)  # minimal quoting to save space
        writer.writerows(rows)

def run_it(original_file, new_file):
    convert_json_to_csv(original_file, new_file)