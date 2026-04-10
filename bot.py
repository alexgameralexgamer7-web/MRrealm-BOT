import discord
from discord.ext import commands
import random
import os
from datetime import datetime

# Configuration Railway
TOKEN = os.getenv('DISCORD_TOKEN')

# Récupérer la liste d'IDs
target_ids_str = os.getenv('TARGET_USER_IDS', '')
TARGET_USER_IDS = [int(id.strip()) for id in target_ids_str.split(',') if id.strip()]

TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', 0))
MOQUERIE_CHANCE = int(os.getenv('MOQUERIE_CHANCE', 100))
REAGIR_TOUJOURS = os.getenv('REAGIR_TOUJOURS', 'True').lower() == 'true'
ACTIF_DEBUT = int(os.getenv('ACTIF_DEBUT', 0))
ACTIF_FIN = int(os.getenv('ACTIF_FIN', 23))
LOG_MOQUERIES = os.getenv('LOG_MOQUERIES', 'True').lower() == 'true'

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Important pour avoir accès aux membres

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
    "Le professeur {user} donne son cours de bêtise niveau expert."
]

def verifier_horaire():
    heure = datetime.now().hour
    return ACTIF_DEBUT <= heure <= ACTIF_FIN

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")
    print(f"🎯 Utilisateurs ciblés ({len(TARGET_USER_IDS)}):")
    
    # Afficher les IDs sans essayer de fetch (pour éviter l'erreur)
    for uid in TARGET_USER_IDS:
        print(f"   - ID: {uid}")
    
    print(f"📢 Salon surveillé : {TARGET_CHANNEL_ID}")
    print(f"🎲 Chance de moquerie : {MOQUERIE_CHANCE}%")
    print(f"😜 Réaction systématique : {REAGIR_TOUJOURS}")
    print(f"⏰ Horaires : {ACTIF_DEBUT}h - {ACTIF_FIN}h")
    print("-" * 50)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Vérifier si le salon correspond ET si l'utilisateur est dans la liste
    if message.channel.id == TARGET_CHANNEL_ID and message.author.id in TARGET_USER_IDS:
        
        # Vérifier les horaires
        if not verifier_horaire():
            if LOG_MOQUERIES:
                print(f"⏰ Hors horaire - Message ignoré de {message.author.name}")
            await bot.process_commands(message)
            return
        
        # Ajouter une réaction
        if REAGIR_TOUJOURS:
            emojis = ["🤡", "😂", "👎", "🤦", "💀"]
            try:
                await message.add_reaction(random.choice(emojis))
            except:
                pass  # Ignorer les erreurs de réaction
        
        # Chance de répondre
        if random.randint(1, 100) <= MOQUERIE_CHANCE:
            moquerie = random.choice(MOQUERIES).format(user=message.author.mention)
            await message.channel.send(moquerie)
            if LOG_MOQUERIES:
                print(f"🎭 Moquerie envoyée à {message.author.name} (ID: {message.author.id})")
        else:
            if LOG_MOQUERIES:
                print(f"⏭️ Pas de moquerie pour {message.author.name}")
    
    await bot.process_commands(message)

# Commande pour lister les cibles avec leurs noms (fonctionne après que le bot est prêt)
@bot.command()
async def cibles(ctx):
    """Affiche la liste des utilisateurs ciblés"""
    if len(TARGET_USER_IDS) == 0:
        await ctx.send("❌ Aucune cible configurée !")
        return
    
    embed = discord.Embed(
        title="🎯 Utilisateurs ciblés",
        color=0xff0000,
        timestamp=datetime.now()
    )
    
    for uid in TARGET_USER_IDS:
        # Chercher l'utilisateur dans le serveur actuel
        user = ctx.guild.get_member(uid)
        if user:
            embed.add_field(
                name=user.name,
                value=f"ID: `{uid}`\nMention: {user.mention}",
                inline=False
            )
        else:
            embed.add_field(
                name="❓ Utilisateur inconnu",
                value=f"ID: `{uid}`\n*(Pas trouvé sur ce serveur)*",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    await ctx.send("✅ Le bot fonctionne correctement !")

@bot.command()
async def config(ctx):
    """Affiche la configuration"""
    embed = discord.Embed(
        title="⚙️ Configuration du bot",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.add_field(name="🎯 Cibles", value=f"{len(TARGET_USER_IDS)} utilisateur(s)", inline=True)
    embed.add_field(name="📢 Salon", value=f"<#{TARGET_CHANNEL_ID}>", inline=True)
    embed.add_field(name="🎲 Chance", value=f"{MOQUERIE_CHANCE}%", inline=True)
    embed.add_field(name="😜 Réactions", value="Oui" if REAGIR_TOUJOURS else "Non", inline=True)
    embed.add_field(name="⏰ Horaires", value=f"{ACTIF_DEBUT}h - {ACTIF_FIN}h", inline=True)
    await ctx.send(embed=embed)

# Lancer le bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERREUR: Token non trouvé !")
    else:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ Erreur: {e}")
