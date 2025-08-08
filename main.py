''' discord bot'''
#pylint:disable=line-too-long
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1403182852706795630

DEFAULT_POLL_QUESTION = "What days work for you?"
DEFAULT_POLL_DURATION = timedelta(hours=24)
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NEXT_DAY = timedelta(days=1)
NEXT_WEEKEND = timedelta(days=4)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    ''' test function '''
    print("Hello! DnD-Tracker bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! DnD-Tracker bot is ready!")

@bot.command()
async def create_dnd_poll(ctx : commands.Context, duration=None, start_date=None, *, question=None):
    ''' create poll to schedule dnd '''

    def get_next_three_weekends(date : datetime) -> list[str]:
        ''' get month/day for next three weekends '''
        weekday = date.weekday()
        days_to_friday = 4 - weekday
        if days_to_friday <= 0:
            days_to_friday += 7
        date += timedelta(days=days_to_friday)
        answers = []
        for _ in range(3):
            for _ in range(3):
                answers.append(str(date.month) + "/" + str(date.day))
                date += NEXT_DAY
            date += NEXT_WEEKEND
        return answers

    def create_poll(answers : list[str], question : str) -> discord.Poll:
        ''' use dates to create poll answers '''
        poll = discord.Poll(question=question,
                    duration=duration,
                    multiple=True)
        for answer in answers:
            poll.add_answer(text=answer)
        return poll

    def parse_start_date() -> datetime:
        for fmt in ('%m-%d-%Y', '%m/%d/%Y'):
            try:
                return datetime.strptime(f"{start_date}", fmt)
            except ValueError:
                pass
        year = datetime.now().year
        for fmt in ('%m-%d/%Y', '%m/%d/%Y'):
            try:
                return datetime.strptime(f"{start_date}/{year}", fmt)
            except ValueError:
                pass
        raise ValueError()

    if question is None:
        question = DEFAULT_POLL_QUESTION
    if duration is None:
        duration = DEFAULT_POLL_DURATION
    else:
        duration = timedelta(hours=float(duration))
    if start_date is None:
        start_date = datetime.now()
    else:
        try:
            start_date = parse_start_date()
        except ValueError:
            await ctx.send("Invalid date format. Valid formats include: 1-22 , 1/22 , 1-22-2000 , 1/22/2000 (if no year is given, the current year is assumed).")
    answers = get_next_three_weekends(start_date)
    poll = create_poll(answers, question)
    await ctx.send(poll=poll)

bot.run(TOKEN)
