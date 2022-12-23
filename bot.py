import os
import openai
import telegram 
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import logging

# Set your API key
openai.api_key = os.environ["API_KEY"]
openai.organization = os.environ["ORGANIZATION_ID"]

bot = telegram.Bot(token=os.environ["BOT_TOKEN"])
updater = Updater(token=os.environ["BOT_TOKEN"], use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def get_responce(prompt, max_tokens=1000, temperature=0.9, frequency_penalty=0, presence_penalty=0, model="text-davinci-003"):
    """
    Get responce from text-davinci-003

    Args:
        prompt (str): Prompt to get responce from
        model (str, optional): Model to use. Defaults to "text-davinci-003".
        max_tokens (int, optional): Max tokens to return. Defaults to 1000.
        temperature (float, optional): how adventurous the responce is. Defaults to 0.9.
        frequency_penalty (float, optional): how much to penalize new tokens based on their existing frequency in the text so far. Defaults to 0.
        presence_penalty (float, optional): how much to penalize new tokens based on whether they appear in the text so far. Defaults to 0.
    """

    responce = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=1000,
        temperature=0.9,
        presence_penalty=0,
        frequency_penalty=0
    )

    return responce["choices"][0]["text"]


# For normal messages
def echo(update: Update, context: CallbackContext):
    prompt = update.message.text
    context.bot_data['lastPrompt'] = prompt

    if 'ill' not in context.bot_data.keys():
        context.bot_data['ill'] = 0.3

    responce = get_responce(prompt, temperature=context.bot_data['ill'])
    context.bot_data['lastResult'] = responce

    context.bot.send_message(chat_id=update.effective_chat.id, text=responce)


def chat(update: Update, context: CallbackContext):
    prompt = " ".join(update.message.text.split(" ")[1:])
    print(prompt)
    context.bot_data['lastPrompt'] = prompt

    if 'ill' not in context.bot_data.keys():
        context.bot_data['ill'] = 0.3

    responce = get_responce(prompt, temperature=context.bot_data['ill'])
    context.bot_data['lastResult'] = responce

    context.bot.send_message(chat_id=update.effective_chat.id, text=responce)


# For command /continue
def continue_(update: Update, context: CallbackContext):
    context.bot_data['lastPrompt'] = context.bot_data['lastPrompt'] + "\n" + context.bot_data['lastResult'] + " ".join(update.message.text.split(" ")[1:])
    prompt = context.bot_data['lastPrompt']
    print(prompt)
    responce = get_responce(prompt)
    context.bot_data['lastResult'] = responce

    context.bot.send_message(chat_id=update.effective_chat.id, text=responce)


# For command /ill
def ill(update: Update, context: CallbackContext):

    # Catch if input is not a number
    try:
        ill = update.message.text.strip().split(" ")[1]
        ill = float(ill)
    except IndexError:
        if 'ill' not in context.bot_data.keys():
            context.bot_data['ill'] = 0.3

        context.bot.send_message(chat_id=update.effective_chat.id, text="illness at: " + str(context.bot_data['ill']) + " (value from 0.0 - 1.0)")
        return
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a number")
        return
    
    # set the ill value between 0 to 1
    if ill > 1:
        ill = 1
    elif ill < 0:
        ill = 0

    context.bot_data['ill'] = ill
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ill value set to {ill}")


# for /img command
def img(update: Update, context: CallbackContext):
    prompt = " ".join(update.message.text.split(" ")[1:])

    responce = openai.Image.create(
        prompt=prompt,
        size="256x256",
        response_format="url",
        n=1
    )

    print(responce)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=responce['data'][0]['url'])


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)
continue_handler = CommandHandler('continue', continue_)
dispatcher.add_handler(continue_handler)
ill_handler = CommandHandler('ill', ill)
dispatcher.add_handler(ill_handler)
chat_handler = CommandHandler('chat', chat)
dispatcher.add_handler(chat_handler)
img_handler = CommandHandler('img', img)
dispatcher.add_handler(img_handler)

updater.start_polling()
