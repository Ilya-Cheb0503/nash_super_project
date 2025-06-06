from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from constants.constants import aditable_text
from data_holder.data_science import load_json_file, save_json_file, change_json_file

router = Router()


class TextEditState(StatesGroup):
    choosing_wich_text = State()
    waiting_for_new_text = State()
    waiting_for_confirmation = State()


def choose_text_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(text="Приветственное сообщение", callback_data="edit_text_welcome")
            ],
            [
                InlineKeyboardButton(text="Контакты", callback_data="edit_text_contacts")
            ],
            [
                InlineKeyboardButton(text="Соц. cети", callback_data="edit_text_social_media")
            ],
            [
                InlineKeyboardButton(text="Информация о компании", callback_data="edit_text_company_info")
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="admin_soft")
            ],
        ]
    )

def confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(text="Сохранить", callback_data="confirmed")
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="unconfirmed")
            ]
        ]
    )

@router.callback_query(F.data == 'edit_text')
async def start_editing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите раздел, текст которого необходимо отредактировать", reply_markup=choose_text_keyboard())
    await state.set_state(TextEditState.choosing_wich_text)

@router.callback_query(F.data_startswith("edit_text_"))
async def choose_wich_text(callback: CallbackQuery, state: FSMContext):
    wich = callback.data.replace("edit_text_", "")
    await state.update_data(wich_text=wich)
    await callback.message.edit_text("Введите новый текст для раздела.")
    await state.set_state(TextEditState.waiting_for_new_text)

@router.message(TextEditState.waiting_for_new_text, F.text)
async def get_new_text(message: Message, state: FSMContext, callback: CallbackQuery):
    await state.update_data(new_text=message.text)
    await callback.message.edit_text(
        f"{message.text}",
        reply_markup=confirmation_keyboard()
        )
    await state.set_state(TextEditState.waiting_for_confirmation)

@router.callback_query(F.data == "confirmed")
async def confirm_new_text(callback: CallbackQuery, state: FSMContext):
    json_file = await load_json_file(aditable_text, '/data_holder/aditable_text.json')
    changed_json_file = await change_json_file(json_file=json_file, key=state.wich_text, value=state.new_text)
    await save_json_file(json_file=changed_json_file, file_path='/data_holder/aditable_text.json')

    await state.clear()

@router.callback_query(F.data == "unconfirmed")
async def unconfirmed_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите новый текст для раздела.")
    await state.set_state(TextEditState.waiting_for_new_text)
