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
        print("Summary retrieved")
        return summary
    
    async def complete_message(self, prompt, model = "gpt-4o-mini"):
        completion = client.chat.completions.create(model=model,
                                                    messages=[
                                                        {"role": "user", "content": prompt}
                                                    ]
                                                    )
        
        return completion.choices[0].message.content
    
    async def on_message(self, message):
        await self.process_commands(message)
        
        if self.user.mentioned_in(message):
            history = await self.retrieve_messages(message)
            
            with open("resources/chat_prompt.txt", "r") as f:
                prompt = f.read()
            
            prompt += history
            
            prompt += f"\nQuestion posed: {message.content}"
            
            print("sending prompt to openAI")
            completion = await self.complete_message(prompt, model="gpt-4o")
            
            await message.channel.send(completion)