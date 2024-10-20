import io
import logging
import os

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import requests
import json
from PIL import Image


router = Router()
API_KEY = 'WwS2Oam4hElngKG0vuIIN8CfbWzUpr0d3vdKVC1oQmZPEjAoQiPQu6PZGHfx'
url = "https://stablediffusionapi.com/api/v3/text2img"

# Just write a keyboard
kb_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Generate images'), KeyboardButton(text="find a music")],
    [KeyboardButton(text='Where is project lay?')]
], one_time_keyboard=True)

class Form(StatesGroup):
    waiting_fro_promt = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Hello.\nYour ID: {message.from_user.id}\nName: {message.from_user.first_name}',
                        reply_markup=kb_main)

# create async func for stop generate images
@router.message(Form.waiting_fro_promt)
async def back_fr_genImg(message: Message):
    back_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Back')]
    ])
    await message.reply(reply_markup=back_kb)

@router.message(F.text == 'Generate images')
async def gen_image(message: Message, state: FSMContext):
    await message.answer("Enter a prompt")
    await state.set_state(Form.waiting_fro_promt)


@router.message(Form.waiting_fro_promt)
async def generate_images(message: Message):
    payload = json.dumps({
        "key": API_KEY,
        "prompt": message.text,
        "negative_prompt": None,
        "width": "1024",
        "height": "1024",
        "samples": "1",
        "num_inference_steps": "20",
        "seed": "99999999",
        "guidance_scale": 7.5,
        "safety_checker": "yes",
        "multi_lingual": "no",
        "panorama": "no",
        "self_attention": "yes",
        "upscale": "no",
        "embeddings_model": None,
        "webhook": None,
        "track_id": None
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_string = response.text
    print(json_string)
    json_oblect = json.loads(json_string)

    link = json_oblect["output"][0]

    response = requests.get(link)

    byte_io = io.BytesIO(response.content)

    image = Image.open(byte_io)

    image_byte_io = io.BytesIO()

    image.save(image_byte_io, format='PNG')

    image_byte_io.seek(0)

    # Try saved image to 'images' directory

    # with open('C:/Other/DL/L1/app/images/img1.png','wb') as f:
    #     f.write(image_byte_io.getvalue())

    photo = BufferedInputFile(image_byte_io.getvalue(), filename="image.png")  # Указываем имя файла
    # photo = FSInputFile('C:/Other/DL/L1/app/images/img1.png')

    await message.answer_photo(photo)