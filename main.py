import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import discord
import random
from datetime import datetime, timedelta
import logging
import schedule
import time
import threading
import json

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents for bot permissions
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Persistent storage for threads and poll information
POLL_STATE_FILE = 'poll_state.json'

def keep_bot_awake():
    """Run a background thread to periodically log messages and prevent idling."""
    while True:
        try:
            # Simple log message to show bot is alive
            print(f"🤖 Bot is alive and running at {datetime.now()}")
            
            # Sleep for 5     
            time.sleep(5 * 60)  # 5 minutes
        except Exception as e:
            print(f"Heartbeat thread error: {e}")

def save_poll_state(threads):
    """Save poll state to a persistent file."""
    state = {
        'thread_ids': threads,
        'last_updated': datetime.now().isoformat()
    }
    with open(POLL_STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_poll_state():
    """Load poll state from persistent file."""
    try:
        with open(POLL_STATE_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                state = json.loads(content)
                thread_ids = state.get('thread_ids', [])
                if not thread_ids:
                    logging.warning("⚠ poll_state.json found, but no thread IDs were saved.")
                return thread_ids
            else:
                logging.warning("⚠ poll_state.json is empty. Starting fresh.")
                return []
    except FileNotFoundError:
        logging.warning("⚠ poll_state.json not found. Starting fresh.")
        return []
    except json.JSONDecodeError:
        logging.error("⚠ Invalid JSON in poll_state.json. Starting fresh.")
        return []

# Import messages
from messages import MIDWEEK_MESSAGES, END_OF_WEEK_MESSAGES, INITIAL_POLL_MESSAGE

# List to keep track of created threads
created_threads_ids = load_poll_state()

# Scheduled message sender
async def send_midweek_messages():
    """Send midweek messages to existing threads."""
    if not created_threads_ids:
        logging.warning("No threads found for midweek messages")
        return

    for thread_id in created_threads_ids:
        try:
            thread = bot.get_channel(thread_id)
            if thread:
                midweek_message = random.choice(MIDWEEK_MESSAGES)
                message = await thread.send(midweek_message)
                await message.add_reaction("🔼")  # reaction for participants to upvote
                logging.info(f"Sent midweek message to thread {thread.name}")
            else:
                logging.warning(f"Thread {thread_id} not found")
        except Exception as e:
            logging.error(f"Error sending midweek message to thread {thread_id}: {e}")

async def send_end_of_week_messages():
    """Send end-of-week messages to existing threads."""
    if not created_threads_ids:
        logging.warning("No threads found for end-of-week messages")
        return

    for thread_id in created_threads_ids:
        try:
            thread = bot.get_channel(thread_id)
            if thread:
                end_of_week_message = random.choice(END_OF_WEEK_MESSAGES).format(
                    user_mentions=", ".join([member.mention for member in thread.members])
                )
                await thread.send(end_of_week_message)
                logging.info(f"Sent end-of-week message to thread {thread.name}")
            else:
                logging.warning(f"Thread {thread_id} not found")
        except Exception as e:
            logging.error(f"Error sending end-of-week message to thread {thread_id}: {e}")

async def lock_old_threads():
    """Lock and archive the previous week's threads."""
    global created_threads_ids  # Use the stored thread IDs
    
    if not created_threads_ids:
        logging.warning("No threads found to lock and archive")
        return

    for thread_id in created_threads_ids:
        try:
            thread = bot.get_channel(thread_id)
            if thread and isinstance(thread, discord.Thread):
                await thread.edit(archived=True, locked=True)
                logging.info(f"Archived and locked thread: {thread.name}")
        except Exception as e:
            logging.error(f"Error archiving thread {thread_id}: {e}")

    # Clear the list after archiving
    created_threads_ids.clear()
    save_poll_state(created_threads_ids)


# Scheduling thread function
def schedule_thread():
    """Run the scheduler in a separate thread."""

    # Production schedule (Uncomment these for actual deployment)
    schedule.every().thursday.at("09:00").do(lambda: asyncio.run_coroutine_threadsafe(send_midweek_messages(), bot.loop))
    schedule.every().sunday.at("18:00").do(lambda: asyncio.run_coroutine_threadsafe(send_end_of_week_messages(), bot.loop))
    schedule.every().monday.at("08:00").do(lambda: asyncio.run_coroutine_threadsafe(lock_old_threads(), bot.loop))

    while True:
        schedule.run_pending()
        time.sleep(1)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    print("✅ Bot is ready and listening for commands!")

    if not created_threads_ids:
        logging.warning("⚠ No previous thread IDs found. This might be expected if the bot was restarted or a new token was used.")
    
    # Start scheduling thread
    threading.Thread(target=schedule_thread, daemon=True).start()
    
    # Start heartbeat thread
    threading.Thread(target=keep_bot_awake, daemon=True).start()

@bot.event
async def on_message(message):
    # Allow processing messages from other bots (e.g., Zapier)
    if message.author.bot:
        if message.content.strip() == "!weeklypoll":
            ctx = await bot.get_context(message)
            await bot.invoke(ctx)
        return
    await bot.process_commands(message)

# check to ensure commands only work in the right channel 
@bot.check
async def globally_block_commands(ctx):
    """Ensure commands are only allowed in the main channel."""
    if ctx.channel.name != "🗳┃poll"
        return False
    return True

# Handle command errors gracefully
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully."""
    if isinstance(error, commands.CheckFailure):
        logging.info(f"Ignored command in {ctx.channel.name}")
    else:
        logging.error(f"Unexpected error: {error}")

# Diagnostic command to check current threads
@bot.command()
async def checkthreads(ctx):
    """Check current threads and their status"""
    if created_threads_ids:
        await ctx.send(f"Current tracked thread IDs: {created_threads_ids}")
        for thread_id in created_threads_ids:
            thread = bot.get_channel(thread_id)
            if thread:
                await ctx.send(f"Thread {thread_id} exists: {thread.name}")
            else:
                await ctx.send(f"Thread {thread_id} not found")
    else:
        await ctx.send("No threads are currently tracked")

# Weekly accountability poll
@bot.command()
async def weeklypoll(ctx):
    """Starts the weekly accountability poll."""
    global created_threads_ids  

    poll_message = await ctx.send(random.choice(INITIAL_POLL_MESSAGE))
    await poll_message.add_reaction("✅")  
    print("Poll message sent.")  # Debug log

 
    await asyncio.sleep(68400)  # 19 hours

    # Fetch the updated message with reactions
    updated_message = await ctx.fetch_message(poll_message.id)
    opted_in_members = []

    for reaction in updated_message.reactions:
        if reaction.emoji == "✅":
            async for user in reaction.users():
                if not user.bot:  # Ignore bots
                    opted_in_members.append(user)

    # Handle responses
    if opted_in_members:
        await ctx.send(f"🎉 {len(opted_in_members)} participants joined! Assigning groups...")
        random.shuffle(opted_in_members)
        groups = [opted_in_members[i:i + 2] for i in range(0, len(opted_in_members), 2)]

        # Balance groups if needed
        if len(groups) > 1 and len(groups[-1]) == 1:  
            groups[-2].extend(groups[-1])
            groups.pop()

        # Create threads for groups
        for i, group in enumerate(groups):
            timestamp = datetime.now().strftime('%d-%m')
            thread_name = f"GoalSquad {i+1} - {timestamp}"
            try:
                # Ensure the channel supports thread creation
                if isinstance(ctx.channel, discord.TextChannel):
                    thread = await ctx.channel.create_thread(
                        name=thread_name, type=discord.ChannelType.private_thread
                    )
                    created_threads_ids.append(thread.id)
                    
                    # Save thread IDs to persistent storage
                    save_poll_state(created_threads_ids)
                    
                    user_mentions = ", ".join([member.mention for member in group])
                    await thread.send(
                        f"Hi {user_mentions}, welcome to your accountability group for this week! 🎉\n\n"
                        f"**Instructions:**\n"
                        f"Share your progress using the following format:\n\n"
                        f"1️⃣ **What did you accomplish yesterday?**\n"
                        f"2️⃣ **What are your goals for today?**\n"
                        f"3️⃣ **Any blockers or challenges you're facing?**\n\n"
                        f"Let's make this week productive! 🚀"
                    )
                else:
                    await ctx.send("❌ This command must be run in a text channel where threads are allowed.")
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to create threads in this channel.")
            except discord.HTTPException as e:
                logging.error(f"HTTPException while creating thread: {e}")
                await ctx.send(f"❌ An error occurred while creating the thread.")
    else:
        await ctx.send("😔 No one joined this week. Better luck next time!")


bot.run(TOKEN)