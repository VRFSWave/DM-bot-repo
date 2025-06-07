import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# --- Configuration ---
TOKEN = "MTM4MDkyMTQxOTk1NzAxNDUyOA.GxeulZ.q3JMRluJ2xyfNy3cCyBjnzNOFXwwjVj-AAYM78"  # Replace with your bot token
GUILD_ID = 1152665688960405504  # Replace with your server ID (int)
OWNER_ROLE_ID = 1367244979625394307  # Replace with your Owner role ID (int)

intents = discord.Intents.default()
intents.members = True  # Required to access role members

# --- Flask webserver for keep-alive ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord bot setup ---
class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands only to the specified guild for faster updates
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)

bot = MyClient()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(
    name="dmrole",
    description="DM all users with a specific role a custom message",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    role="The role to DM",
    message="The message to send"
)
async def dmrole(interaction: discord.Interaction, role: discord.Role, message: str):
    # Check if user has the owner role
    if OWNER_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message("❌ You don’t have permission to use this command.", ephemeral=True)
        return

    await interaction.response.send_message(f"📨 Sending DMs to everyone in {role.name}...", ephemeral=True)

    count = 0
    for member in role.members:
        if member.bot:
            continue  # Skip bots
        try:
            await member.send(message)
            count += 1
        except Exception as e:
            print(f"⚠️ Couldn't DM {member.display_name}: {e}")

    await interaction.followup.send(f"✅ Sent message to {count} users with the role `{role.name}`.")

# Start the webserver and run the bot
keep_alive()
bot.run(TOKEN)
