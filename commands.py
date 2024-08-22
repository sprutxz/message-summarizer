from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def summarize_chat(self, ctx, limit: int = 100):
        
        summary = await self.bot.retrieve_messages(ctx, limit, include_bot_messages=False)
                
        with open("summarize_prompt.txt", "r") as f:
            prompt = f.read()
        
        prompt += summary
        
        completion = await self.bot.complete_message(prompt)
        
        await ctx.send(completion)

    @commands.command()
    async def write_poem(self, ctx):
        # using openAI to write a poem
        await ctx.send("Crafting a poem")
        
        prompt = "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.\nCompose a poem that explains the concept of recursion in programming."
        
        completion = await self.bot.complete_message(prompt)
        
        await ctx.send(completion)
