import io
import logging
import os

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import requests
import json
from PIL import Image

import yt_dlp


router = Router()
API_KEY = 'Ukj6MtrLV23rnsiHZykzXZ1iOR1u7s9avScLnBRBG94NjB5ghszwoOspW2Jf'
url = "https://stablediffusionapi.com/api/v3/text2img"

# Just write a keyboard
kb_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Generate images'), KeyboardButton(text="find a music")],
    [KeyboardButton(text='Where is project lay?')]
], one_time_keyboard=True)

kb_back = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Back')]
], one_time_keyboard=True)

class Form(StatesGroup):
    waiting_fro_promt = State()
    audio_get = State()
    continue_get = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # logging.INFO("using start command")
    await message.reply(f'Hello',
                        reply_markup=kb_main)




@router.message(F.text == 'Generate images')
async def gen_image(message: Message, state: FSMContext):
    await message.answer("Enter a prompt")
    await state.set_state(Form.waiting_fro_promt)

# ============================================================================ #
def gitHubUrl():
    inl_kb = [
        [InlineKeyboardButton(text='link to repo', callback_data='urlOfGitHub')], #, url='https://github.com/kitCHERNOV/EcomDjango.git')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inl_kb)

@router.message(F.text == 'Where is project lay?')
async def get_url(message: Message, state: FSMContext):
    await message.answer('link to repo', reply_markup=gitHubUrl())

@router.callback_query(F.data == 'urlOfGitHub')
async def ret_to_mainkb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer('https://github.com/kitCHERNOV/telegaBot.git', reply_markup=kb_main)

@router.message(Form.continue_get)
async def crossroad(message: Message, state: FSMContext):
    if message.text in ['No','no','n']:
        await state.clear()
        await message.answer("All right, we go back", reply_markup=kb_main)
    elif message.text in ['Yes','yes','y']:
        await state.set_state(Form.waiting_fro_promt)
        await  message.answer("You are continue. Write new prompt")

# ================================================================================= #


@router.message(Form.waiting_fro_promt)
async def generate_images(message: Message, state: FSMContext):
    # if message.text == 'back':
    #     await
    #     await state.set_state(Form.get_kebord)
    await state.clear()


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

    json_object = json.loads(json_string)

    link = json_object[ "output"][0]

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
    await message.answer(f'request: {message.text}') #,reply_markup=kb_back)
    await message.answer(f'Are you want to continue?')

    await state.set_state(Form.continue_get)


# ================================================================================ #
def download_audio(anime_title):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': ('downloads/'+str(anime_title)+'.mp3'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{anime_title} song", download=True) # can add opening
            if search_results['entries']:
                video_url = search_results['entries'][0]['url']
                ydl.download([video_url])
                audio_file = f"downloads/{anime_title}.mp3"
                if os.path.exists(audio_file):
                    return audio_file
                else:
                    return None
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@router.message(F.text == 'find a music')
async def transitToAudioFunc(message: Message, state: FSMContext):
    await state.set_state(Form.audio_get)
    await message.answer('What kind of audio do you want to find?')

@router.message(Form.audio_get)
async def InputNameOfMusic(message: Message, state: FSMContext):
    audio_file = download_audio(message.text)
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, 'rb'):
            audio_byte_io = FSInputFile(audio_file)
            await state.clear()
            await message.answer_audio(audio_byte_io, reply_markup=kb_main)
        os.remove(audio_file)  # Удаляем файл после отправки
    else:
        await message.reply(message.text, "Не удалось найти опенинг для указанного аниме.")