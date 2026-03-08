from formats.telegram_format import *

def get_lists():
    return replace, remove_list, messages_remove

def get_message_format():
    return message_format

message_format = ["d", "f", "t"]

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