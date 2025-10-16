from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from datetime import datetime

API_TOKEN = "8286922470:AAGjLeAwDsLuwJ3-gTninHWWlTQzJzACqjw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class ReminderStates(StatesGroup):
    status_text = State()
    status_data = State()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать напоминание")], ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start(message: types.Message):
    user_name = message.from_user.full_name
    await message.answer(f"Доброго времени суток, {user_name}", reply_markup=keyboard)


@dp.message(lambda m: m.text == "Создать напоминание")
async def vvod(message: types.Message, state: FSMContext):
    await message.answer("Что мне напомнить?")
    await state.set_state(ReminderStates.status_text)


@dp.message(ReminderStates.status_text)  # сохраняем текст напоминания в переменную
async def text(message: types.Message, state: FSMContext):
    reminder_text = message.text
    await state.update_data(reminder_text=reminder_text)
    await message.answer("Теперь введи дату и время в формате: 2025-10-20 14:30")
    await state.set_state(ReminderStates.status_data)


@dp.message(ReminderStates.status_data)
async def napominalka(message: types.Message, state: FSMContext):
    try:
        vvod_data = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        now = datetime.now()
        if vvod_data <= now:
            await message.answer("Эта дата уже прошла! Введите будущую дату.")
            return
        data = await state.get_data()
        reminder_text = data["reminder_text"]  # достаём ранее сохранённый текст
        delay = (vvod_data - now).total_seconds()
        await message.answer(f"Напоминание установлено на {vvod_data.strftime('%d.%m.%Y %H:%M')}")
        asyncio.create_task(otpravka(message.chat.id, delay, reminder_text))
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат! Используй формат: 2025-10-20 14:30")


async def otpravka(chat_id: int, delay: float, text: str):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id, f"Напоминание: {text}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
