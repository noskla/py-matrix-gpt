#!/usr/bin/python3
import simplematrixbotlib as matrix
import requests
import asyncio
import os


config = matrix.Config()
config.encryption_enabled = True
config.emoji_verify = True
config.ignore_unverified_devices = True
config.store_path = './crypto_store/'

Creds = matrix.Creds(os.getenv("MATRIX_INSTANCE"),
                     os.getenv("MATRIX_USERNAME"),
                     os.getenv("MATRIX_PASSWORD"))
OpenAICreds = {
        "token": os.getenv("OPENAI_TOKEN")
        }

Bot = matrix.Bot(Creds, config)
PREFIX = os.getenv("BOT_PREFIX")
MAX_MSG_LEN = os.getenv("BOT_MAX_QUERY")


async def fetch_openai_res(query, room_id, msg_author):
    res = requests.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OpenAICreds['token']}"},
            json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{
                            "role": "user",
                            "content": query
                        }]
                })

    json = res.json()

    if "error" in json:
        return await Bot.api.send_text_message(room_id, json["error"]["message"])
    
    choices = json["choices"]
    message = choices[0]
    await Bot.api.send_text_message(room_id, msg_author + " : "
                                    + message["message"]["content"].lower())


@Bot.listener.on_message_event
async def use_gpt(room, message):
    _match = matrix.MessageMatch(room, message, Bot, PREFIX)

    if not _match.is_not_from_this_bot() or not _match.prefix():
        return
    
    if len(str(message)) > MAX_MSG_LEN:
        return await Bot.api.send_text_message(room.room_id, "Query too long")

    asyncio.create_task(fetch_openai_res(message, room.room_id, message.sender))


Bot.run()
