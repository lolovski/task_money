import os
import re

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from dotenv import load_dotenv

from database.requests.user import get_user_by_tg_id, debit, get_profile
from keyboard.inline.admin_panel import withdrawal_admin_keyboard
from keyboard.inline.profile import money_withdrawal_keyboard
from keyboard.reply.profile import choose_payment_system_keyboard, choose_bank_keyboard, contact_keyboard, \
    choose_telecom_operator_keyboard
from keyboard.reply.start import start_keyboard

load_dotenv()
admin_id = os.getenv('ADMIN_ID')
router = Router(name=__name__)


class MoneyWithdrawalForm(StatesGroup):
    message_id = State()

    telephone = State()
    sbp_bank = State()
    sbp_balance = State()

    card = State()
    bank = State()
    bank_balance = State()

    cripto = State()
    cripto_balance = State()

    mobile_operator = State()
    mobile_telephone = State()
    mobile_balance = State()


@router.message(F.text.startswith('Профиль'))
async def main_profile_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    await state.clear()
    user, pending_tasks, count_ref = await get_profile(tg_id)
    text_pending_tasks = ' \n'
    for task in pending_tasks:
        text_pending_tasks += f'{task.title} | {task.reward}₽ \n'
    
    await message.answer_sticker('CAACAgEAAxkBAAIU7mcIHR7ewG5XTmHgzoTAGoZfNoHJAAKbAgAClmsYRAGYrZHkPYMkNgQ')
    await message.answer(
        text=f'<b>👤 Пользователь: {user.username} \n\n'
             f'🏦 Баланс: {user.balance}₽ \n\n'
             f'👾 ID: {user.id} \n\n'
             f'💰Количество рефералов: {count_ref}\n\n'
             f'📥Задания на проверке: {text_pending_tasks} \n</b>',
        reply_markup=money_withdrawal_keyboard)


@router.callback_query(F.data == 'money withdrawal')
async def money_withdrawal_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id, )
    answer = await call.message.answer(
        text='<b>💳 ВЫВОД ДЕНЕЖНЫХ СРЕДСТВ ПРОИСХОДИТ ТОЛЬКО НА ЮMoney (РФ/СНГ) и банковские картs РФ💸 \n\n'
             'Минимальная сумма вывода средств (руб):📌\n\n'
             'Юmoney\n'
             '├  по номеру телефона/счета - 150₽\n'
             '└  по номеру карты - 150 ₽\n\n'
             '📌 Банковские карты (РФ)\n'
             '├  по номеру телефона - 300 ₽\n'
             '└  пономеру карты - 400 ₽\n\n'
             '📌 Баланс телефона - 150 ₽❗️\n\n'
             'Выводим только на идентифицированные(верифицированные) кошельки ЮMoney. \n'
             '🖥 Как верифицировать свой кошелек <a href="https://yoomoney.ru/page?id=536144">ЮMoney</a>\n\n'
             '🏦 Выбери платежную систему для вывода 🏦</b>',
        reply_markup=choose_payment_system_keyboard, disable_web_page_preview=True)
    await state.set_state(MoneyWithdrawalForm.message_id)
    await state.update_data(message_id=answer.message_id)


@router.message(F.text == 'СБП (номер телефона РФ)')
async def sbp_bank_handler(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                text='<b>Выберите банк</b>\n'
                     'Или напишите название банка',
                reply_markup=choose_bank_keyboard),

    await state.set_state(MoneyWithdrawalForm.sbp_bank)
    await state.update_data(message_id=answer[0].message_id)


@router.message(MoneyWithdrawalForm.sbp_bank)
async def sbp_telephone_handler(message: Message, bot: Bot, state: FSMContext):
    sbp_bank = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(text='<b>Введите номер телефона</b>'
                                       ' (Формат +79876543210)\n '
                                       'Или нажмите на кнопку', reply_markup=contact_keyboard)
    await state.set_state(MoneyWithdrawalForm.telephone)
    await state.update_data(message_id=answer.message_id)
    await state.update_data(sbp_bank=sbp_bank)


@router.message(MoneyWithdrawalForm.telephone)
async def sbp_balance_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    if message.contact:
        telephone = message.contact.phone_number
    else:
        telephone = re.sub(r'[^0-9\s]', '', message.text)
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                                text=f"<b>Введите сумму вывода\n"
                                     f"Минимум: 150р\n"
                                     f"Баланс: {user.balance}</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MoneyWithdrawalForm.sbp_balance)
    await state.update_data(telephone=telephone)
    await state.update_data(message_id=answer.message_id)


@router.message(MoneyWithdrawalForm.sbp_balance)
async def sbp_final_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    balance = int(re.sub(r'[^0-9\s]', '', message.text))
    context = await state.get_data()
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    if 150 <= balance <= user.balance:
        await debit(tg_id, balance)
        new_balance = user.balance - balance
        await bot.send_message(chat_id=admin_id, text=f'<b>Вывод сбп\n'
                                                      f'id {user.id}\n'
                                                      f'Сумма {balance}₽\n'
                                                      f'Банк {context.get('sbp_bank')}\n'
                                                      f'Телефон {context["telephone"]}</b>',
                               reply_markup=await withdrawal_admin_keyboard(tg_id=tg_id, balance=balance))
        await message.answer(text=f'<b>Деньги отправлены на вывод, ожидайте ответа (~5ч) \n'
                                  f'Текущий баланс: {new_balance}₽</b>', reply_markup=start_keyboard
                             )
    else:
        if user.balance < balance:
            answer = await message.answer(text=f'<b>На счету недостаточно денег\n'
                                      f'Текущий баланс: {user.balance}₽\n'
                                      f'Введите корректную сумму</b>'
                                 )
            await state.set_state(MoneyWithdrawalForm.sbp_balance)
            await state.update_data(message_id=answer.message_id)
        else:
            answer = await message.answer(text='Введенная вами сумма \n'
                                               '<b>Ниже минимума!</b> \n'
                                               'Введите еще раз')
            await state.set_state(MoneyWithdrawalForm.sbp_balance)
            await state.update_data(message_id=answer.message_id)


@router.message(F.text == 'Банковская карта (РФ)')
async def bank_name_handler(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                text='<b>Выберите банк</b>\n'
                     'Или напишите название банка',
                reply_markup=choose_bank_keyboard),

    await state.set_state(MoneyWithdrawalForm.bank)
    await state.update_data(message_id=answer[0].message_id)


@router.message(MoneyWithdrawalForm.bank)
async def bank_card_handler(message: Message, bot: Bot, state: FSMContext):
    bank_name = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(text='<b>Введите номер карты или счета</b>\n'
                                       'Формат 1111222233334444')
    await state.set_state(MoneyWithdrawalForm.card)
    await state.update_data(message_id=answer.message_id)
    await state.update_data(bank=bank_name)


@router.message(MoneyWithdrawalForm.card)
async def bank_balance_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    card = re.sub(r'[^0-9\s]', '', message.text)
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                                text=f"<b>Введите сумму вывода\n"
                                     f"Минимум: 200р\n"
                                     f"Баланс: {user.balance}₽</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MoneyWithdrawalForm.bank_balance)
    await state.update_data(card=card)
    await state.update_data(message_id=answer.message_id)


@router.message(MoneyWithdrawalForm.bank_balance)
async def bank_final_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    balance = int(re.sub(r'[^0-9\s]', '', message.text))
    context = await state.get_data()
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    if 200 <= balance <= user.balance:
        await debit(tg_id, balance)
        new_balance = user.balance - balance
        await bot.send_message(chat_id=admin_id, text=f'<b>Вывод карта\n'
                                                      f'id {user.id}\n'
                                                      f'Сумма {balance}₽\n'
                                                      f'Банк {context.get('bank')}\n'
                                                      f'Карта/счёт {context["card"]}</b>',
                               reply_markup=await withdrawal_admin_keyboard(tg_id=tg_id, balance=balance))
        await message.answer(text=f'<b>Деньги отправлены на вывод, ожидайте ответа (~5ч) \n'
                                  f'Текущий баланс: {new_balance}₽</b>', reply_markup=start_keyboard
                             )
    else:
        if user.balance < balance:
            answer = await message.answer(text=f'<b>На счету недостаточно денег\n'
                                      f'Текущий баланс: {user.balance}₽\n'
                                      f'Введите корректную сумму</b>'
                                 )
            await state.set_state(MoneyWithdrawalForm.bank_balance)
            await state.update_data(message_id=answer.message_id)
        else:
            answer = await message.answer(text='Введенная вами сумма \n'
                                               '<b>Ниже минимума!</b> \n'
                                               'Введите еще раз')
            await state.set_state(MoneyWithdrawalForm.bank_balance)
            await state.update_data(message_id=answer.message_id)


@router.message(F.text == 'Крипта')
async def cripto_wallet_handler(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                text='<b>Введите номер кошелька</b>\n',
                reply_markup=choose_bank_keyboard),

    await state.set_state(MoneyWithdrawalForm.cripto)
    await state.update_data(message_id=answer[0].message_id)


@router.message(MoneyWithdrawalForm.cripto)
async def cripto_balance_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    cripto = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', message.text)
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                                text=f"<b>Введите сумму вывода\n"
                                     f"Минимум: 1000р\n"
                                     f"Баланс: {user.balance}</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MoneyWithdrawalForm.cripto_balance)
    await state.update_data(cripto=cripto)
    await state.update_data(message_id=answer.message_id)


@router.message(MoneyWithdrawalForm.cripto_balance)
async def cripto_final_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    balance = int(re.sub(r'[^0-9\s]', '', message.text))
    context = await state.get_data()
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    if 1000 <= balance <= user.balance:
        await debit(tg_id, balance)
        new_balance = user.balance - balance
        await bot.send_message(chat_id=admin_id, text=f'<b>Вывод криптовалюта\n'
                                                      f'id {user.id}\n'
                                                      f'Сумма {balance}₽\n'
                                                      f'Кошелек {context["cripto"]}</b>',
                               reply_markup=await withdrawal_admin_keyboard(tg_id=tg_id, balance=balance))
        await message.answer(text=f'Деньги отправлены на вывод, ожидайте ответа (~5ч) \n'
                                  f'Текущий баланс: {new_balance}', reply_markup=start_keyboard
                             )
    else:
        if user.balance < balance:
            answer = await message.answer(text=f'На счету недостаточно денег\n'
                                      f'Текущий баланс: {user.balance}\n'
                                      f'Введите корректную сумму'
                                 )
            await state.set_state(MoneyWithdrawalForm.cripto_balance)
            await state.update_data(message_id=answer.message_id)
        else:
            answer = await message.answer(text='Введенная вами сумма \n'
                                               '<b>Ниже минимума!</b> \n'
                                               'Введите еще раз')
            await state.set_state(MoneyWithdrawalForm.cripto_balance)
            await state.update_data(message_id=answer.message_id)


@router.message(F.text == 'Мобильная связь')
async def mobile_name_handler(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                text='<b>Выберите оператора</b>\n'
                     'Или напишите название оператора',
                reply_markup=choose_telecom_operator_keyboard),

    await state.set_state(MoneyWithdrawalForm.mobile_operator)
    await state.update_data(message_id=answer[0].message_id)


@router.message(MoneyWithdrawalForm.mobile_operator)
async def mobile_telephone_handler(message: Message, bot: Bot, state: FSMContext):
    mobile_operator = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(text='<b>Введите номер телефона</b>'
                                       ' (Формат +79876543210)\n '
                                       'Или нажмите на кнопку', reply_markup=contact_keyboard)
    await state.set_state(MoneyWithdrawalForm.mobile_telephone)
    await state.update_data(message_id=answer.message_id)
    await state.update_data(mobile_operator=mobile_operator)


@router.message(MoneyWithdrawalForm.mobile_telephone)
async def mobile_balance_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    if message.contact:
        mobile_telephone = message.contact.phone_number
    else:
        mobile_telephone = re.sub(r'[^0-9\s]', '', message.text)
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    context = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    answer = await message.answer(
                                text=f"<b>Введите сумму вывода\n"
                                     f"Минимум: 200р\n"
                                     f"Баланс: {user.balance}₽</b>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MoneyWithdrawalForm.mobile_balance)
    await state.update_data(mobile_telephone=mobile_telephone)
    await state.update_data(message_id=answer.message_id)


@router.message(MoneyWithdrawalForm.mobile_balance)
async def mobile_final_handler(message: Message, bot: Bot, state: FSMContext, tg_id: str):
    balance = int(re.sub(r'[^0-9\s]', '', message.text))
    context = await state.get_data()
    user = await get_user_by_tg_id(tg_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=context.get('message_id'))
    if 200 <= balance <= user.balance:
        await debit(tg_id, balance)
        new_balance = user.balance - balance
        await bot.send_message(chat_id=admin_id, text=f'<b>Вывод мобильная связь\n'
                                                      f'id {user.id}\n'
                                                      f'Сумма {balance}₽\n'
                                                      f'Оператор {context.get('mobile_operator')}\n'
                                                      f'Номер {context["mobile_telephone</b>"]}',
                               reply_markup=await withdrawal_admin_keyboard(tg_id=tg_id, balance=balance))
        await message.answer(text=f'<b>Деньги отправлены на вывод, ожидайте ответа (~5ч) \n'
                                  f'Текущий баланс: {new_balance}</b>', reply_markup=start_keyboard
                             )
    else:
        if user.balance < balance:
            answer = await message.answer(text=f'<b>На счету недостаточно денег\n'
                                      f'Текущий баланс: {user.balance}₽\n'
                                      f'Введите корректную сумму</b>'
                                 )
            await state.set_state(MoneyWithdrawalForm.mobile_balance)
            await state.update_data(message_id=answer.message_id)
        else:
            answer = await message.answer(text='Введенная вами сумма \n'
                                               '<b>Ниже минимума!</b> \n'
                                               'Введите еще раз')
            await state.set_state(MoneyWithdrawalForm.mobile_balance)
            await state.update_data(message_id=answer.message_id)