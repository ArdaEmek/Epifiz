import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions

class owner(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.is_owner()
    @commands.command()
    async def status(self, ctx, arg1: str, arg2: str):
        if arg1:
            if arg2:
                if arg1 == "playing":
                    await self.client.change_presence(activity=discord.Game(name= arg2))
                    await ctx.send('Changed Epifiz status to Playing **' + arg2 + '**.')
                elif arg1 == "streaming":
                    await self.client.change_presence(activity=discord.Streaming(name=arg2))
                    await ctx.send('Changed Epifiz status to Streaming **' + arg2 + '**.')
                elif arg1 == "listening":
                    await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=arg2))
                    await ctx.send('Changed Epifiz status to Listening **' + arg2 + '**.')
                elif arg1 == "watching":
                    await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=arg2))
                    await ctx.send('Changed Epifiz status to Watching **' + arg2 + '**.')

    @status.error
    async def status_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            return


    @commands.is_owner()
    @commands.command()
    async def shutdown(self, ctx): 
        await ctx.send('Shutting down...')
        await ctx.bot.logout()


    @shutdown.error
    async def shutdown_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            return


def setup(client):
    client.add_cog(owner(client))
