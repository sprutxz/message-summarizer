import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

bot_user_id = os.getenv("BOT_USR_ID")

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.message_history = [None]
    
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
    async def retrieve_messages(self, ctx, limit: int = 500):
        print(f"Retrieving last {limit} messages")
        
        messages = ctx.channel.history(limit=limit, oldest_first=True)
        
        return messages
    
    async def generate_message_summary(self, messages):
        summary = """"""
        async for message in messages:
            username = message.author.global_name if message.author.global_name else message.author.name
            summary += f"{username}: {message.content}\n"
        
        # deleting last line from summary
        index = len(summary) - 1
        for i in range(len(summary) - 2, -1, -1):
            if summary[i] == "\n":
                index = i
                break
        
        summary = summary[:index+1]
        
        return summary
    
    async def text_generation(self, sys_prompt, prompt, model = "gpt-4o-mini"):
        print("Completing message")
        completion = client.chat.completions.create(model=model,
                                                    messages=[
                                                        {"role": "system", "content": sys_prompt},
                                                        {"role": "user", "content": prompt}
                                                    ]
                                                    )
        
        return completion.choices[0].message.content
    
    async def image_generation(self, prompt, model = "dall-e-3"):
        completion = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        url = completion.data[0].url
        print(f"Image generated : {url}")
        
        return url
    
    async def on_message(self, message):
        await self.process_commands(message)

        if self.user.mentioned_in(message):
            await self.respond_to_message(message)
        
        else:
            if message.channel.type == discord.ChannelType.public_thread and message.author.id != int(bot_user_id):
                message_history = await self.retrieve_messages(message, limit = 1)
                async for msg in message_history:
                    if self.user.mentioned_in(msg):
                        await self.respond_to_message(message)
    
    async def respond_to_message(self, message):
        print("retreiving message history")
        message_history = await self.retrieve_messages(message)
        
        print("generating message summary")
        summary = await self.generate_message_summary(message_history)
        
        with open("resources/bot_prompt.txt", "r") as f:
            sys_prompt = f.read()
        
        prompt = f"\nrequest: {message.content}\n\n"
        
        prompt += "History of the conversation:\n"
        
        prompt += summary
        
        print("sending prompt to openAI")

        completion = await self.text_generation(sys_prompt, prompt, model="gpt-4o")
        
        await self.split_message_and_send(message, completion)
    
    async def split_message_and_send(self, message, completion):
        i = 0
        while i < len(completion):
            
            j = min(i + 2000, len(completion))
            
            while j > i and completion[j-1] != "\n":
                if j == len(completion):
                    break
                
                j -= 1
                
            if j == i:
                j = min(i + 2000, len(completion))
            
            await message.channel.send(completion[i:j])
            i = j
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide all required arguments.")
        else:
            await ctx.send("An error occurred.")
            print(error)