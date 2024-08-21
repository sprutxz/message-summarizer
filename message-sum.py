import discord
from discord.ext import commands
from openai import OpenAI
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

token = os.getenv("DISCORD_TOKEN")
bot_user_id = "1267862691905536073"

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.message_history = [None]
    
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
    async def retrieve_messages(self, ctx, limit: int = 500, include_bot_messages: bool = True):
        print(f"Retrieving last {limit} messages")
        
        messages = ctx.channel.history(limit=(limit + 1))
        
        message_history = [None]
        async for message in messages:
            if message.author.id != int(bot_user_id) or include_bot_messages:
                message_history.insert(0, (message.author.global_name, message.content))
        
        message_history.pop(-1)
        
        
        summary = """"""
        for message in message_history:
            if message is not None:
                summary += f"{message[0]}: {message[1]}\n"
        
        return summary
    
    async def on_message(self, message):
        await self.process_commands(message)
        
        if self.user.mentioned_in(message):
            history = await self.retrieve_messages(message)
            
            with open("chat_prompt.txt", "r") as f:
                prompt = f.read()
            
            prompt += history
            
            prompt += f"\nQuestion posed: {message.content}"
            
            completion = client.chat.completions.create(model="gpt-4o-mini",
                                                        messages=[
                                                            {"role": "user", "content": prompt}
                                                        ]
                                                        )
            
            await message.channel.send(completion.choices[0].message.content)
    
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def summarize_chat(self, ctx, limit: int = 100):
        
        summary = await self.bot.retrieve_messages(ctx, limit, include_bot_messages=False)
                
        with open("summarize_prompt.txt", "r") as f:
            prompt = f.read()
        
        prompt += summary

        
        completion = client.chat.completions.create(model="gpt-4o-mini",
                                                    messages=[
                                                        {"role": "user", "content": prompt}
                                                    ]
                                                    )
        
        await ctx.send(completion.choices[0].message.content)

    @commands.command()
    async def write_poem(self, ctx):
        #using openAI to write a poem
        await ctx.send("Crafting a poem")
        completion = client.chat.completions.create(model="gpt-4o-mini",
                                                    messages=[
                                                        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                                                        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
                                                    ]
                                                    )
        
        await ctx.send(completion.choices[0].message.content)

#setting up the intents
intents = discord.Intents.default()
intents.message_content = True
bot = MyBot(command_prefix='>', intents=intents)

client = OpenAI()
    
# Adding the Cog
async def main():
    async with bot:
        await bot.add_cog(Commands(bot))
        await bot.start(token)

# Running the bot
if __name__ == "__main__":
    asyncio.run(main())