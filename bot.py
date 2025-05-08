import discord
from discord.ext import commands
from discord import app_commands, ui
import asyncio
import random
import os
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
BONUS_ROLE_IDS = []

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
        return None
    except:
        return None

def format_time(seconds):
    return str(timedelta(seconds=seconds))

class GiveawayModal(ui.Modal, title="Create a Giveaway"):
    prize = ui.TextInput(label="Prize", placeholder="Enter the prize", required=True)
    duration = ui.TextInput(label="Duration", placeholder="e.g., 10s, 1m, 1h", required=True)
    winners = ui.TextInput(label="Number of winners", placeholder="e.g., 1, 3", required=True)
    description = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        seconds = parse_duration(str(self.duration))
        if seconds is None:
            await interaction.response.send_message("❌ Invalid duration format. Use 10s, 5m, 1h, 2d.", ephemeral=True)
            return

        try:
            winner_count = max(1, int(str(self.winners).strip()))
        except ValueError:
            await interaction.response.send_message("❌ Number of winners must be a valid number.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🎉 Giveaway 🎉",
            description=f"**Prize:** {self.prize}\n**Winners:** {winner_count}\n**Description:** {self.description}\nReact with 🎉 to enter!",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Ends in: {format_time(seconds)}")
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction("🎉")

        await interaction.followup.send("✅ Giveaway started!", ephemeral=True)

        async def update_timer():
            remaining = seconds
            while remaining > 0:
                await asyncio.sleep(10)
                remaining -= 10
                try:
                    embed.set_footer(text=f"Ends in: {format_time(remaining)}")
                    await message.edit(embed=embed)
                except Exception as e:
                    print(f"Timer update failed: {e}")

        async def finish_giveaway():
            await asyncio.sleep(seconds)
            try:
                msg = await interaction.channel.fetch_message(message.id)
                users = [user async for user in msg.reactions[0].users() if not user.bot]

                weighted_users = []
                for user in users:
                    member = interaction.guild.get_member(user.id)
                    if member is None:
                        continue
                    entries = 1
                    for role_id in BONUS_ROLE_IDS:
                        if discord.utils.get(member.roles, id=role_id):
                            entries += 1
                    weighted_users.extend([user] * entries)

                unique_users = list(set(weighted_users))
                if unique_users:
                    winners = random.sample(unique_users, min(winner_count, len(unique_users)))
                    mentions = ", ".join(w.mention for w in winners)
                    await interaction.channel.send(f"🎉 Congratulations {mentions}! You won **{self.prize}**!")
                else:
                    await interaction.channel.send("😢 No valid entries.")
            except Exception as e:
                print(f"Error during winner pick: {e}")
                await interaction.channel.send(f"❌ Could not finish giveaway: `{e}`")

        bot.loop.create_task(update_timer())
        bot.loop.create_task(finish_giveaway())

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced globally.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@bot.tree.command(name="create_giveaway", description="Start a giveaway using a popup form")
async def create_giveaway(interaction: discord.Interaction):
    await interaction.response.send_modal(GiveawayModal())

bot.run(os.getenv("YOUR_BOT_TOKEN"))

