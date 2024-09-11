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
                username = message.author.global_name if message.author.global_name else message.author.username
                message_history.append((username, message.content))
        
        message_history.pop(0)    
        message_history.reverse()
        
        summary = """"""
        for message in message_history:
            if message is not None:
                summary += f"{message[0]}: {message[1]}\n"
        return summary
    
    async def complete_message(self, sys_prompt, prompt, model = "gpt-4o-mini"):
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
            history = await self.retrieve_messages(message)
            
            with open("resources/bot_prompt.txt", "r") as f:
                sys_prompt = f.read()
            
            prompt = f"\nrequest: {message.content}\n\n"
            
            prompt += "History of the conversation:\n"
            
            prompt += history
            
            print("sending prompt to openAI")
            
            print(prompt)
            completion = await self.complete_message(sys_prompt, prompt, model="gpt-4o")
            
            await message.channel.send(completion)
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide all required arguments.")
        else:
            await ctx.send("An error occurred.")
            print(error)