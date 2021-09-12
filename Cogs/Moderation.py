import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions
import json

from discord.ext.commands.core import command

def keystoint(x):
    return {int(k): v for k, v in x.items()}

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.User):
        with open('./logs.json', 'r') as f:
            logsf = json.load(f, object_hook=keystoint)
        if guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Ban")
            embedv.add_field(name='User:', value= user)
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            try:
                schannel = self.client.get_channel(logsf[ctx.guild.id])
                await schannel.send(embed=embedv)  
            except:
                pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        with open('./logs.json', 'r') as f:
            logsf = json.load(f, object_hook=keystoint)
        if guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Unban")
            embedv.add_field(name='User:', value= user)
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            try:
                schannel = self.client.get_channel(logsf[ctx.guild.id])
                await schannel.send(embed=embedv)  
            except:
                pass

    @commands.command(aliases=['setlogs', 'setlog'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def modlogs(self,ctx,channel:discord.TextChannel = None):
        if channel is None:
            await ctx.send(':x: You have to state a channel to log!')
        else:
            try:
                with open('./logs.json', 'r') as f:
                    logsf = json.load(f)
                logsf[str(ctx.guild.id)] = channel.id

                with open('./logs.json', 'w') as f:
                    json.dump(logsf, f, indent= 4)
                await ctx.send('Successfully set modlogs to **{}** channel!'.format(channel))
            except:
                await ctx.send('An error occurred, please contact to Epifiz Developers!')            

    @commands.command(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self,ctx, arg: int = None):
        if arg is None:
            await ctx.send(':x: You need to state a value!')
        else:
            with open('./logs.json', 'r') as f:
                logsf = json.load(f, object_hook=keystoint)
            if ctx.guild.id in logsf:
                embedv = discord.Embed(color = discord.Colour.random())
                embedv.add_field(name='Event Type:', value= "Clear")
                embedv.add_field(name='Channel:', value= ctx.message.channel)
                embedv.add_field(name='Moderator:', value= ctx.message.author)
                embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
                embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png") 
                await ctx.channel.purge(limit=arg)
                await ctx.send(':white_check_mark: Successfully cleared {} messages.'.format(arg))
                try:
                    schannel = self.client.get_channel(logsf[ctx.guild.id])
                    await schannel.send(embed=embedv)  
                except:
                    pass
            else:
                await ctx.channel.purge(limit=arg)
                await ctx.send(':white_check_mark: Successfully cleared {} messages.'.format(arg))

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(":x: You don't have permission to do that!")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':x: Please specify the amount of messages you want to clear.')

    @commands.command(name='kick')
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason="None"):
        with open('./logs.json', 'r') as f:
                logsf = json.load(f, object_hook=keystoint)
        if ctx.guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Kick")
            embedv.add_field(name='Channel:', value= ctx.message.channel)
            embedv.add_field(name='User:', value = member.mention)
            embedv.add_field(name='Moderator:', value= ctx.message.author)
            embedv.add_field(name="Reason:", value= reason)
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png") 
            await member.kick(reason=reason)
            try:
                schannel = self.client.get_channel(logsf[ctx.guild.id])
                await schannel.send(embed=embedv)  
            except:
                pass
        else:       
            await member.kick(reason=reason)
            await ctx.send(f'User {member.mention} has been kicked for: "{reason}".')

    @kick.error
    async def kick_error(self, error, ctx):
        if isinstance(error, error.MissingPermissions):
            await ctx.send(":x: You don't have permission to kick members.")

    @commands.command(name='Ban')
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        with open('./logs.json', 'r') as f:
            logsf = json.load(f, object_hook=keystoint)
        if ctx.guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Ban")
            embedv.add_field(name='Channel:', value= ctx.message.channel)
            embedv.add_field(name='User:', value = member.mention)
            embedv.add_field(name='Moderator:', value= ctx.message.author)
            embedv.add_field(name="Reason:", value= reason)
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            await ctx.send(f'User {member.mention} has been banned for: "{reason}".')
            await member.ban(reason=reason)
            try:
                schannel = self.client.get_channel(logsf[ctx.guild.id])
                await schannel.send(embed=embedv)  
            except:
                pass
        else:
            await ctx.send(f'User {member.mention} has been banned for: "{reason}".')
            await member.ban(reason=reason)

    @ban.error
    async def ban_error(self, error, ctx):
        if isinstance(error, error.MissingPermissions):
            await ctx.send(":x: You don't have permission to ban members.")


    @commands.command(name='Unban', aliases=['pardon', 'uba'])
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        with open('./logs.json', 'r') as f:
            logsf = json.load(f, object_hook=keystoint)
        if ctx.guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Unban")
            embedv.add_field(name='Channel:', value= ctx.message.channel)
            embedv.add_field(name='User:', value = member)
            embedv.add_field(name='Moderator:', value= ctx.message.author)
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            bans = ctx.guild.bans()
            member_name, member_disc = member.split('#')
            for ban_entry in bans:
                user = bans.user

                if (user.name, user.disc) == (member.name, member.disc):
                    await ctx.guild.unban(user)
                    await ctx.send(f'Unbanned {user.name}#{user.disc}.')
                    return
            try:
                schannel = self.client.get_channel(logsf[ctx.guild.id])
                await schannel.send(embed=embedv)  
            except:
                pass
        else:
            bans = ctx.guild.bans()
            member_name, member_disc = member.split('#')
            for ban_entry in bans:
                user = bans.user

                if (user.name, user.disc) == (member.name, member.disc):
                    await ctx.guild.unban(user)
                    await ctx.send(f'Unbanned {user.name}#{user.disc}.')
                    return
        

    @unban.error
    async def unban_error(self, error, ctx):
        if isinstance(error, error.MissingPermissions):
            await ctx.send(":x: You don't have permission to unban members.")

def setup(client):
    client.add_cog(Moderation(client))

