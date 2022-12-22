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
        max_tokens=256,
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
    context.bot_data['lastResponse'] = responce

    context.bot.send_message(chat_id=update.effective_chat.id, text=responce)


# For command /continue
def continue_(update: Update, context: CallbackContext):
    prompt = context.bot_data['lastPrompt'] + "\n" + context.bot_data['lastResponse'] + "\n" + update.message.text
    responce = get_responce(prompt)
    context.bot.send_message(chat_id=update.effective_chat.id, text=responce)


# For command /ill
def ill(update: Update, context: CallbackContext):

    # Catch if input is not a number
    try:
        ill = int(update.message.text.strip())
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


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)
continue_handler = CommandHandler('continue', continue_)
dispatcher.add_handler(continue_handler)

updater.start_polling()
