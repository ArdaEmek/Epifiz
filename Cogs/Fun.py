import discord
from discord.ext import commands
import json

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'API Latency is **{round(self.client.latency * 1000)}** ms!')
    
    @commands.command()
    async def help(self, ctx):
        embedvar = discord.Embed(color=discord.Colour.random())
        embedvar.add_field(name="Fun", value= "- **ping**: Shows API latency.\n - **support** : Support the Epifiz.")
        embedvar.add_field(name="Moderation", value="- **prefix <arg>** : Changes the bot prefix (Administrator)\n- **modlogs <#channel>** : Logs every mod action that is made by Epifiz. (Manage Server)\n- **clear <value>** : Purges messages (Manage Messages)\n- **kick <@user>** : Kicks user (Kick Members)\n- **ban <@user>** : Bans user (Ban Members)\n- **unban <user#1234>** : Unbans User (Ban Members)")
        embedvar.set_footer(text= "Epifiz", icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
        embedvar.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
        await ctx.send(embed=embedvar)

    @commands.command()
    async def support(self, ctx):
        embedvar = discord.Embed(color=discord.Colour.random())
        embedvar.add_field(name="Epifiz Support Server", value='[Link](https://discord.gg/3U4qJaw2BJ)')
        embedvar.add_field(name='Invite Epifiz to your server', value="[Link](https://discord.com/api/oauth2/authorize?client_id=837369249629863977&permissions=8&scope=bot)")
        await ctx.send(embed=embedvar)

def setup(client):
    client.add_cog(Fun(client))

