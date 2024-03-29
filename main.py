import os
import random
import json
import time
import requests
import telebot
from telebot.types import PollOption
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from giphy_api_key import GIPHY_API_KEY
from bot_token import TG_BOT_API_TOCKEN
from user_id import YOUR_TELEGRAM_USER_ID

# Load data from JSON file
with open('stepan_answers.json') as f:
    stepan_answers = json.load(f)
    
# Create a bot instance
bot = telebot.TeleBot(TG_BOT_API_TOCKEN)

# Command to show the menu with callback buttons
@bot.message_handler(commands=['menu', 'Menu'])
def show_menu(message):
    """Show the menu with callback buttons."""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Stepan', callback_data='stepan'))
    keyboard.row(InlineKeyboardButton('Gif', callback_data='gif'))
    keyboard.row(InlineKeyboardButton('Hello', callback_data='hello'))
    keyboard.row(InlineKeyboardButton('Go', callback_data='go'))
    keyboard.row(InlineKeyboardButton('Help', callback_data='help'))

    bot.send_message(message.chat.id, 'Меню:', reply_markup=keyboard)

# Handler for callback queries
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Handle callback queries from the menu."""
    if call.data == 'stepan':
        send_stepan_answers(call.message)
    elif call.data == 'gif':
        send_random_gif(call.message)
    elif call.data == 'hello':
        greet(call.message)
    elif call.data == 'go':
        send_poll(call.message)
    elif call.data == 'help':
        send_help(call.message)
        
# Stepan command generates random answers from the JSON file
@bot.message_handler(commands=['stepan', 'Stepan'])
def send_stepan_answers(message):
    """Send random answers from the JSON file."""
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
    """Send a text message."""
    speaker = answer.get('speaker', '')
    message_text = answer.get('message', '')

    if speaker:
        bot.send_message(message.chat.id, f"{speaker}: \"{message_text}\"")
    else:
        bot.send_message(message.chat.id, message_text)

def send_message_with_image(message, answer):
    """Send a message with an image."""
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
        
# Command handler for /gif command
@bot.message_handler(commands=['gif', 'Gif'])
def send_random_gif(message):
    """Send a random GIF based on the user's tag."""
    api_key = GIPHY_API_KEY # Your Giphy API key
    
    # Get the tag from the user's message. 
    # If no tag is provided, use 'monkey' as the default tag
    tag = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else 'monkey'

    try:
        # URL for Giphy API to get a random GIF with the specified tag
        url = f"https://api.giphy.com/v1/gifs/random?api_key={api_key}&tag={tag}"

        # Make API request to Giphy
        response = requests.get(url)

        # Parse JSON response
        data = response.json()

        # Check if the response contains data
        if 'data' in data:
            gif_url = data['data']['images']['original']['url']

            # Send the GIF directly in the message
            bot.send_animation(message.chat.id, gif_url)
        else:
            bot.send_message(message.chat.id, "Sorry, couldn't find a GIF with that tag.")

    except Exception as e:
        # Handle any errors
        bot.send_message(message.chat.id, "Такого тегу немає. Спробуй щось інше")

# Command to provide help
@bot.message_handler(commands=['help', 'Help'])
def send_help(message):
    """Send a help message with available commands."""
    bot.reply_to(message, "Ось командни, блеть /menu /stepan, /hello, /go /gif.")

# Command to greet
@bot.message_handler(commands=['hello', 'Hello'])
def greet(message):
    """Greet the user."""
    bot.reply_to(message, "Єбеть")

# Command to send a poll
@bot.message_handler(commands=['go', 'Go'])
def send_poll(message):
    """Send a poll to the chat."""
    options = [PollOption('Go'), PollOption('Ne go'), PollOption('Za try godyny go')]
    poll = bot.send_poll(message.chat.id, 'Go?', options, is_anonymous=False)
    print_usernames(message)
    print(poll)

def print_usernames(message):
    """Print the usernames of the users in the chat."""
    # List of usernames you want to mention
    usernames_to_mention = call_usernames()

    # Construct the message with mentioned users
    mentioned_users_text = ', '.join([f"{username}" for username in usernames_to_mention])
    message_text = f"Патаци {mentioned_users_text}, го грати ігори!"

    # Send the message
    bot.send_message(message.chat.id, message_text)
    
def call_usernames():
    """Read the usernames from a file and return a list."""
    filename = 'users_to_call.csv'
    with open(filename) as f:
        usernames_to_mention = f.read().splitlines()
        return usernames_to_mention

@bot.poll_handler(func=lambda poll: True)
def handle_poll(poll):
    """Handle poll updates."""
    if hasattr(poll, 'chat'):
        chat_id = poll.chat.id
    elif hasattr(poll, 'message') and hasattr(poll.message, 'chat'):
        chat_id = poll.message.chat.id
    else:
        # Handle the case where the chat ID cannot be determined
        return
    
    bot.send_message(chat_id, 'Poll results: {}'.format(str(poll.options)))
    
# Define a dictionary to store the last message/command timestamp for each user
last_action_time = {}

# Define a cooldown period in seconds
cooldown_period = 10  # Adjust this value as needed

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle messages and commands with a cooldown period."""
    global last_action_time

    # Get the user ID
    user_id = message.from_user.id

    # Get the current time
    current_time = time.time()

    # Check if the user has sent a message or command before
    if user_id in last_action_time:
        # Check if the cooldown period has elapsed
        if current_time - last_action_time[user_id] < cooldown_period:
            # Send a message indicating the cooldown period
            bot.reply_to(message, f"Почекай, блеть {cooldown_period} сек.")
            return

    # Update the last action timestamp for the user
    last_action_time[user_id] = current_time
    
    # Check if the user wants to stop the bot
    _stop_bot(message)
            
def _stop_bot(message):
    """Stop the bot process."""
    # Your message handling logic goes here
    if message.text.lower() in ['/stop', '/end']:
        # Check if the user is authorized to stop the bot
        if message.from_user.id == YOUR_TELEGRAM_USER_ID:
            bot.reply_to(message, "Stopping the bot...")
            # Stop the bot process
            os.kill(os.getpid(), 9)
        else:
            # If the user is not authorized, send a warning message
            bot.reply_to(message, "Навіть не думай, блеть.")

# Start the bot
bot.polling(none_stop=True)
