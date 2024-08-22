import discord
import asyncio
from dotenv import load_dotenv
import os
from src.commands import Commands
from src.bot import MyBot

# Load environment variables from .env file
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

#setting up the intents
intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(command_prefix='?', intents=intents)
    
# Adding the Cog
async def main():
    async with bot:
        await bot.add_cog(Commands(bot))
        await bot.start(token)

# Running the bot
if __name__ == "__main__":
    asyncio.run(main())