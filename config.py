from apps import discord, telegram
# from apps import custom_module

# select platform
# discord/telegram or custom
# platform = custom_module
platform = telegram

working_dir = "to_clean/"

saved_file = "_clean.json"
saved_file_inline = "_inline_clean.json"

# If using discord - replace telegram with discord
replace, remove_list, messages_remove = platform.get_lists();
message_format = platform.get_message_format();
platform_name = platform.__name__

compress_message_seconds = 240
compress_messages = True
format_messages = True
inline_json = False