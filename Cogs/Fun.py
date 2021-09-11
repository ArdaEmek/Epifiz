import discord
from discord.ext import commands
import json
import asyncio
from typing import Union

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'API Latency is **{round(self.client.latency * 1000)}** ms!')
    
    @commands.command()
    async def help(self, ctx):
        mainembed = (discord.Embed(color=discord.Colour.random())
            .add_field(name="**Categories**", value=":tada: Fun\n:gear: Moderation\n:musical_note: Music")
        
            )
        embed1 = (discord.Embed(color=discord.Colour.random())
            .add_field(name="Fun", value= "- **ping** : Shows API latency.\n - **support** : Support the Epifiz.")
            .set_footer(text= "Epifiz", icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
        )

        embed2 = (discord.Embed(color=discord.Colour.random())
            .add_field(name="Moderation", value="- **prefix <arg>** : Changes the bot prefix (Administrator)\n- **modlogs <#channel>** : Logs every mod action that is made by Epifiz. (Manage Server)\n- **clear <value>** : Purges messages (Manage Messages)\n- **kick <@user>** : Kicks user (Kick Members)\n- **ban <@user>** : Bans user (Ban Members)\n- **unban <user#1234>** : Unbans User (Ban Members)")
            .set_footer(text= "Epifiz", icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
        )
        embed3 = (discord.Embed(color=discord.Colour.random())
            .add_field(name="Music", value= "- **join** : Makes the bot join the channel which you are in.\n - **play** : Plays a song.\n - **summon** : The bot joins a channel given by the user.(Manage Guild)\n - **leave** : The bot leaves the channel.\n - **now** : Sends a message containing the currently playing song.\n - **pause** : Pauses the currently playing song.\n - **resume** : Resumes the song that was playing and was paused.\n - **stop** : Stops the currently playing or paused song.\n - **skip** : Skips the currently playing song and plays the next one in the queue if present.\n - **queue** : Sends a message with the current songs queue.\n - **shuffle** : Shuffles the current queue songs so that they'll play randomly.\n - **remove** : Removes a song from the current queue.\n - **loop** : Loops the current song.")
            .set_footer(text= "Epifiz", icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            
            )

        embed = await ctx.send(embed=mainembed)
        await embed.add_reaction('🎉')
        await embed.add_reaction('⚙️')
        await embed.add_reaction('🎵')
        
        def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):  # r = discord.Reaction, u = discord.Member or discord.User.
            return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id and \
               str(r.emoji) in ["🎉", "⚙️", "🎵", "⬅️"]
        while True:
            try:
                reaction, user = await self.client.wait_for(event = 'reaction_add', check = check, timeout = 60.0)

                if str(reaction.emoji) == "🎉":
                    await embed.clear_reaction('🎉')
                    await embed.clear_reaction('⚙️')
                    await embed.clear_reaction('🎵')
                    await embed.remove_reaction(reaction, user)
                    await embed.edit(embed=embed1)
                    await embed.add_reaction('⬅️')

                elif str(reaction.emoji) == "⚙️":
                    await embed.clear_reaction('🎉')
                    await embed.clear_reaction('⚙️')
                    await embed.clear_reaction('🎵')
                    await embed.edit(embed=embed2)
                    await embed.add_reaction('⬅️')

                elif str(reaction.emoji) == "🎵":
                    await embed.clear_reaction('🎉')
                    await embed.clear_reaction('⚙️')
                    await embed.clear_reaction('🎵')
                    await embed.edit(embed=embed3)
                    await embed.add_reaction('⬅️')

                elif str(reaction.emoji) == "⬅️":
                    await embed.clear_reaction('⬅️')
                    await embed.edit(embed=mainembed)
                    await embed.add_reaction('🎉')
                    await embed.add_reaction('⚙️')
                    await embed.add_reaction('🎵')

            except asyncio.TimeoutError:
                await embed.delete()
                break


    @commands.command()
    async def support(self, ctx):
        embedvar = discord.Embed(color=discord.Colour.random())
        embedvar.add_field(name="Epifiz Support Server", value='[Link](https://discord.gg/3U4qJaw2BJ)')
        embedvar.add_field(name='Invite Epifiz to your server', value="[Link](https://discord.com/api/oauth2/authorize?client_id=837369249629863977&permissions=8&scope=bot)")
        await ctx.send(embed=embedvar)

def setup(client):
    client.add_cog(Fun(client))

