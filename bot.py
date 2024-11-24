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

# File paths
DATA_FILE = "./data/economy.json"

# Ensure the data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# Load and save economy data
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Logging utility
def log_activity(guild, message):
    logs_category_name = "━━╴Logs╶━━"
    log_channel_name = "hermes-log"

    logs_category = discord.utils.get(guild.categories, name=logs_category_name)
    if not logs_category:
        return
    log_channel = discord.utils.get(logs_category.text_channels, name=log_channel_name)
    if log_channel:
        bot.loop.create_task(log_channel.send(message))

# Utility to initialize user data
def initialize_user(data, user_id):
    if user_id not in data:
        data[user_id] = {
            "balance": 0,
            "bank": 0,
            "daily_streak": 0,
            "last_daily": None,
            "loan": 0,
            "loan_interest_rate": 0.1,  # 10% daily interest
            "taxes_due": 0
        }
        save_data(data)


# Daily Login Rewards
@bot.tree.command(name="daily", description="Claim your daily login reward.")
async def daily(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)
    
    user_data = data[user_id]
    streak_bonus = 20 * user_data["daily_streak"]  # $20 per day streak
    reward = 20 + streak_bonus

    user_data["balance"] += reward
    user_data["daily_streak"] += 1
    save_data(data)

    await interaction.response.send_message(
        f"{interaction.user.name}, you claimed your daily reward of ${reward}! "
        f"(Current streak: {user_data['daily_streak']} days)"
    )
    log_activity(interaction.guild, f"{interaction.user.name} claimed their daily reward of ${reward}.")

# Shop System
@bot.tree.command(name="shop", description="View and purchase virtual items.")
async def shop(interaction: discord.Interaction):
    shop_items = {
        "lottery_ticket": {"name": "Lottery Ticket", "price": 50, "description": "Chance to win $500."},
        "multiplier_boost": {"name": "Multiplier Boost", "price": 200, "description": "Doubles work rewards for 1 hour."},
        "lucky_charm": {"name": "Lucky Charm", "price": 100, "description": "Increases gambling win chances."}
    }

    shop_list = "\n".join([f"{key}: {item['name']} - ${item['price']} ({item['description']})" for key, item in shop_items.items()])
    await interaction.response.send_message(f"**Shop Items:**\n{shop_list}")

# Bank System
@bot.tree.command(name="deposit", description="Deposit money into your bank account.")
async def deposit(interaction: discord.Interaction, amount: int):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount to deposit.", ephemeral=True)
        return

    if data[user_id]["balance"] < amount:
        await interaction.response.send_message("You don't have enough money to deposit that amount.", ephemeral=True)
        return

    data[user_id]["balance"] -= amount
    data[user_id]["bank"] += amount
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you successfully deposited ${amount} into your bank account.")
    log_activity(interaction.guild, f"{interaction.user.name} deposited ${amount} into their bank account.")

@bot.tree.command(name="withdraw", description="Withdraw money from your bank account.")
async def withdraw(interaction: discord.Interaction, amount: int):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount to withdraw.", ephemeral=True)
        return

    if data[user_id]["bank"] < amount:
        await interaction.response.send_message("You don't have enough money in the bank to withdraw that amount.", ephemeral=True)
        return

    data[user_id]["balance"] += amount
    data[user_id]["bank"] -= amount
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you successfully withdrew ${amount} from your bank account.")
    log_activity(interaction.guild, f"{interaction.user.name} withdrew ${amount} from their bank account.")

@bot.tree.command(name="interest", description="Check your bank interest.")
async def interest(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    # Calculate interest (e.g., 5% of the bank balance)
    interest = data[user_id]["bank"] * 0.05
    data[user_id]["balance"] += interest
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you earned ${interest} in interest from your bank balance!")
    log_activity(interaction.guild, f"{interaction.user.name} earned ${interest} in bank interest.")

# Tax System
@bot.tree.command(name="checktax", description="Check your tax dues.")
async def checktax(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    taxes_due = data[user_id]["taxes_due"]
    await interaction.response.send_message(f"{interaction.user.name}, you owe ${taxes_due} in taxes.")

@bot.tree.command(name="paytax", description="Pay your taxes.")
async def paytax(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    taxes_due = data[user_id]["taxes_due"]
    if taxes_due == 0:
        await interaction.response.send_message(f"{interaction.user.name}, you don't owe any taxes.")
        return

    if data[user_id]["balance"] < taxes_due:
        await interaction.response.send_message(f"{interaction.user.name}, you don't have enough balance to pay your taxes.", ephemeral=True)
        return

    data[user_id]["balance"] -= taxes_due
    data[user_id]["taxes_due"] = 0  # Tax cleared
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you successfully paid ${taxes_due} in taxes.")
    log_activity(interaction.guild, f"{interaction.user.name} paid ${taxes_due} in taxes.")

# Loans System
@bot.tree.command(name="loan", description="Take out a loan.")
async def loan(interaction: discord.Interaction, amount: int):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount for the loan.", ephemeral=True)
        return

    # Loan logic: User can take a loan up to a certain limit (e.g., 1000)
    max_loan = 1000
    if data[user_id]["loan"] > max_loan:
        await interaction.response.send_message(f"{interaction.user.name}, you already have the maximum loan limit.", ephemeral=True)
        return

    if data[user_id]["loan"] + amount > max_loan:
        await interaction.response.send_message(f"{interaction.user.name}, you cannot take a loan greater than ${max_loan}.", ephemeral=True)
        return

    # Issue the loan
    data[user_id]["loan"] += amount
    data[user_id]["balance"] += amount
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you have taken a loan of ${amount}.")
    log_activity(interaction.guild, f"{interaction.user.name} took a loan of ${amount}.")

@bot.tree.command(name="repayloan", description="Repay part of your loan.")
async def repayloan(interaction: discord.Interaction, amount: int):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    if amount <= 0:
        await interaction.response.send_message("Please enter a positive amount to repay.", ephemeral=True)
        return

    if data[user_id]["loan"] < amount:
        await interaction.response.send_message(f"{interaction.user.name}, you don't owe that much on your loan.", ephemeral=True)
        return

    if data[user_id]["balance"] < amount:
        await interaction.response.send_message(f"{interaction.user.name}, you don't have enough balance to repay that amount.", ephemeral=True)
        return

    data[user_id]["loan"] -= amount
    data[user_id]["balance"] -= amount
    save_data(data)

    await interaction.response.send_message(f"{interaction.user.name}, you successfully repaid ${amount} of your loan.")
    log_activity(interaction.guild, f"{interaction.user.name} repaid ${amount} of their loan.")

@bot.tree.command(name="loanstatus", description="Check your current loan status.")
async def loanstatus(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    loan_balance = data[user_id]["loan"]
    await interaction.response.send_message(f"{interaction.user.name}, your current loan balance is ${loan_balance}.")


@tasks.loop(hours=24)
async def daily_interest_task():
    data = load_data()
    for user_id, user_data in data.items():
        # Bank interest
        bank_balance = user_data["bank"]
        if bank_balance > 0:
            interest = bank_balance * 0.05  # 5% interest
            user_data["balance"] += interest
            log_message = f"User {user_id} earned ${interest:.2f} interest on their bank balance."

        # Loan interest
        loan_balance = user_data["loan"]
        if loan_balance > 0:
            loan_interest = loan_balance * user_data["loan_interest_rate"]
            user_data["loan"] += loan_interest
            log_message = f"User {user_id}'s loan increased by ${loan_interest:.2f} due to interest."

        save_data(data)
        # Post logs to the log channel
        for guild in bot.guilds:
            log_activity(guild, log_message)

@bot.tree.command(name="deposit", description="Deposit money into your bank account with interest benefits.")
async def deposit(interaction: discord.Interaction, amount: int):
    data = load_data()
    user_id = str(interaction.user.id)
    initialize_user(data, user_id)

    if amount <= 0:
        await interaction.response.send_message("Enter a positive amount to deposit.", ephemeral=True)
        return

    if data[user_id]["balance"] < amount:
        await interaction.response.send_message("Insufficient funds to deposit.", ephemeral=True)
        return

    # Deposit money into the bank
    data[user_id]["balance"] -= amount
    data[user_id]["bank"] += amount
    save_data(data)

    await interaction.response.send_message(f"Deposited ${amount} to your bank account. Your money is safe and earns interest!")
    log_activity(interaction.guild, f"{interaction.user.name} deposited ${amount} into their bank.")

@tasks.loop(hours=24)
async def loan_status_task():
    data = load_data()
    for user_id, user_data in data.items():
        loan_balance = user_data["loan"]
        if loan_balance > 0:
            log_message = f"User {user_id} has an outstanding loan of ${loan_balance:.2f}."
            for guild in bot.guilds:
                log_activity(guild, log_message)

# Update Rules Command
@bot.tree.command(name="rules", description="View the updated rules.")
async def rules(interaction: discord.Interaction):
    rules_message = (
        "**Hermes Economy Simulator - Rules**\n"
        "- No cheating, exploiting, or abusing bugs.\n"
        "- Respect all other players and staff.\n"
        "- No spamming or excessive messaging.\n"
        "- Do not share personal or sensitive information.\n"
        "- Be mindful of your balance, taxes, loans, and spending.\n\n"
        "**Game Features:**\n"
        "- Earn money by working, gambling, and completing events.\n"
        "- Check your balance, work, gamble, and give gifts to others.\n"
        "- Visit the shop to buy virtual items.\n"
        "- Deposit and withdraw money from your bank.\n"
        "- Pay taxes and take out loans with interest.\n"
        "- Check leaderboards and claim your daily rewards.\n"
    )
    await interaction.response.send_message(rules_message)

bot.run(TOKEN)
