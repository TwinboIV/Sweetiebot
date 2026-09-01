import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from datetime import datetime, time
import random
from pathlib import Path

load_dotenv()
#intents.message_content = True
TARGET_TIME = time(hour=23, minute=28, second=0)
base_path = "..\\res\\weekdays\\"
last_images = {
    "Monday": "",
    "Tuesday": "",
    "Wednesday": "",
    "Thursday": "",
    "Friday": "",
    "Saturday": "",
    "Sunday": ""
}

class SweetieBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        print(f'Initializing SweetieBot.....')
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self):
        self.send_message.start()

    @tasks.loop(time=TARGET_TIME)
    async def send_message(self, channel_id=int(os.getenv('DEFAULT_CHANNEL_ID'))):
        channel = self.get_channel(channel_id)
        print(f"Channel found: {channel}")  # Debugging line to check if the channel is found
        if channel:
            day_name = datetime.now().strftime('%A')
            image_path: Path = Path(f"{base_path}{day_name}")
            print (f"Looking for images in: {image_path}")
            folders = [f for f in image_path.iterdir() if f.is_dir()]
            files = []
            for folder in folders:
                # Get all files in the folder
                folder_files = [f for f in folder.iterdir() if f.is_file()]
                files.extend(folder_files)
                
            # Select a random file that's different from last week's and update it to be stored
            random_file = random.choice(files)

            while random_file.name == last_images[day_name]:
                random_file = random.choice(files)

            last_images[day_name] = random_file.name

            # Clear any previous bot messages
            async for message in channel.history(limit=150):
            # Check if the message was sent by this bot
                if message.author.id == self.user.id:
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        print("Missing permissions to delete a message.")
                        break
                    except discord.HTTPException as e:
                        print(f"Failed to delete message: {e}")
            
            # Get the name of the containing folder
            folder_name = random_file.parent.name
            # Get the day of the week in all lowercase letters
            day_of_week = datetime.now().strftime('%A').lower()
            # Edit the name of the channel to include the folder name and day of the week
            new_channel_name = f"{folder_name}-{day_of_week}"

            await channel.edit(name=new_channel_name)

            # Send the new file
            await channel.send(file=discord.File(random_file))
        else:
            print(f"Error: Could not find channel with ID {channel_id}")

intents = discord.Intents.default()
intents.message_content = True
sweetiebot = SweetieBot(command_prefix="!", intents=intents)

@sweetiebot.command()
async def send(ctx):
    await sweetiebot.send_message(channel_id=ctx.channel.id)

sweetiebot.run(os.getenv('DISCORD_TOKEN'))