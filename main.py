''' discord bot'''
#pylint:disable=line-too-long
#pyright:reportInvalidTypeForm=false
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import discord

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1403182852706795630

DEFAULT_POLL_QUESTION = "What days work for you?"
DEFAULT_POLL_DURATION = 24 # hours
NEXT_DAY = timedelta(days=1)
NEXT_WEEKEND = timedelta(days=4)

bot = discord.Bot()

@bot.event
async def on_ready():
    ''' test function '''
    print("Hello! DnD-Tracker bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! DnD-Tracker bot is ready!")

@bot.command(description="Create a poll to schedule future DnD sessions.")
async def create_dnd_poll(ctx: discord.ApplicationContext,
                          question: discord.Option(str,
                                                   "question for the poll",
                                                   default=DEFAULT_POLL_QUESTION),
                          duration: discord.Option(int,
                                                   "time, in hours, the poll will be available",
                                                   default=DEFAULT_POLL_DURATION),
                          start_date: discord.Option(str,
                                                   "valid formats: 1-22 , 1/22 , 1-22-2000 , 1/22/2000 (if no year is given, the current year is used)",
                                                   required=False)):
    ''' create poll to schedule dnd '''

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

    def get_next_three_weekends(date: datetime) -> list[str]:
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

    def create_poll(answers: list[str], question: str) -> discord.Poll:
        ''' use dates to create poll answers '''
        poll = discord.Poll(question=question,
                    duration=duration,
                    allow_multiselect=True)
        for answer in answers:
            poll.add_answer(text=answer)
        return poll

    if start_date is None:
        start_date = datetime.now()
    else:
        try:
            start_date = parse_start_date()
        except ValueError:
            await ctx.send("Invalid date format.")
    answers = get_next_three_weekends(start_date)
    poll = create_poll(answers, question)
    await ctx.respond(poll=poll)

bot.run(TOKEN)
