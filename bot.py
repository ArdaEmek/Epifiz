import os
import json
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import Member


TOKEN = 'ODM3MzY5MjQ5NjI5ODYzOTc3.YIri4g.5pI3eZZJPwqEY9bTA3ljt4KwAJ0'
DTOKEN = 'ODg5MTcyNDk5Njk3Mzc3MzQx.YUdYaw.UCv9vCtHaoMyKNOt68hQca3zykk'

extensions = ['Fun', 'Moderation', 'owner', 'Music']

def get_prefix(client, message):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]
    except:
        try:
            prefixes[str(message.guild.id)] = '.'
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent= 4)
            return "."
        except:
            return "."


client = commands.AutoShardedBot(command_prefix = get_prefix, help_command= None, owner_id = 486198835975028757)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Epifiz is working on {str(len(client.guilds))} servers.')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))

@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '.'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent= 4)

@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent= 4)

def keystoint(x):
    return {int(k): v for k, v in x.items()}

@client.command()
@commands.guild_only()
@has_permissions(administrator=True)
async def prefix(ctx, prefix= None):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if prefix is None:
        await ctx.send('You need to state a new prefix!' )
    else:
        with open('./logs.json', 'r') as f:
            logsf = json.load(f, object_hook=keystoint)
        if ctx.guild.id in logsf:
            embedv = discord.Embed(color = discord.Colour.random())
            embedv.add_field(name='Event Type:', value= "Change Prefix")
            embedv.add_field(name='Channel:', value= ctx.message.channel)
            embedv.add_field(name='Moderator:', value= ctx.message.author)
            embedv.add_field(name='New Prefix:', value= "**" + prefix + "**")
            embedv.set_footer(text='Epifiz Logging', icon_url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            embedv.set_thumbnail(url="https://images-ext-2.discordapp.net/external/ywSgoes0w0g4O39Zu9vFOho4nGV6uBNcWXNps7SfE_I/%3Fsize%3D256/https/cdn.discordapp.com/avatars/837369249629863977/9416002e65d8c493e6c2b23d34c328cd.png")
            schannel = client.get_channel(logsf[ctx.guild.id])
            await schannel.send(embed=embedv)
            await ctx.send('I successfully changed my prefix to **' + prefix + '**')
            prefixes[str(ctx.guild.id)] = prefix

            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent= 4)

@prefix.error
async def prefix_error(ctx, error):
    if isinstance(error, MissingPermissions):
        ctx.send(":x: You don't have permission to  do that!")

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        client.load_extension("Cogs." + extension)
        print('Successfully loaded {}'.format(extension))
        await ctx.send('Success!')
    except Exception as error:
        print('{} cannot be loaded. [{}]'.format(extension, error))
        await ctx.send('An error occurred while loading **{}** extension. Please check the console.'.format(extension))

@load.error
async def load_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return

@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.mention_everyone is False:
        with open("prefixes.json", "r") as f:
            prefixes= json.load(f)
        prefix = prefixes[str(message.guild.id)]
        await message.channel.send("My prefix is **" + prefix + "** in this server.")
        await client.process_commands(message)
    await client.process_commands(message)

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        client.unload_extension("Cogs." + extension)
        print('Successfully unloaded {}'.format(extension))
        await ctx.send('Success!')
    except Exception as error:
        print('{} cannot be unloaded. [{}]'.format(extension, error))
        await ctx.send('An error occurred while disabling **{}** extension. Please check the console.'.format(extension))


@unload.error
async def unload_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please complete the required arguements.")
    elif isinstance(error, MissingPermissions):
        await ctx.send("You don't have enough permission to do that!")
    elif isinstance(error, commands.CommandError):
        print("An error occurred. Guild id : {} . Error: ".format(ctx.guild.id), error)


for extension in extensions:
    try:
        client.load_extension("Cogs." + extension)
    except Exception as error:
        print('{} cannot be loaded. [{}]'.format(extension, error))
client.run(TOKEN)