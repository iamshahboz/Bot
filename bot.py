from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Bot initialization
API_TOKEN = '7347984574:AAFT2itjoFydJjzIyNX08TJOG5rdqB3dCo8'  # Replace with your actual bot token

# Set up bot and dispatcher with FSMStorage (to remember the user's state)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# State definitions
class UserState(StatesGroup):
    language = State()
    level = State()
    materials = State()

# Main Menu Keyboard (with "Back" button)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("English language"))
main_menu.add(KeyboardButton("Russian language"))

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
    await msg.answer("Welcome! Please select your language:", reply_markup=main_menu)
    await UserState.language.set()

# Language Selection Handler
@dp.message_handler(lambda message: message.text in ["English language", "Russian language"], state=UserState.language)
async def language_selection(msg: types.Message, state: FSMContext):
    if msg.text == "English language":
        await msg.answer("You selected English. Now, please select your level:", reply_markup=levels)
        await UserState.level.set()
    elif msg.text == "Russian language":
        await msg.answer("You selected Russian. The bot will be in Russian soon!", reply_markup=main_menu)  # Adjust for Russian flow as needed
        await UserState.language.set()

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

# Material Selection Handler
@dp.message_handler(lambda message: message.text in ["📚 Book", "🎧 Audio materials"], state=UserState.materials)
async def materials_selection(msg: types.Message, state: FSMContext):
    if msg.text == "📚 Book":
        await msg.answer("You selected the Book. Here are the book resources for your level!")
        # Provide the book resources or further instructions here.
    elif msg.text == "🎧 Audio materials":
        await msg.answer("You selected Audio materials. Here are the audio resources for your level!")
        # Provide the audio resources or further instructions here.

# Back button in Material Selection (Go back to level selection)
@dp.message_handler(Text(equals="🔙 Back"), state=UserState.materials)
async def back_to_level(msg: types.Message, state: FSMContext):
    await msg.answer(f"You are back at the level selection. Please select your level:", reply_markup=levels)
    await UserState.level.set()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
