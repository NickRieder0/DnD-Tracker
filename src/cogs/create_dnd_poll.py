''' cog file for /create_dnd_poll '''
#pylint:disable=line-too-long, no-member
#pyright:reportInvalidTypeForm=false
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from constants import (DEFAULT_POLL_DURATION,
                       DEFAULT_POLL_QUESTION,
                       TIMEZONE,
                       NEXT_DAY,
                       NEXT_WEEKEND,
                       GUILD_ID)

class CreateDndPoll(commands.Cog):
    ''' create poll to schedule future DnD sessions '''

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(description="Create a poll to schedule future DnD sessions", guild_ids=[GUILD_ID])
    async def create_dnd_poll(self, ctx: discord.ApplicationContext,
                                question: discord.Option(str,
                                                        "question for the poll",
                                                        default=DEFAULT_POLL_QUESTION),
                                duration: discord.Option(int,
                                                        "time, in hours, the poll will be available",
                                                        default=DEFAULT_POLL_DURATION),
                                start_date: discord.Option(str,
                                                        "valid formats: 1-22 , 1/22 , 1-22-2000 , 1/22/2000 (if no year is given, the current year is used)",
                                                        required=False)):
        ''' Create a poll to schedule future DnD sessions '''

        def parse_start_date() -> datetime:
            ''' if user input start date, attempt to parse into datetime object '''
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
            start_date = datetime.now(tz=TIMEZONE)
        else:
            try:
                start_date = parse_start_date()
            except ValueError:
                await ctx.send("ERROR. Invalid date given. Valid formats are provided in the parameter description.")
        answers = get_next_three_weekends(start_date)
        poll = create_poll(answers, question)
        await ctx.respond(poll=poll)

def setup(bot: discord.Bot):
    ''' connect cog to bot '''
    bot.add_cog(CreateDndPoll(bot))
