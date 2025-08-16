''' modal to modify scheduled event details '''
#pylint:disable=line-too-long
from datetime import datetime
import discord
from constants import (TIMEZONE,
                       GUILD_ID)

class EventModifyModal(discord.ui.Modal):
    ''' event param verification '''

    def __init__(self, bot: discord.Bot, event: dict, *args, **kwargs):
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
