import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()

# Bot initialization
API_TOKEN = os.getenv('API_KEY')  # Replace with your actual bot token

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Path to your PDF files directory
PDF_BOOKS_PATH = '/books'

# State definitions
class UserState(StatesGroup):
    language = State()
    level = State()
    materials = State()

# Main Menu Keyboard (with "Start" button, language options, and command buttons)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("English language"))
main_menu.add(KeyboardButton("Russian language"))

# Commands Menu Keyboard (with all available commands as buttons)
commands_menu = ReplyKeyboardMarkup(resize_keyboard=True)
commands_menu.add(KeyboardButton("/help"))
commands_menu.add(KeyboardButton("/settings"))
commands_menu.add(KeyboardButton("/status"))
commands_menu.add(KeyboardButton("/reset"))
commands_menu.add(KeyboardButton("/exit"))
commands_menu.add(KeyboardButton("/about"))
commands_menu.add(KeyboardButton("🔙 Back"))

# Levels Menu Keyboard (with "Back" button)
levels = ReplyKeyboardMarkup(resize_keyboard=True)
levels.add(KeyboardButton("Beginner"))
levels.add(KeyboardButton("Elementary"))
levels.add(KeyboardButton("Pre-Intermediate"))
levels.add(KeyboardButton("Intermediate"))
levels.add(KeyboardButton("Upper Intermediate"))
levels.add(KeyboardButton("Advanced"))
levels.add(KeyboardButton("🔙 Back"))

# Level Options Menu Keyboard (with "Back" button)
level_options = ReplyKeyboardMarkup(resize_keyboard=True)
level_options.add(KeyboardButton("📚 Book"))
level_options.add(KeyboardButton("🎧 Audio materials"))
level_options.add(KeyboardButton("🔙 Back"))



# Start Command Handler
@dp.message_handler(commands=["start"], state="*")
async def start(msg: types.Message):
    await msg.answer("Welcome! Please select course:", reply_markup=main_menu)
    await UserState.language.set()

# Language Selection Handler
@dp.message_handler(lambda message: message.text in ["English language", "Russian language"], state=UserState.language)
async def language_selection(msg: types.Message, state: FSMContext):
    if msg.text == "English language":
        await msg.answer("You selected English. Now, please select your level:", reply_markup=levels)
        await UserState.level.set()
    elif msg.text == "Russian language":
        await msg.answer("Вы выбрали русский язык. Теперь выберите уровень:", reply_markup=levels)
        await UserState.level.set()

# Level Selection Handler
@dp.message_handler(lambda message: message.text in ["Beginner", "Elementary", "Pre-Intermediate", "Intermediate", "Upper Intermediate", "Advanced"], state=UserState.level)
async def level_selection(msg: types.Message, state: FSMContext):
    await msg.answer(f"You selected {msg.text} level. Now, choose your learning materials:", reply_markup=level_options)
    await UserState.materials.set()

# Back button in Level Selection (Go back to language selection)
@dp.message_handler(Text(equals="🔙 Back"), state=UserState.level)
async def back_to_language(msg: types.Message, state: FSMContext):
    await msg.answer("You are back at the language selection. Please choose a language:", reply_markup=main_menu)
    await UserState.language.set()

# Material Selection Handler (Book or Audio materials)
@dp.message_handler(lambda message: message.text in ["📚 Book", "🎧 Audio materials"], state=UserState.materials)
async def materials_selection(msg: types.Message, state: FSMContext):
    # Check the level and send the appropriate file for the Book
    level_map = {
        "Beginner": "beginner.pdf",
        "Elementary": "elementary.pdf",
        "Pre-Intermediate": "pre_intermediate.pdf",
        "Intermediate": "intermediate.pdf",
        "Upper Intermediate": "upper_intermediate.pdf",
        "Advanced": "advanced.pdf",
    }

    # Check if the user is asking for the Book
    if msg.text == "📚 Book":
        # Get the file name based on level
        level = await state.get_state()
        level = level.split(":")[-1]  # Extract the level name from the state
        pdf_file = level_map.get(level)

        if pdf_file:
            # Construct the path to the file
            pdf_path = os.path.join(PDF_BOOKS_PATH, pdf_file)
            if os.path.exists(pdf_path):
                # Send the PDF file
                await bot.send_document(msg.chat.id, open(pdf_path, 'rb'))
                await msg.answer(f"Here is your {level} book!")
            else:
                await msg.answer("Sorry, the requested book is not available.")
        else:
            await msg.answer("Sorry, no book found for your level.")

    elif msg.text == "🎧 Audio materials":
        await msg.answer("You selected Audio materials. Here are the audio resources for your level!")

# Back button in Material Selection (Go back to level selection)
@dp.message_handler(Text(equals="🔙 Back"), state=UserState.materials)
async def back_to_level(msg: types.Message, state: FSMContext):
    await msg.answer(f"You are back at the level selection. Please select your level:", reply_markup=levels)
    await UserState.level.set()

# Helper commands
@dp.message_handler(commands=["help"], state="*")
async def help_command(msg: types.Message):
    await msg.answer(
        "Here are some commands you can use:\n\n"
        "/start - Start the bot and begin interacting with it.\n"
        "/help - Get help with the bot commands.\n"
        "/settings - Change your preferences.\n"
        "/reset - Reset your progress.\n"
        "/status - Check your current progress.\n"
        "/cancel - Cancel the current action.\n"
        "/exit - End the conversation.\n"
        "/about - Learn more about this bot.\n\n"
        "Use the buttons to navigate through the menus."
    )

@dp.message_handler(commands=["settings"], state="*")
async def settings_command(msg: types.Message):
    await msg.answer("Here are your settings options:\n\n"
                     "1. Change Language\n"
                     "2. Reset Progress\n"
                     "Use the buttons to adjust your settings.")

@dp.message_handler(commands=["status"], state="*")
async def status_command(msg: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language = user_data.get("language", "Not selected")
    level = user_data.get("level", "Not selected")
    await msg.answer(
        f"Your current status:\n\n"
        f"Language: {language}\n"
        f"Level: {level}\n"
        "You can change your selection anytime."
    )

@dp.message_handler(commands=["reset"], state="*")
async def reset_command(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Your progress has been reset. Please start again by selecting your language:", reply_markup=main_menu)

@dp.message_handler(commands=["exit"], state="*")
async def exit_command(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Goodbye! Type '/start' to begin again.")

@dp.message_handler(commands=["about"], state="*")
async def about_command(msg: types.Message):
    await msg.answer(
        "This bot helps you to learn different languages with tailored materials.\n\n"
        "Created by [Your Name].\n\n"
        "For more help, use the /help command."
    )

# Restart Command Handler (Reset and restart the conversation)
@dp.message_handler(commands=["restart"], state="*")
async def restart_command(msg: types.Message, state: FSMContext):
    await state.finish()  # Clear the current state and user data
    await msg.answer("The conversation has been reset. Please select your language:", reply_markup=main_menu)
    await UserState.language.set()

# Command handler for the Back button
@dp.message_handler(Text(equals="🔙 Back"), state="*")
async def back_to_start(msg: types.Message):
    await msg.answer("You are back at the main menu. Please select your language:", reply_markup=main_menu)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
