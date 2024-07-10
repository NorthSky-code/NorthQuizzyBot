from dependencies import InlineKeyboardBuilder, types, F, aiosqlite
from database import update_quiz_index, get_quiz_index, update_users_score, get_users_score
from questions import quiz_data
from config import dp, bot

async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    update_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_users_score(user_id, update_score)
    await get_question(message, user_id)
    
async def get_question(message, user_id):
    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)
    
def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer_{option}" if option == right_answer else f"wrong_answer_{option}"
        ))
    builder.adjust(1)
    return builder.as_markup()
  
@dp.callback_query(F.data.startswith("right_answer"))
async def right_answer(callback: types.CallbackQuery):
    selected_option = callback.data.split('_')[-1]
    
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    await bot.send_message(callback.from_user.id, f"{selected_option}")
    
    await callback.message.answer("Верно!")
    
    current_question_index = await get_quiz_index(user_id)
    current_score = await get_users_score(user_id)
    
    current_question_index += 1
    current_score += 1
    await update_quiz_index(user_id, current_question_index)
    await update_users_score(user_id, current_score)
    
    result_quiz = f"Ваш результат правильных ответов: {current_score}"
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\n{result_quiz}")
        await update_quiz_index(user_id, current_score)
        
@dp.callback_query(F.data.startswith("wrong_answer"))
async def wrong_answer(callback: types.CallbackQuery):
    selected_option = callback.data.split('_')[-1]
    
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    await bot.send_message(callback.from_user.id, f"{selected_option}")

    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    current_score = await get_users_score(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    await update_users_score(user_id, current_score)
    
    result_quiz = f"Ваш результат правильных ответов: {current_score}"
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\n{result_quiz}")
        await update_quiz_index(user_id, current_score)
