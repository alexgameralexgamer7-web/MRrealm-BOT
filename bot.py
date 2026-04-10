import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les valeurs depuis .env
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USER_ID = int(os.getenv('TARGET_USER_ID'))
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
MOQUERIE_CHANCE = int(os.getenv('MOQUERIE_CHANCE', 100))  # 100% par défaut
REAGIR_TOUJOURS = os.getenv('REAGIR_TOUJOURS', 'True').lower() == 'true'

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des moqueries
MOQUERIES = [
    "Ah, revoilà {user}... on avait pourtant bien fermé la cage ?",
    "{user} parle ! Et si on écoutait plutôt les murs ?",
    "Attention, {user} va nous expliquer la vie... Prenez des notes inutiles !",
    "{user}, tu es le coupable idéal... même quand t'as rien fait.",
    "Tu as fini {user} ? Certains essaient de réfléchir ici.",
    "On t'a dit que le silence était d'or ? Toi tu dois être riche alors.",
    "{user}... tes messages sont comme des trous noirs : ils aspirent notre intelligence.",
    "Ah non, {user} a parlé... je retourne me coucher.",
    "{user}, tu devrais breveter ton talent à dire n'importe quoi.",
    "Le professeur {user} donne son cours de bêtise niveau expert.",
    "Est-ce que quelqu'un a demandé l'avis de {user} ? Non.",
    "{user} est comme un bug, ça revient tout le temps.",
    "Silence ! {user} va encore dire une dinguerie."
]

# Vérification au démarrage
@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")
    print(f"🎯 Cible : {TARGET_USER_ID}")
    print(f"📢 Salon surveillé : {TARGET_CHANNEL_ID}")
    print(f"🎲 Chance de moquerie : {MOQUERIE_CHANCE}%")
    print(f"😜 Réaction systématique : {REAGIR_TOUJOURS}")
    print("-" * 50)
    
    # Vérifier que le token est chargé
    if not TOKEN:
        print("❌ ERREUR: Token non trouvé dans .env !")
        return
    print("✅ Configuration chargée avec succès !")

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author == bot.user:
        return

    # Vérifier si c'est le bon salon ET la bonne utilisatrice
    if message.channel.id == TARGET_CHANNEL_ID and message.author.id == TARGET_USER_ID:
        
        # Ajouter une réaction (si activé)
        if REAGIR_TOUJOURS:
            emojis = ["🤡", "😂", "👎", "🤦", "💀", "😭", "🙄", "🥴"]
            await message.add_reaction(random.choice(emojis))
        
        # Chance de répondre avec une moquerie
        if random.randint(1, 100) <= MOQUERIE_CHANCE:
            moquerie = random.choice(MOQUERIES).format(user=message.author.mention)
            await message.channel.send(moquerie)
            print(f"🎭 Moquerie envoyée à {message.author.name}")
        else:
            print(f"⏭️ Pas de moquerie cette fois (chance: {MOQUERIE_CHANCE}%)")
    
    await bot.process_commands(message)

# Commande pour recharger la config sans redémarrer
@bot.command()
async def reload_config(ctx):
    """Recharge les variables depuis .env"""
    if ctx.author.guild_permissions.administrator:
        load_dotenv(override=True)
        global TARGET_USER_ID, TARGET_CHANNEL_ID, MOQUERIE_CHANCE, REAGIR_TOUJOURS
        TARGET_USER_ID = int(os.getenv('TARGET_USER_ID'))
        TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
        MOQUERIE_CHANCE = int(os.getenv('MOQUERIE_CHANCE', 100))
        REAGIR_TOUJOURS = os.getenv('REAGIR_TOUJOURS', 'True').lower() == 'true'
        await ctx.send("✅ Configuration rechargée !")
        print("🔄 Configuration rechargée")
    else:
        await ctx.send("❌ Tu n'as pas les permissions !")

# Commande pour afficher la config (sans les infos sensibles)
@bot.command()
async def config(ctx):
    """Affiche la configuration actuelle"""
    embed = discord.Embed(title="⚙️ Configuration du bot", color=0x00ff00)
    embed.add_field(name="Salon ciblé", value=f"<#{TARGET_CHANNEL_ID}>", inline=False)
    embed.add_field(name="Chance de moquerie", value=f"{MOQUERIE_CHANCE}%", inline=True)
    embed.add_field(name="Réactions activées", value="Oui" if REAGIR_TOUJOURS else "Non", inline=True)
    await ctx.send(embed=embed)

# Commande de test
@bot.command()
async def test(ctx):
    await ctx.send("✅ Le bot fonctionne correctement !")

# Lancer le bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERREUR CRITIQUE: Token Discord non trouvé !")
        print("📝 Crée un fichier .env avec DISCORD_TOKEN=ton_token")
    else:
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ Token invalide ! Vérifie ton .env")
        except Exception as e:
            print(f"❌ Erreur: {e}")