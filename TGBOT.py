import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from collections import defaultdict
import time

class CasinoGame:
    def __init__(self):
        self.balance = 1000
        self.bet = 0

    def place_bet(self, bet):
        if bet > self.balance or bet <= 0:
            raise ValueError("Некорректная ставка")
        self.balance -= bet
        return bet

    def fly(self):
        height = random.randint(1, 10)
        fall_probability = random.randint(1, 100)
        return height, fall_probability

    def calculate_winnings(self, height, bet):
        return bet * (height + 1)

class Leaderboard:
    def __init__(self):
        self.scores = defaultdict(int)

    def add_score(self, username, score):
        self.scores[username] += score

    def get_leaderboard(self):
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


leaderboard = Leaderboard()
last_reward_time = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['game'] = CasinoGame()
    await update.message.reply_text(f"Добро пожаловать в Казино! Ваш баланс: {context.user_data['game'].balance}\nВведите ставку с помощью /bet <сумма>\nИспользуйте /leaderboard для просмотра таблицы лидеров.\nИспользуйте /daily_reward для получения ежедневной награды.")

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if 'game' not in context.user_data:
            await update.message.reply_text("Сначала начните игру с помощью /start.")
            return

        bet_amount = int(context.args[0])
        game = context.user_data['game']

        game.place_bet(bet_amount)

        height, fall_probability = game.fly()

        if fall_probability < 50:
            result_message = "Упали! Вы проиграли ставку."
            leaderboard.add_score(update.effective_user.username, -bet_amount)
        else:
            winnings = game.calculate_winnings(height, bet_amount)
            game.balance += winnings
            result_message = f"Вы взлетели на {height} и выиграли {winnings}!"
            leaderboard.add_score(update.effective_user.username, winnings)

        await update.message.reply_text(f"Баланс: {game.balance}\n{result_message}")

    except (ValueError, IndexError) as e:
        await update.message.reply_text("Ошибка: " + str(e) + "\nИспользуйте /bet <сумма> для ставки.")

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lb = leaderboard.get_leaderboard()
    if not lb:
        await update.message.reply_text("Таблица лидеров пуста.")
        return

    lb_message = "Таблица лидеров:\n"
    for idx, (username, score) in enumerate(lb, start=1):
        lb_message += f"{idx}. {username}: {score}\n"

    await update.message.reply_text(lb_message)

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global last_reward_time

    username = update.effective_user.username
    current_time = time.time()

    
    if username in last_reward_time and current_time - last_reward_time[username] < 86400:
        await update.message.reply_text("Вы уже получили свою ежедневную награду. Пожалуйста, подождите 24 часа.")
        return

    
    reward_amount = 1000
    last_reward_time[username] = current_time
    context.user_data['game'].balance += reward_amount

    await update.message.reply_text(f"Вы получили свою ежедневную награду в размере {reward_amount}! Ваш баланс: {context.user_data['game'].balance}")

def main() -> None:
    application = ApplicationBuilder().token("ВАШ ТОКЕН").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bet", bet))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("daily_reward", daily_reward))

    application.run_polling()

if __name__ == '__main__':
    main()