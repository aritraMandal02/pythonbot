import discord
import asyncio
import json
import os
import random
import DiscordUtils
import youtube_dl

from discord import guild
from discord.ext import commands
from discord.ext import tasks
from itertools import cycle
from discord.ext import commands


def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix)
music = DiscordUtils.Music()
players = {}


@client.event
async def on_ready():
    print('Bot is online.')


@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)


# @client.event
# async def on_message(msg):
#     if msg.mentions[0] == client.user:
#         with open('prefixes.json', 'r') as f:
#             prefixes = json.load(f)
#
#             pre = prefixes[str(msg.guild.id)]
#
#         await msg.channel.send(f"My prefix is {pre}")
#
#     await client.process_commands(msg)


@client.command()
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)
    await ctx.send(f"The prefix was changed to {prefix}")


@client.event
async def on_member_join(member):
    # role = discord.utils.get(member.server.roles, name='Example Role')
    # await client.add_roles(member, role)
    print(f'{member} has joined the server')


@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')


@client.command()
async def status(ctx):
    await ctx.send('Ready to rock. New updates are coming in future!')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send('Invalid command used!')


@client.command(aliases=['hi'], help="Say 'hi' to the bot")
async def hello(ctx):
    await ctx.send('Hello. Beep. Boop. Hi user! How are you? Beep.')


@client.command(help='This command kicks any member from the server.')
@commands.has_permissions(administrator=True)
async def kick(ctx, member: commands.MemberConverter, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')


@client.command(help='This command bans any member from the server.')
@commands.has_permissions(administrator=True)
async def ban(ctx, member: commands.MemberConverter):
    await ctx.guild.ban(member)
    await ctx.send(f'{member.mention} has been banned.')


class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        amount = argument[:-1]
        unit = argument[-1]

        if amount.isdigit() and unit in ['s', 'm']:
            return int(amount), unit

        raise commands.BadArgument(message='Not a valid duration')


@client.command(help='This command bans any member temporarily from the server.')
@commands.has_permissions(administrator=True)
async def tempban(ctx, member: commands.MemberConverter, duration: DurationConverter):

    multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    amount, unit = duration

    await ctx.guild.ban(member)
    await ctx.send(f'Banned {member.mention} for {amount}{unit}.')
    await asyncio.sleep(amount*multiplier[unit])
    await ctx.guild.unban(member)


@client.command(help='This command unbans any banned member.')
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return


@client.command(help='By default clears 5 messages. Use `.clear (amount)` instead to clear any amount of messages.')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


async def ch_pr():
    await client.wait_until_ready()

    statuses = [f'on {len(client.guilds)} servers', 'Demons', '.help [for help]', '.play']

    while not client.is_closed():
        status = random.choice(statuses)

        await client.change_presence(activity=discord.Game(name=status))

        await asyncio.sleep(3)

client.loop.create_task(ch_pr())


@client.command()
async def load(ctx, extension):
    await ctx.send(f'{extension} is loaded.')
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    await ctx.send(f'{extension} is unloaded.')
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    await ctx.send(f'{extension} is reloaded.')
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.command(aliases=['hiMe', 'test'], help='You can ask any Yes/No question to the bot using this command.')
async def askme(ctx, *, questions):
    responses = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes - definitely.',
                 'As I see it, yes.',
                 'Most likely.',
                 'yes.',
                 "I think it's possible.",
                 'Signs point to yes.',
                 'Ask again later.',
                 'My reply is no.',
                 'My instincts say no.',
                 'Cannot predict now',
                 'Very doubtful',
                 'Better not tell you now.',
                 "I think it's not possible",
                 "Don't count on it",
                 'Try hard. You will be successful']
    await ctx.send(f'Question: {questions}\nAnswer: {random.choice(responses)}')


@client.command(name='die', help='This command returns some response from the bot.')
async def die(ctx):
    responses = ['Why have you brought my short life to an end?!',
                 'I could have done so much more!...',
                 "I have a family. Please don't kill me."]
    await ctx.send(random.choice(responses))


@client.command(name='credits', help='This command returns the credits.')
async def credits(ctx):
    await ctx.send('I was made by `someone` in his free time.')


# join leave
@client.command(pass_context=True, help='Before using play command use this to join the bot to a voice channel. This command joins the bot to a voice channel.')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send('I joined your voice channel.')
    else:
        await ctx.send('You are not currently in a voice channel.')


@client.command(pass_context=True, help='This command removes the bot from a voice channel.')
async def leave(ctx):
    voicetrue = ctx.author.voice
    mevoicetrue = ctx.guild.me.voice
    # if ctx.voice_client:
    if voicetrue is None:
        return await ctx.send('You are not currently in a voice channel.')
    if mevoicetrue is None:
        return await ctx.send('I am not currently in a voice channel.')
    await ctx.guild.voice_client.disconnect()
    await ctx.send('I left your voice channel.')


@client.command(aliases=['p'], pass_context=True, help='".play song_name" to play any song. Make sure to join the bot to a voice channel before using .play command.')
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f'Now playing `{song.name}`')
    else:
        song = await player.queue(url, search=True)
        await ctx.send(f'Queued `{song.name}`')


@client.command(pass_context=True, help='Pauses the current audio.')
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send('Audio is paused.')
    else:
        await ctx.send('There is no audio currently playing in the voice channel!')


@client.command(pass_context=True, help='Resumes a paused audio.')
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send('Audio is resumed.')
    else:
        await ctx.send('There is no audio currently paused in the voice channel!')


@client.command(pass_context=True, help='Skips the current audio.')
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send('Audio skipped.')


@client.command(pass_context=True, help='Stops the whole queue.')
async def stop(ctx):
    await ctx.guild.voice_client.disconnect()
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()

# Detecting specific words


# @client.event
# async def on_message(message):
#     if message.content == "How are you bot?":
#         await message.channel.send('I am good. How are you?')


client.run('ODU1MzQyMzcyMzU4ODQ4NTcy.YMxFqQ.wp_PkqFNB1u4WQXi2qapAQYZnTo')

# client.run('ODU1MzQyMzcyMzU4ODQ4NTcy.YMxFqQ.wp_PkqFNB1u4WQXi2qapAQYZnTo')
