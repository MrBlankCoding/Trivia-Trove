import discord
from discord.ext import commands, tasks
import json
from trivia import TriviaGame
from database import JSONDatabase

# Load config
with open('config.json') as f:
    config = json.load(f)

# Initialize bot
bot = commands.Bot(command_prefix=config['prefix'])
trivia = TriviaGame(config['trivia_api_url'])
db = JSONDatabase('database.json')

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    daily_trivia.start()

# Task: Daily trivia question
@tasks.loop(hours=24)
async def daily_trivia():
    await trivia.fetch_questions(amount=1)
    question = trivia.get_next_question()
    if question:
        channel = bot.get_channel(YOUR_CHANNEL_ID)
        await channel.send(f"**Daily Trivia!**\n{question['question']}\n"
                           f"A) {question['incorrect_answers'][0]}\n"
                           f"B) {question['incorrect_answers'][1]}\n"
                           f"C) {question['incorrect_answers'][2]}\n"
                           f"D) {question['correct_answer']}")

# Command: Start trivia
@bot.command(name='trivia')
async def start_trivia(ctx, category=None, difficulty=None):
    await trivia.fetch_questions(category=category, difficulty=difficulty, amount=5)
    question = trivia.get_next_question()
    if question:
        await ctx.send(f"**Trivia Time!**\n{question['question']}\n"
                       f"A) {question['incorrect_answers'][0]}\n"
                       f"B) {question['incorrect_answers'][1]}\n"
                       f"C) {question['incorrect_answers'][2]}\n"
                       f"D) {question['correct_answer']}")

# Command: Answer trivia
@bot.command(name='answer')
async def answer_trivia(ctx, *, answer):
    if trivia.check_answer(answer):
        await ctx.send("Correct!")
        # Update score
        user_id = str(ctx.author.id)
        score = db.get(user_id, 0)
        db.update(user_id, score + 1)
    else:
        await ctx.send("Incorrect.")

# Command: Leaderboard
@bot.command(name='leaderboard')
async def leaderboard(ctx):
    scores = db.read()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "\n".join([f"<@{user_id}>: {score}" for user_id, score in sorted_scores])
    await ctx.send(f"**Leaderboard**\n{leaderboard_text}")

# Command: User profile
@bot.command(name='profile')
async def profile(ctx):
    user_id = str(ctx.author.id)
    score = db.get(user_id, 0)
    await ctx.send(f"**{ctx.author.name}'s Profile**\nScore: {score}")

# Run bot
bot.run(config['token'])
