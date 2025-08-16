''' cog file for /create_dnd_poll '''
#pylint:disable=line-too-long
from datetime import datetime
import discord
from discord.ext import commands
from views.event_confirm_view import EventConfirmView
from constants import (DESCRIPTION,
                       ADDRESS,
                       TIMEZONE,
                       CHANNEL_ID)

class MessageEdit(commands.Cog):
    ''' handle on_message_edit event '''

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        ''' on_message_edit event '''

        def get_winning_answers(poll_answers: list[discord.PollAnswer]) -> list[discord.PollAnswer]:
            ''' get vote count for winning answers and collect winning answers into list '''
            winning_answers: list[discord.PollAnswer] = []
            winning_count = -1
            for answer in poll_answers:
                winning_count = max(winning_count, answer.count)
            for answer in poll_answers:
                if answer.count == winning_count:
                    winning_answers.append(after.poll.get_answer(answer.id))
            return winning_answers

        def create_event(answer: discord.PollAnswer) -> tuple[str, str]:
            ''' create event object '''
            start_time = datetime.strptime(answer.text + "/" + str(datetime.now().year) + " @ 05:00PM", "%m/%d/%Y @ %I:%M%p")
            start_time = start_time.astimezone(TIMEZONE)
            readable_start = start_time.strftime("%A, %m/%d/%Y @ %I:%M%p")
            end_time = datetime.strptime(answer.text + "/" + str(datetime.now().year) + " @ 11:00PM", "%m/%d/%Y @ %I:%M%p")
            end_time = end_time.astimezone(TIMEZONE)
            readable_end = end_time.strftime("%A, %m/%d/%Y @ %I:%M%p")
            self.bot.events.append(
                {
                    'id': answer.id,
                    'description': DESCRIPTION,
                    'name': answer.text,
                    'start_time': start_time,
                    'readable_start_time': readable_start,
                    'end_time': end_time,
                    'readable_end_time': readable_end,
                    'location': ADDRESS
                }
            )
            return readable_start, readable_end

        async def create_scheduled_events() -> None:
            ''' create scheduled events from poll results '''
            if poll_answers := after.poll.results.answer_counts:
                winning_answers = get_winning_answers(poll_answers)
                for answer in winning_answers:
                    try:
                        readable_start, readable_end = create_event(answer)
                        msg = await channel.send(f"An event will be created with the following information:\n \
                                                Event Name: {answer.text}\n \
                                                Event Description: {DESCRIPTION}\n \
                                                Start Time: {readable_start}\n \
                                                End Time: {readable_end}\n \
                                                Location: {ADDRESS}")
                        view = EventConfirmView(self.bot, msg)
                        await msg.edit(view=view)
                    except discord.HTTPException as e:
                        await channel.send("ERROR. The bot failed to create the scheduled event.")
                        await channel.send("Reason: " + e.text)
                        break
                    except ValueError:
                        await channel.send("ERROR. Invalid time format")
                        break

        channel = self.bot.get_channel(CHANNEL_ID)
        # if the message edit is the poll closing
        if before.poll and after.poll:
            if not after.poll.has_ended(): #temp
                await after.poll.end() #temp
            if after.poll.has_ended():
                await create_scheduled_events()

def setup(bot: discord.Bot):
    ''' connect cog to bot '''
    bot.add_cog(MessageEdit(bot))
