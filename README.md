
# Hermes Economy Bot

**Hermes Economy Bot** is a Discord bot designed to simulate a virtual economy for your Discord server. Players can earn, spend, save, and manage virtual money while engaging in various activities such as claiming daily rewards, purchasing items, paying taxes, and handling loans.



## Features

### 🎁 **Daily Rewards**
Claim your daily rewards and increase your streak for bigger bonuses!

### 🛒 **Shop System**
Buy virtual items with unique benefits:
- Lottery Tickets
- Multiplier Boosts
- Lucky Charms

### 🏦 **Banking System**
- Deposit and withdraw money from your bank account.
- Earn interest on your bank balance daily.

### 📊 **Tax and Loan Management**
- Pay taxes to keep your virtual economy on track.
- Take out loans and repay them with interest.

### 📈 **Automated Daily Updates**
- Automatic daily interest on bank savings.
- Loan balances increase with daily interest.

### 📜 **Logs and Rules**
- Keep a track of all activities in a designated log channel.
- View detailed rules and guidelines for the game.



## Commands

### 🎮 **Economy Commands**
- `/daily` - Claim your daily login reward.
- `/shop` - View and purchase virtual items.
- `/deposit <amount>` - Deposit money into your bank account.
- `/withdraw <amount>` - Withdraw money from your bank account.
- `/interest` - Check your bank interest earnings.

### 💰 **Loan and Tax Commands**
- `/loan <amount>` - Take out a loan.
- `/repayloan <amount>` - Repay a portion of your loan.
- `/loanstatus` - Check your current loan status.
- `/checktax` - View your tax dues.
- `/paytax` - Pay your taxes.

### 🛠️ **Utility Commands**
- `/rules` - View the updated rules and guidelines.



## Setup Instructions

### Prerequisites
- Python 3.8+
- A Discord bot token
- `discord.py` library
- `.env` file to store the bot token
- `dotenv` and `discord-ext-tasks` installed

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Hermes-Economy-Bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add your bot token:
   ```
   DISCORD_TOKEN=your-bot-token
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```



## Configuration

### File Structure
- **data/economy.json**: Stores user data (balances, loans, streaks, etc.).
- **.env**: Stores environment variables like the bot token.

### Log Channel Setup
Create a category called `━━╴Logs╶━━` and a text channel named `hermes-log` to track activities.


## Future Enhancements
- Add gambling mechanics like slots and blackjack.
- Leaderboards for top balances or streaks.
- Guild-wide taxes and events.
- User trading and gifting features.



## Troubleshooting

1. **Bot not starting?**
   - Ensure you’ve set up your `.env` file correctly with the bot token.
   - Verify that all dependencies are installed.

2. **Missing logs?**
   - Ensure the logs category and channel exist in your server.

3. **Commands not working?**
   - Check bot permissions and ensure it can manage messages and interact with application commands.



## License
This project is open-source and available under the [MIT License](LICENSE).

## Support
For issues or suggestions, open an issue in the repository or contact the bot developer.

Happy Simulating! 😊
