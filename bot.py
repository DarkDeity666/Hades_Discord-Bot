import discord
from discord.ext import tasks
from discord import app_commands
import json
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents and bot initialization
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

bot = MyBot()

# Load or initialize economy data
DATA_FILE = "./data/economy.json"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Logging utility
def log_activity(guild, message):
    logs_category_name = "━━╴Logs╶━━"
    log_channel_name = "hermes-log"
    
    # Get the category and channel
    logs_category = discord.utils.get(guild.categories, name=logs_category_name)
    if not logs_category:
        return
    log_channel = discord.utils.get(logs_category.text_channels, name=log_channel_name)
    if log_channel:
        bot.loop.create_task(log_channel.send(message))

# DM welcome message
async def send_welcome_dm(user):
    try:
        await user.send(
            "Welcome to Hermes Economy Simulator!\n\n"
            "**How to Play:**\n"
            "- Use `/work` to earn money.\n"
            "- Gamble your earnings with `/gamble [amount]`.\n"
            "- Gift money to others with `/gift [@user] [amount]`.\n"
            "- View leaderboards with `/leaderboard`.\n"
            "- Random events can happen with `/event`.\n\n"
            "**Rules:**\n"
            "- No cheating or exploiting bugs.\n"
            "- Play fair and have fun!"
        )
    except discord.Forbidden:
        pass  # Cannot send a DM to the user

# Weekly leaderboard announcement
@tasks.loop(weeks=1)
async def post_weekly_leaderboard():
    for guild in bot.guilds:
        category_name = "━━╴Hermes- Economy ╶━━"
        channel_name = "⫸▕▏weekly-leaderboard"

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            continue
        channel = discord.utils.get(category.text_channels, name=channel_name)
        if not channel:
            continue

        data = load_data()
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)
        leaderboard = "\n".join([f"<@{user}>: ${info['balance']}" for user, info in sorted_users[:10]])
        await channel.send(f"**Weekly Leaderboard:**\n{leaderboard}")

# Monthly leaderboard announcement
@tasks.loop(weeks=4)
async def post_monthly_leaderboard():
    for guild in bot.guilds:
        category_name = "━━╴Hermes- Economy ╶━━"
        channel_name = "⫸▕▏monthly-leaderboard"

        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            continue
        channel = discord.utils.get(category.text_channels, name=channel_name)
        if not channel:
            continue

        data = load_data()
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)
        leaderboard = "\n".join([f"<@{user}>: ${info['balance']}" for user, info in sorted_users[:10]])
        top_5_rewards = 50  # Example bonus credits for top 5 users

        for user, _ in sorted_users[:5]:
            if user in data:
                data[user]["balance"] += top_5_rewards

        save_data(data)
        await channel.send(
            f"**Monthly Leaderboard:**\n{leaderboard}\n\n"
            f"The top 5 users received a bonus of ${top_5_rewards} each!"
        )

# Slash Commands

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    post_weekly_leaderboard.start()
    post_monthly_leaderboard.start()
    await bot.tree.sync()

@bot.tree.command(name="balance", description="Check your balance.")
async def balance(interaction: discord.Interaction):
    """Check your balance."""
    data = load_data()
    user = str(interaction.user.id)
    if user not in data:
        data[user] = {"balance": 0}
        save_data(data)
        await send_welcome_dm(interaction.user)
    balance = data[user]["balance"]
    await interaction.response.send_message(f"{interaction.user.name}, you have ${balance}!")

    # Log the activity
    log_activity(interaction.guild, f"{interaction.user.name} checked their balance.")

@bot.tree.command(name="work", description="Earn money through work.")
async def work(interaction: discord.Interaction):
    """Earn money through work."""
    data = load_data()
    user = str(interaction.user.id)
    if user not in data:
        data[user] = {"balance": 0}
        await send_welcome_dm(interaction.user)
    amount = random.randint(10, 50)
    data[user]["balance"] += amount
    save_data(data)
    await interaction.response.send_message(f"{interaction.user.name}, you worked hard and earned ${amount}!")

    # Log the activity
    log_activity(interaction.guild, f"{interaction.user.name} worked and earned ${amount}.")

@bot.tree.command(name="gamble", description="Gamble an amount of money.")
async def gamble(interaction: discord.Interaction, amount: int):
    """Gamble an amount of money."""
    data = load_data()
    user = str(interaction.user.id)
    if user not in data:
        data[user] = {"balance": 0}
        await send_welcome_dm(interaction.user)
    
    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount to gamble.", ephemeral=True)
        return
    
    if data[user]["balance"] < amount:
        await interaction.response.send_message("You don't have enough money to gamble that amount.", ephemeral=True)
        return
    
    # Gamble logic
    outcome = random.choice(["win", "lose"])
    if outcome == "win":
        winnings = amount * 2
        data[user]["balance"] += winnings - amount
        result_message = f"Congratulations, {interaction.user.name}! You gambled ${amount} and won ${winnings}!"
    else:
        data[user]["balance"] -= amount
        result_message = f"Sorry, {interaction.user.name}, you gambled ${amount} and lost it all."

    save_data(data)
    await interaction.response.send_message(result_message)

    # Log the activity
    log_activity(interaction.guild, f"{interaction.user.name} gambled ${amount} and {'won' if outcome == 'win' else 'lost'}.")

@bot.tree.command(name="gift", description="Gift money to another user.")
async def gift(interaction: discord.Interaction, member: discord.Member, amount: int):
    """Gift money to another user."""
    if member == interaction.user:
        await interaction.response.send_message("You can't gift money to yourself.", ephemeral=True)
        return

    data = load_data()
    sender = str(interaction.user.id)
    receiver = str(member.id)

    if sender not in data:
        data[sender] = {"balance": 0}
        await send_welcome_dm(interaction.user)

    if receiver not in data:
        data[receiver] = {"balance": 0}
        await send_welcome_dm(member)

    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount to gift.", ephemeral=True)
        return

    if data[sender]["balance"] < amount:
        await interaction.response.send_message("You don't have enough money to gift that amount.", ephemeral=True)
        return

    # Gift logic
    data[sender]["balance"] -= amount
    data[receiver]["balance"] += amount
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name} gifted ${amount} to {member.name}!")

    # Log the activity
    log_activity(interaction.guild, f"{interaction.user.name} gifted ${amount} to {member.name}.")

@bot.tree.command(name="leaderboard", description="View the top 10 users by balance.")
async def leaderboard(interaction: discord.Interaction):
    """View the top 10 users by balance."""
    data = load_data()
    if not data:
        await interaction.response.send_message("No data available yet.")
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)
    leaderboard = "\n".join(
        [f"{index + 1}. <@{user}>: ${info['balance']}" for index, (user, info) in enumerate(sorted_users[:10])]
    )

    await interaction.response.send_message(f"**Leaderboard:**\n{leaderboard}")

    # Log the activity
    log_activity(interaction.guild, f"{interaction.user.name} viewed the leaderboard.")

bot.run(TOKEN)
