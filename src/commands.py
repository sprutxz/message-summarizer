from discord.ext import commands
from resources.prompts import summarize_prompt

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def summarize_chat(self, ctx, limit: int = 100):
        
        msg_hst = await self.bot.retrieve_messages(ctx, limit)
        
        summary = await self.bot.generate_message_summary(msg_hst)
           
        sys_prompt = summarize_prompt
        
        prompt = f"Chat History:\n{summary}"
        
        completion = await self.bot.text_generation(sys_prompt, prompt)
        
        await ctx.send(completion)

    @commands.command(
        description="Writes a poem about recursion",
        help="Usage: !write_poem"
    )
    async def write_poem(self, ctx):
        # using openAI to write a poem
        await ctx.send("Crafting a poem")
        
        prompt = "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.\nCompose a poem that explains the concept of recursion in programming."
        
        completion = await self.bot.text_generation(prompt)
        
        await ctx.send(completion)
    
    @commands.command(
        description="Generate an image based on a prompt",
        help="Usage: !generate_image <prompt>"
    )
    async def generate_image(self, ctx, prompt: str):
        if not prompt:
            await ctx.send("Please provide a prompt.")
            return
        
        await ctx.send("Generating an image")
        
        print(prompt)
        
        completion = await self.bot.image_generation(prompt)
        
        await ctx.send(completion)