# welcome_bot.py
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
SERVER_NAME = os.getenv("SERVER_NAME")
INTERVIEWER = os.getenv("INTERVIEWER")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        embed = discord.Embed(
            title=f"Bienvenue sur {SERVER_NAME}, {member.name} ! 👋",
            description=(
                f"Bonjour {member.mention},\n\n"
                f"Bienvenue sur **{SERVER_NAME}** ! 🎉\n\n"
                f"Sache que **{INTERVIEWER}** voudra te faire passer un entretien en vocal sur le serveur.\n\n"
                f"Reste disponible et à l'écoute, il te contactera dès que possible !"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"À très vite sur {SERVER_NAME} !")
        await member.send(embed=embed)
        print(f"MP de bienvenue envoyé à {member.name}")
    except discord.Forbidden:
        print(f"Impossible d'envoyer un MP à {member.name} (MPs désactivés)")

bot.run(TOKEN)