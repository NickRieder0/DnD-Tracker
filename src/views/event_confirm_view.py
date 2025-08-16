''' view for confirming scheduled events '''
#pylint:disable=line-too-long, unused-argument
import discord
from modals.event_modify_modal import EventModifyModal
from constants import GUILD_ID

class EventConfirmView(discord.ui.View):
    ''' event confirm view '''

    def __init__(self, bot: discord.Bot, message: discord.Message):
        super().__init__()
        self.bot = bot
        self.message = message
        self.guild = bot.get_guild(GUILD_ID)

    def find_answer(self, interaction: discord.Interaction) -> dict:
        ''' find answer from list of winning poll answers '''
        date = interaction.message.content[118:124]
        date = date.rstrip()
        for index, event in enumerate(self.bot.events):
            if event['name'] == date:
                return self.bot.events.pop(index)
        return None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_event_button")
    async def confirm_button_callback(self, button: discord.Button, interaction: discord.Interaction):
        ''' create scheduled event from event info '''
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
        ''' brings up the modal to edit event info and create scheduled event '''
        try:
            if params := self.find_answer(interaction):
                modal = EventModifyModal(bot=self.bot, event=params)
                await interaction.response.send_modal(modal)
                await self.bot.wait_for("scheduled_event_create", timeout=120)
                await discord.asyncio.sleep(2)
                await self.message.delete()
            else:
                await interaction.followup.send("ERROR. Poll answer could not be found. Failed to create event.")
        except discord.asyncio.TimeoutError:
            await interaction.followup.send("Modify Timeout. Please complete modifications within 2 minutes.")
