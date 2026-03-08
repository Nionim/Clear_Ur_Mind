from apps import discord, telegram

# select platform
# discord/telegram or custom
platform = discord

working_dir = "to_clean/"

saved_file = "_clean.json"
saved_file_inline = "_clean_inline.json"

# If using discord - replace telegram with discord
replace, remove_list, messages_remove = platform.get_lists();
message_format = platform.get_message_format();
platform_name = platform.__name__

compress_message_seconds = 240
compress_messages = True
format_messages = True
inline_json = False