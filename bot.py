import discord
from discord.ext import commands
import asyncio
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

BONUS_ROLE_IDS = [123456789012345678]  # Replace with real role IDs
YOUR_SERVER_ID = 1334304518736842913

def parse_duration(duration_str):
    try:
        unit = duration_str[-1]
        amount = int(duration_str[:-1])
        if unit == 's':
            return amount
        elif unit == 'm':
            return amount * 60
        elif unit == 'h':
            return amount * 3600
        elif unit == 'd':
            return amount * 86400
        else:
            return None
    except:
        return None

@bot.command()
@commands.has_permissions(administrator=True)
async def giveaway(ctx):
    if ctx.guild is None or ctx.guild.id != YOUR_SERVER_ID:
        await ctx.send("❌ This bot is only available in the official server.")
        return

    def check_author_and_channel(message):
    return (
        message.guild
        and message.guild.id == YOUR_SERVER_ID
        and message.author == ctx.author
        and message.channel == ctx.channel
    )
    try:
        await ctx.send("🎁 What is the **prize**?")
        prize_msg = await bot.wait_for("message", timeout=60.0, check=check_author_and_channel)
        prize = prize_msg.content

        await ctx.send("🕒 What is the **duration**? (e.g. 1h, 30m, 10s)")
        duration_msg = await bot.wait_for("message", timeout=60.0, check=check_author_and_channel)
        duration = parse_duration(duration_msg.content)
        if duration is None:
            return await ctx.send("❌ Invalid duration format.")

        await ctx.send("📄 Enter a short **description**:")
        desc_msg = await bot.wait_for("message", timeout=60.0, check=check_author_and_channel)
        description = desc_msg.content

    except asyncio.TimeoutError:
        return await ctx.send("⏰ You took too long to respond. Giveaway cancelled.")

    giveaway_message = await ctx.send(
        f"🎉 **GIVEAWAY** 🎉\n\n**Prize:** {prize}\n**Description:** {description}\nReact with 🎉 to enter!"
    )
    await asyncio.sleep(1)
    await giveaway_message.add_reaction("🎉")

    await asyncio.sleep(duration)
    message = await ctx.channel.fetch_message(giveaway_message.id)
    users = await message.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    weighted_users = []
    for user in users:
        await asyncio.sleep(0.5)
        member = ctx.guild.get_member(user.id)
        entries = 1
        for role_id in BONUS_ROLE_IDS:
            if discord.utils.get(member.roles, id=role_id):
                entries += 1
        weighted_users.extend([user] * entries)

    if weighted_users:
        winner = random.choice(weighted_users)
        await ctx.send(f"🎉 Congratulations {winner.mention}! You won **{prize}**!")
    else:
        await ctx.send("😢 No valid entries.")

@bot.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, message_id: int):
    if ctx.guild is None or ctx.guild.id != YOUR_SERVER_ID:
        return await ctx.send("❌ This bot is only available in the official server.")

    try:
        message = await ctx.channel.fetch_message(message_id)
        users = await message.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]

        weighted_users = []
        for user in users:
            await asyncio.sleep(0.5)
            member = ctx.guild.get_member(user.id)
            entries = 1
            for role_id in BONUS_ROLE_IDS:
                if discord.utils.get(member.roles, id=role_id):
                    entries += 1
            weighted_users.extend([user] * entries)

        if weighted_users:
            winner = random.choice(weighted_users)
            await ctx.send(f"🔁 New winner: {winner.mention}! Congratulations!")
        else:
            await ctx.send("😢 No valid entries to reroll.")
    except:
        await ctx.send("❌ Could not reroll. Please ensure the message ID is correct.")

bot.run(os.getenv("YOUR_BOT_TOKEN"))
