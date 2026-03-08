from formats.discord_format import *

def get_lists():
    return replace, remove_list, messages_remove

def get_message_format():
    return message_format

message_format = ["d", "f", "t"]

replace = {
    "guild": "g",
    "channel": "ch",
    "dateRange": "dr",
    "exportedAt": "ea",
    "messages": "ms",
    "id": "i",
    "name": "n",
    "type": "ty",
    "timestamp": "ts",
    "timestampEdited": "te",
    "callEndedTimestamp": "cet",
    "isPinned": "p",
    "content": "c",
    "author": "a",
    "attachments": "att",
    "embeds": "emb",
    "stickers": "st",
    "reactions": "re",
    "mentions": "men",
    "inlineEmojis": "ie",
    "discriminator": "d",
    "nickname": "nn",
    "color": "col",
    "isBot": "b",
    "roles": "rl",
    "avatarUrl": "au",
    "after": "a",
    "before": "b",
    "categoryId": "ci",
    "category": "ca",
    "topic": "t",
    "iconUrl": "iu",
    "position": "pos"
}

remove_list = [
    "guild.iconUrl",
    "channel.categoryId",
    "channel.category",
    "channel.topic",
    "dateRange",
    "exportedAt"
]

messages_remove = [
    "callEndedTimestamp",
    "timestampEdited",
    "isPinned",
    "mentions",
    "inlineEmojis",
    "reactions",
    "embeds",
    "stickers",
    "author.discriminator",
    "author.color",
    "author.isBot",
    "author.roles",
    "attachments.id",
    "attachments.size",
    "attachments.proxy_url",
    "attachments.height",
    "attachments.width",
    "attachments.content_type"
]