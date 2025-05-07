# Accountability Bot 
<p align="left">
<a href="https://medium.com/@y.zeynab1" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/medium.svg" alt="@y.zeynab1" height="30" width="40" /></a>
</p>

**Welcome to my accountability bot** 

As they say ***Accountability is the key to progress*** and this bot is here to help you stay on track!<br>

Designed with automation and consistency in mind, this Discord bot is your ultimate companion for crushing your goals, building habits and staying motivated.

The bot interacts with Discord's API and requires a bot token from the **Discord Developer Portal**

##  **Features**
1. **Weekly Accountability Polls**:
   - Start a poll to let participants opt into weekly accountability groups.
   - Automatically create threads for participants to collaborate and share progress.
![Image](https://github.com/user-attachments/assets/7e09c702-0abe-4483-86af-8821f854d72e)

1. **Motivational Messages**:
   - Midweek nudges and end-of-week recaps.
![Image](https://github.com/user-attachments/assets/440cba7f-19bd-43f4-9f7f-e265914df77e)

1. **Thread Management**:
   - Automatically organises users into small groups.
   - Creates a space for participants to interact and stay on track.
  ![Image](https://github.com/user-attachments/assets/f4a1306d-3824-406f-8582-270ec4056d21)

---

##  **How It Works**
1. Use the `!weeklypoll` command to start a new week of accountability. Automated with a zapier integration.
2. Participants opt-in by reacting to the poll.
3. Threads are created automatically, and motivational messages are scheduled throughout the week.
4. Watch as your community stays on track and levels up their consistency! 💪

---
### Requirements
- Python 3.8+
- `discord.py` (v2.0 or higher)
- `python-dotenv`
- `schedule`
- JSON (used for persistent storage in `poll_state.json`)
  

> [!IMPORTANT]  
> **Messages Setup**: The `messages.py` file is crucial for the bot to send messages (midweek, end-of-week and initial poll messages). You need to manually create this file in your project’s root directory as described above.<br>
> **Permissions**: Make sure the bot has the appropriate permissions to send messages, create threads, and react in the Discord server you intend to use it in. <br>
> **Persistent Storage**: The bot saves the state of the threads to a file called `poll_state.json` in the project directory. Ensure this file is not deleted, as it tracks active accountability threads. <br>
> **.env**- add you discord token here  `DISCORD_BOT_TOKEN=your_discord_bot_token` <br>
>  Run the bot`python index.py`

---

## How to Host the Bot

If you wish to host the bot yourself, I recommend using [Cybrance](https://cybrancee.com/client/aff.php?aff=494) . It’s an easy-to-use platform that allows you to deploy your bot quickly and keep it running 24/7. Be sure to follow the platform’s instructions to properly deploy your bot, and ensure that your bot token is stored securely.

