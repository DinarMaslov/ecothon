hellotxt = "Привет!\n Нажми /user, если ты польщователь и /dep, если ты работник департамента"  #все имена переменных текста заканчивать txt
biotxt = "Спасибо! Расскажи, пожалуйста, о себе"
thanktxt = "Спасибо!"


from asyncio import Lock

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types

import sqlite3

con = sqlite3.connect("ecothon.db")
cur = con.cursor()


bot = Bot(token="", parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=MemoryStorage())

lock = Lock()

class RegisterMessages(StatesGroup):
    step1 = State() #статус пользователя
    step2 = State() #био


class ObserveMessages(StatesGroup):
    step1 = State() #проект
    step2 = State() #

class NearMessages(StatesGroup):
    step1 = State() #проект
    step2 = State() #

@dp.message_handler(commands='start', state=None) #добавляем в БД, справшиваем имя, добаляем кнопу "пропустить"
async def start(message: types.Message):
    print(message)
    if cur.execute("""SELECT userid FROM users WHERE userid=?""", (message.from_user.id, )).fetchone() is None:
        print("!!!")
        cur.execute("""INSERT INTO users (userid) VALUES (?)""", (message.from_user.id, ))
        con.commit()
    await RegisterMessages.step1.set()
    await bot.send_message(message.from_user.id, hellotxt)
    
@dp.message_handler(commands='user', state=RegisterMessages.step1)
async def reg_step1(message: types.Message, state: FSMContext):
    cur.execute("""UPDATE users SET status=0 WHERE userid=(?)""", (message.text, message.from_user.id, ))
    con.commit()
    await bot.send_message(message.from_user.id, biotxt)
    await RegisterMessages.next()

@dp.message_handler(commands='dep', state=RegisterMessages.step1)
async def reg_step1(message: types.Message, state: FSMContext):
    async with lock:
        name = message.text
        print(name)
    cur.execute("""UPDATE users SET name=(?) WHERE userid=(?)""", (message.text, message.from_user.id, ))
    con.commit()
    await bot.send_message(message.from_user.id, biotxt)
    await RegisterMessages.next()

@dp.message_handler(content_types='text', state=RegisterMessages.step2)
async def reg_step2(message: types.Message, state: FSMContext):
    async with lock:
        bio = message.text
        print(bio)
    cur.execute("""UPDATE users SET about=(?) WHERE userid=(?)""", (message.text, message.from_user.id, ))
    con.commit()
    await bot.send_message(message.from_user.id, thanktxt)
    await state.finish()


@dp.message_handler(content_types='photo', state=None)
async def observe_start(message: types.Message, state: FSMContext):
    cur.execute("""INSERT INTO map (userid) VALUES (?)""", (message.from_user.id, ))
    con.commit()
    await ObserveMessages.step1.set()
    await bot.send_message(message.from_user.id, "напиши название")


@dp.message_handler(content_types='text', state=ObserveMessages.step1)
async def observe_step1(message: types.Message, state: FSMContext):

    #cur.execute("""UPDATE users SET name=(?) WHERE userid=(?)""", (message.text, message.from_user.id, ))
    #con.commit()
    await ObserveMessages.step2.set()
    await bot.send_message(message.from_user.id, "скинь гео")

@dp.message_handler(content_types='location', state=ObserveMessages.step2)
async def observe_step2(message: types.Message, state: FSMContext):
    lat=message.location.latitude
    long=message.location.longitude
    n = cur.execute("""SELECT id FROM map WHERE userid=(?) ORDER BY id DESC LIMIT 1""", (message.from_user.id, ))
    cur.execute("""UPDATE users SET (lat, long) VALUES (?, ?) WHERE id=(?)""", (lat, long, n, ))
    con.commit()
    await ObserveMessages.step2.set()
    await bot.send_message(message.from_user.id, "скинь fghjlk")

@dp.message_handler(commands='near', state=None) 
async def start(message: types.Message):
    await NearMessages.step1.set()
    await bot.send_message(message.from_user.id, "отправь гео")



if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
