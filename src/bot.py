import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv
from resources.prompts import bot_prompt
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
        
    async def retrieve_messages(self, ctx, limit: int = 300, oldest = False):
        
        messages = ctx.channel.history(limit=limit, oldest_first = oldest)
        
        message_list = LinkedList()
        
        async for message in messages:
            message_list.prepend(message)
            
        return message_list
    
    async def generate_message_summary(self, messages):
        summary = """"""
        current = messages.head
        while current and current.next:
            message = current.value
            if message:
                username = message.author.global_name if message.author.global_name else message.author.name
                summary += f"{username}: {message.content}\n"
                current = current.next
            
        return summary
    
    async def text_generation(self, sys_prompt, prompt, model = "gpt-4o-mini"):
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
            await self.respond_in_channel(message)
        
        else:
            if message.channel.type == discord.ChannelType.public_thread and message.author.id != int(bot_user_id):
                message_history = await self.retrieve_messages(message, limit = 1, oldest=True)
                
                if self.user.mentioned_in(message_history.head.value):
                    await self.respond_in_thread(message)
    
    async def respond_in_channel(self, message):
        message_history = await self.retrieve_messages(message)
        
        summary = await self.generate_message_summary(message_history)
        
        sys_prompt = bot_prompt
        
        prompt = f"\n query: {message.content}\n\n History of the conversation:\n {summary}"

        completion = await self.text_generation(sys_prompt, prompt, model="gpt-4o")
        
        await self.split_message_and_send(message, completion)

    async def respond_in_thread(self, message):
        message_history = await self.retrieve_messages(message, limit = None)
        
        summary = await self.generate_message_summary(message_history)
        
        sys_prompt = bot_prompt
        
        prompt = f"\n query: {message.content}\n\n History of the conversation:\n {summary}"

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
            
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        
class LinkedList:
    def __init__(self):
        self.head = None
        
    def prepend(self, value):
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node