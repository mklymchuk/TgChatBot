import os
import random
import json
import telebot
from telebot.types import Poll, PollOption

filename = 'bot_token.txt'

with open(filename) as f:
    api_token = f.read()

# Load data from JSON file
with open('stepan_answers.json') as f:
    stepan_answers = json.load(f)

bot = telebot.TeleBot(api_token)

@bot.message_handler(commands=['help', 'Help'])
def send_help(message):
    bot.reply_to(message, "I am a bot, I can help you with some stuff")
    bot.reply_to(message, "You can use the following commands: /stepan, /greet, /go, /help")
    
@bot.message_handler(commands=['stepan','Stepan'])
def send_stepan_answers(message):
    random_key = random.choice(list(stepan_answers.keys()))
    random_answer = stepan_answers[random_key]
    
    if isinstance(random_answer, list):
        for item in random_answer:
            if 'image' in item and 'image_path' in item and item['image']:
                send_message_with_image(message, item)
            elif 'speaker' in item and 'message' in item:
                send_text_message(message, item)
    else:
        if 'image' in random_answer and 'image_path' in random_answer and random_answer['image']:
            send_message_with_image(message, random_answer)
        elif 'speaker' in random_answer and 'message' in random_answer:
            send_text_message(message, random_answer)

def send_text_message(message, answer):
    speaker = answer.get('speaker', '')
    message_text = answer.get('message', '')

    if speaker:
        bot.reply_to(message, f"{speaker}: \"{message_text}\"")
    else:
        bot.reply_to(message, message_text)

def send_message_with_image(message, answer):
    image_path = answer.get('image_path', '')

    if image_path:
        # Construct the absolute path to the image
        script_directory = os.path.dirname(os.path.abspath(__file__))
        image_full_path = os.path.join(script_directory, image_path)

        # Check if the file exists
        if os.path.exists(image_full_path):
            # Open the file and send it as a photo
            with open(image_full_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            # Send a default image instead
            with open('images/default_image.jpg', 'rb') as default_image:
                bot.send_photo(message.chat.id, default_image)
    else:
        # Handle the case where no image_path is provided
        bot.reply_to(message, "Image file not found.")

@bot.message_handler(commands=['greet','Greet'])
def greet(message):
    bot.reply_to(message, "Єбеть")

def print_usernames(message):
    # List of usernames you want to mention
    usernames_to_mention = ['mklymchuk', 'Wizariel', 'Arigotael', '@Nazar803', '@Agent_Ptic']

    # Construct the message with mentioned users
    mentioned_users_text = ', '.join([f"@{username}" for username in usernames_to_mention])
    message_text = f"Патаци {mentioned_users_text}, го грати ігори!"

    # Send the message
    bot.send_message(message.chat.id, message_text)

@bot.message_handler(commands=['go', 'Go'])
def send_poll(message):
    options = [PollOption('Go'), PollOption('Ne go'), PollOption('Za try godyny go')]
    poll = bot.send_poll(message.chat.id, 'Go?', options, is_anonymous=False)
    print_usernames(message)
    print(poll)

@bot.poll_handler(func=lambda poll: True)
def handle_poll(poll):
    if hasattr(poll, 'chat'):
        chat_id = poll.chat.id
    elif hasattr(poll, 'message') and hasattr(poll.message, 'chat'):
        chat_id = poll.message.chat.id
    else:
        # Handle the case where the chat ID cannot be determined
        return
    
    bot.send_message(chat_id, 'Poll results: {}'.format(str(poll.options)))

# Start the bot
bot.polling(none_stop=True)
