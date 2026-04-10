import discord
from discord.ext import commands
import random
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables
load_dotenv()

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')

# Convertir la liste d'IDs (format: "id1,id2,id3")
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
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des moqueries (neutres, s'adaptent à tous)
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
    "Silence ! {user} va encore dire une dinguerie.",
    "Ah, {user}... le meeting des développeurs de problèmes vient de commencer.",
    "Chaque fois que {user} parle, un développeur pleure quelque part.",
    "{user}, t'es payé à l'erreur ou c'est un cadeau ?"
]

def verifier_horaire():
    """Vérifie si on est dans les horaires d'activation"""
    heure = datetime.now().hour
    return ACTIF_DEBUT <= heure <= ACTIF_FIN

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")
    print(f"🎯 Utilisateurs ciblés ({len(TARGET_USER_IDS)}):")
    for uid in TARGET_USER_IDS:
        user = await bot.fetch_user(uid)
        print(f"   - {user.name} (ID: {uid})")
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
            emojis = ["🤡", "😂", "👎", "🤦", "💀", "😭", "🙄", "🥴"]
            await message.add_reaction(random.choice(emojis))
        
        # Chance de répondre
        if random.randint(1, 100) <= MOQUERIE_CHANCE:
            moquerie = random.choice(MOQUERIES).format(user=message.author.mention)
            await message.channel.send(moquerie)
            if LOG_MOQUERIES:
                print(f"🎭 Moquerie envoyée à {message.author.name}")
        else:
            if LOG_MOQUERIES:
                print(f"⏭️ Pas de moquerie pour {message.author.name} (chance: {MOQUERIE_CHANCE}%)")
    
    await bot.process_commands(message)

# Commandes
@bot.command()
async def test(ctx):
    await ctx.send("✅ Le bot fonctionne correctement !")

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
        try:
            user = await bot.fetch_user(uid)
            embed.add_field(
                name=user.name,
                value=f"ID: `{uid}`\nMention: {user.mention}",
                inline=False
            )
        except:
            embed.add_field(
                name="❓ Utilisateur inconnu",
                value=f"ID: `{uid}`",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.command()
async def ajouter_cible(ctx, user_id: int):
    """Ajoute un utilisateur à la liste (admin uniquement)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas les permissions !")
        return
    
    if user_id in TARGET_USER_IDS:
        await ctx.send(f"⚠️ L'utilisateur `{user_id}` est déjà dans la liste !")
        return
    
    TARGET_USER_IDS.append(user_id)
    
    # Sauvegarder dans .env (optionnel)
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith('TARGET_USER_IDS='):
                f.write(f'TARGET_USER_IDS={",".join(map(str, TARGET_USER_IDS))}\n')
            else:
                f.write(line)
    
    try:
        user = await bot.fetch_user(user_id)
        await ctx.send(f"✅ {user.mention} a été ajouté aux cibles ! 🎯")
    except:
        await ctx.send(f"✅ Utilisateur `{user_id}` ajouté aux cibles !")

@bot.command()
async def enlever_cible(ctx, user_id: int):
    """Enlève un utilisateur de la liste (admin uniquement)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Tu n'as pas les permissions !")
        return
    
    if user_id not in TARGET_USER_IDS:
        await ctx.send(f"⚠️ L'utilisateur `{user_id}` n'est pas dans la liste !")
        return
    
    TARGET_USER_IDS.remove(user_id)
    
    # Sauvegarder dans .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    with open('.env', 'w') as f:
        for line in lines:
            if line.startswith('TARGET_USER_IDS='):
                f.write(f'TARGET_USER_IDS={",".join(map(str, TARGET_USER_IDS))}\n')
            else:
                f.write(line)
    
    await ctx.send(f"✅ Utilisateur `{user_id}` retiré des cibles !")

@bot.command()
async def config(ctx):
    """Affiche la configuration"""
    embed = discord.Embed(
        title="⚙️ Configuration du bot",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.add_field(
        name="🎯 Cibles", 
        value=f"{len(TARGET_USER_IDS)} utilisateur(s)", 
        inline=True
    )
    embed.add_field(
        name="📢 Salon", 
        value=f"<#{TARGET_CHANNEL_ID}>", 
        inline=True
    )
    embed.add_field(
        name="🎲 Chance", 
        value=f"{MOQUERIE_CHANCE}%", 
        inline=True
    )
    embed.add_field(
        name="😜 Réactions", 
        value="Oui" if REAGIR_TOUJOURS else "Non", 
        inline=True
    )
    embed.add_field(
        name="⏰ Horaires", 
        value=f"{ACTIF_DEBUT}h - {ACTIF_FIN}h", 
        inline=True
    )
    await ctx.send(embed=embed)

# Lancer le bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERREUR: Token non trouvé !")
    elif not TARGET_USER_IDS:
        print("⚠️ ATTENTION: Aucun utilisateur ciblé dans TARGET_USER_IDS !")
        print("📝 Format: TARGET_USER_IDS=id1,id2,id3")
        bot.run(TOKEN)  # Le bot tourne mais ne fait rien
    else:
        bot.run(TOKEN)