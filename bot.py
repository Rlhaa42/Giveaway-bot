import discord
from discord.ext import commands
from discord import app_commands, ui, Interaction
import asyncio
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
BONUS_ROLE_IDS = []
giveaways = {}

def parse_duration(duration_str):
    try:
        duration_str = duration_str.strip().lower().replace(" ", "")
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
    except Exception as e:
        print(f"Duration parse error: {e}")
        return None

class GiveawayModal(ui.Modal, title="Create a Giveaway"):
    prize = ui.TextInput(label="Prize", placeholder="Enter the prize", required=True)
    duration = ui.TextInput(label="Duration", placeholder="e.g., 10s, 30m, 1h", required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_duration(self.duration)
        if seconds is None:
            return await interaction.response.send_message("❌ Invalid duration format. Please use formats like 10s, 5m, 1h, 2d.", ephemeral=True)

        embed = discord.Embed(
            title="🎉 Giveaway 🎉",
            description=f"**Prize:** {self.prize}\n**Description:** {self.description}\nReact with 🎉 to enter!",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Ends in: {self.duration}")
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction("🎉")

        giveaways[message.id] = {
            "prize": self.prize,
            "channel_id": interaction.channel.id,
            "message_id": message.id,
            "ended": False
        }

        await interaction.response.send_message("✅ Giveaway started!", ephemeral=True)

        await asyncio.sleep(seconds)

        msg = await interaction.channel.fetch_message(message.id)
        users = await msg.reactions[0].users().flatten()
        users = [u for u in users if not u.bot]

        weighted_users = []
        for user in users:
            member = interaction.guild.get_member(user.id)
            entries = 1
            for role_id in BONUS_ROLE_IDS:
                if discord.utils.get(member.roles, id=role_id):
                    entries += 1
            weighted_users.extend([user] * entries)

        if weighted_users:
            winner = random.choice(weighted_users)
            await interaction.channel.send(f"🎉 Congratulations {winner.mention}! You won **{self.prize}**!")
        else:
            await interaction.channel.send("😢 No valid entries.")
        giveaways[message.id]["ended"] = True

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        await bot.tree.sync(guild=discord.Object(id=1334304518736842913))
        print("Synced commands to the server.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(guild=discord.Object(id=1334304518736842913), name="create_giveaway", description="Create a new giveaway with a modal form")
async def create_giveaway(interaction: discord.Interaction):
    await interaction.response.send_modal(GiveawayModal())

@bot.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, message_id: int):
    if message_id not in giveaways or not giveaways[message_id]["ended"]:
        return await ctx.send("❌ Invalid or active giveaway ID.")

    giveaway = giveaways[message_id]
    channel = bot.get_channel(giveaway["channel_id"])
    message = await channel.fetch_message(giveaway["message_id"])
    users = await message.reactions[0].users().flatten()
    users = [u for u in users if not u.bot]

    weighted_users = []
    for user in users:
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

bot.run(os.getenv("YOUR_BOT_TOKEN"))

