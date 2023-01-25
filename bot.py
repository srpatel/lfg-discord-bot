import os
import asyncio
import discord
import random
import functools
from discord.ext import commands
from datetime import datetime

# Ensure all prints are flushing
print = functools.partial(print, flush=True)

TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Client()

sent_message = None
sent_time = None
boops = []

timeout = 1800
boop_timeout = 600
users_needed = 4

async def timeout_rooms():
    global sent_message
    global sent_time
    global timeout
    global boop_timeout
    global boops

    while(True):
        now = datetime.now()
        if sent_message != None and sent_time != None:
            duration = now - sent_time
            if duration.total_seconds() > timeout:
                # Timeout this role call
                await sent_message.delete()
                sent_message = None
                sent_time = None
        # Delete old boops
        for boop in boops[:]:
            msg = boop[0]
            when = boop[1]
            if (now - when).total_seconds() > boop_timeout:
                await boop[0].delete()
                boops.remove(boop)
        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    guild = bot.guilds[0]
    print(f'{guild.name} {guild.id}')
    bot.loop.create_task(timeout_rooms())

@bot.event
async def on_message_delete(message):
    global sent_message
    global sent_time
    if sent_message == message:
        sent_message = None
        sent_tile = None
        print(f'Roll call deleted')

@bot.event
async def on_message(message):
    global sent_message
    global sent_time

    channel = message.channel

    # Only in lfg channel
    if channel.name != 'bot-testing' and channel.name != 'looking-for-game':
        return

    # Ignore bot message
    if message.author == bot.user:
        return

    # If the other message hasn't expired, delete this message!
    if sent_message != None:
        await message.delete()
        print(f'Message deleted because of active roll call')
    else:
        sent_message = message
        sent_time = datetime.now()
        print(f'New roll call posted by {message.author.name}')
    
@bot.event
async def on_reaction_add(reaction, user):
    global sent_message
    global boops
    global users_needed
    # Get list of reactions...
    if reaction.message == sent_message:
        emoted = {}
        emoted[sent_message.author.id] = sent_message.author
        for reaction in reaction.message.reactions:
            reactors = await reaction.users().flatten()
            for u in reactors:
                emoted[u.id] = u
        if len(emoted) >= users_needed:
            # Boop them!
            mentions = []
            for user in emoted.values():
                mentions.append(user.mention)
                if len(mentions) == users_needed:
                    break
            boopString = random.choice(["Boop!", "Nudge!", "Prod!", "Oi!", "Wake up!", "Get lively!", "Look busy!", "Grand Wodka or bust!", "Time to shine!"])
            boop = await sent_message.channel.send(f'{boopString} {" ".join(mentions)}')
            await sent_message.delete()
            print(f'Boop sent for {" ".join(mentions)}')
            sent_message = None
            sent_time = None
            boops.append([boop, datetime.now()])

bot.run(TOKEN)
