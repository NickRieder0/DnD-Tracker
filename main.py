''' discord bot'''
#pylint:disable=line-too-long,missing-function-docstring,unused-argument
import os
from datetime import datetime
import discord
from constants import (TOKEN,
                       CHANNEL_ID,
                       GUILD_ID,
                       TIMEZONE,
                       DESCRIPTION,
                       ADDRESS,
                       COGS_LIST)

class DndTrackerBot(discord.Bot):
    ''' discord bot with custom data '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []

bot = DndTrackerBot()

@bot.event
async def on_ready():
    ''' test function '''
    channel = bot.get_channel(CHANNEL_ID)
    for cog in COGS_LIST:
        bot.load_extension(f"cogs.{cog}")
    await bot.sync_commands()
    await channel.send("DnD-Tracker bot is ready!")

class EventConfirmView(discord.ui.View):
    ''' custom view '''
    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message
        self.guild = bot.get_guild(GUILD_ID)

    def find_answer(self, interaction: discord.Interaction) -> dict:
        ''' find answer from list of winning poll answers '''
        date = interaction.message.content[114:120]
        date = date.rstrip()
        for index, event in enumerate(bot.events):
            if event['name'] == date:
                return bot.events.pop(index)
        return None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_event_button")
    async def confirm_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        if params := self.find_answer(interaction):
            await self.guild.create_scheduled_event(name=params['name'],
                                            description=params['description'],
                                            start_time=params['start_time'],
                                            end_time=params['end_time'],
                                            location=params['location'])
            await interaction.response.send_message("Event created!", ephemeral=True)
            await discord.asyncio.sleep(2)
            await interaction.delete_original_response()
            await self.message.delete()
        else:
            await interaction.response.send_message("ERROR. Poll answer could not be found. Failed to create event.")


    @discord.ui.button(label="Modify", style=discord.ButtonStyle.blurple, custom_id="modify_event_button")
    async def modify_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        try:
            if params := self.find_answer(interaction):
                modal = EventModifyModal(event=params)
                await interaction.response.send_modal(modal)
                await bot.wait_for("scheduled_event_create", timeout=120)
                await discord.asyncio.sleep(2)
                await self.message.delete()
            else:
                await interaction.followup.send("ERROR. Poll answer could not be found. Failed to create event.")
        except discord.asyncio.TimeoutError:
            await interaction.followup.send("Modify Timeout. Please complete modifications within 2 minutes.")

class EventModifyModal(discord.ui.Modal):
    ''' event param verification '''
    def __init__(self, event, *args, **kwargs):
        super().__init__(title="Modify Event", custom_id="modify_event_modal", *args, **kwargs)
        self.event = event
        self.guild = bot.get_guild(GUILD_ID)

        self.add_item(discord.ui.InputText(label="Name", custom_id="event_name", value=event['name']))
        self.add_item(discord.ui.InputText(label="Description", custom_id="event_description", value=event['description']))
        self.add_item(discord.ui.InputText(label="Start time", custom_id="event_start_time", value=event['readable_start_time']))
        self.add_item(discord.ui.InputText(label="End time", custom_id="event_end_time", value=event['readable_end_time']))
        self.add_item(discord.ui.InputText(label="Location", custom_id="event_location", value=event['location']))

    async def callback(self, interaction: discord.Interaction):

        def get_new_params() -> None:
            ''' grab values from modal and replace them in the event object '''
            new_name = interaction.data['components'][0]['components'][0]['value']
            new_description = interaction.data['components'][1]['components'][0]['value']
            new_start_time = interaction.data['components'][2]['components'][0]['value']
            new_end_time = interaction.data['components'][3]['components'][0]['value']
            new_location = interaction.data['components'][4]['components'][0]['value']

            self.event['name'] = new_name
            self.event['description'] = new_description
            self.event['readable_start_time'] = new_start_time
            self.event['readable_end_time'] = new_end_time
            self.event['location'] = new_location
            start_time = datetime.strptime(new_start_time, "%A, %m/%d/%Y @ %I:%M%p")
            self.event['start_time'] = start_time.astimezone(TIMEZONE)
            end_time = datetime.strptime(new_end_time, "%A, %m/%d/%Y @ %I:%M%p")
            self.event['end_time'] = end_time.astimezone(TIMEZONE)

        try:
            get_new_params()
            await self.guild.create_scheduled_event(name=self.event['name'],
                                            description=self.event['description'],
                                            start_time=self.event['start_time'],
                                            end_time=self.event['end_time'],
                                            location=self.event['location'])
            await interaction.response.send_message("Event created!", ephemeral=True)
            await discord.asyncio.sleep(2)
            await interaction.delete_original_response()
        except ValueError:
            await interaction.response.send_message("ERROR. Invalid date given. Submit time in the same format it is presented.")
        except discord.HTTPException as e:
            await interaction.response.send_message("ERROR. Failed to create the scheduled event.")
            await interaction.followup.send("Reason: " + e.text)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):

    def get_winning_answers(poll_answers: list[discord.PollAnswer]) -> list[discord.PollAnswer]:
        ''' get vote count for winning answers and collect winning answers into list '''
        winning_answers: list[discord.PollAnswer] = []
        winning_count = -1
        for answer in poll_answers:
            if answer.count > winning_count:
                winning_count = answer.count
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
        bot.events.append(
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
                    view = EventConfirmView(msg)
                    await msg.edit(view=view)
                except discord.HTTPException as e:
                    await channel.send("ERROR. The bot failed to create the scheduled event.")
                    await channel.send("Reason: " + e.text)
                    break
                except ValueError:
                    await channel.send("ERROR. Invalid time format")
                    break

    channel = bot.get_channel(CHANNEL_ID)
    # if the message edit is the poll closing
    if before.poll and after.poll:
        if after.poll.has_ended():
            await create_scheduled_events()

bot.run(TOKEN)
