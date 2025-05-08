# Discord Giveaway Bot

This bot allows administrators to create giveaways with a prize, duration, and description. It supports rerolling and extra entries for users with specific roles.

## Features

- Restricted to one server
- Administrator-only commands
- Custom prize, duration, and description
- Bonus entries for special roles

## Setup

1. Replace `YOUR_BOT_TOKEN` in `bot.py` with your bot's token.
2. Replace `YOUR_SERVER_ID` with your server's ID.
3. Replace `BONUS_ROLE_IDS` with any role IDs that should get extra entries.

## Hosting

Use a free service like [Render](https://render.com) to host the bot 24/7.

- Build Command: `pip install -r requirements.txt`
- Start Command: `python bot.py`

Make sure to add your token as an environment variable on Render.
