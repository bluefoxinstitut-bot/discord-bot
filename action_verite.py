import discord
from discord.ext import commands
import random

ACTIONS = [
    "Fais 10 pompes ! 💪",
    "Imite quelqu'un pendant 1 minute 🎭",
    "Chante 30 secondes d'une chanson de ton choix 🎵",
    "Dis un compliment sincère à quelqu'un de ton choix 💬",
    "Fais le tour de la pièce à quatre pattes 🐾",
    "Dis l'alphabet à l'envers aussi vite que possible 🔤",
    "Envoie le dernier meme que tu as regardé 😂",
    "Fais 5 burpees 🏋️",
    "Parle avec un accent étranger pendant 2 minutes 🗣️",
    "Poste ta photo de profil originale 📸",
    "Écris un poème de 4 vers maintenant 📝",
    "Fais semblant d'être un robot pendant 1 minute 🤖",
    "Dis le prénom de ton crush (si t'en as un) 😏",
    "Fais un headstand ou essaie pendant 30 secondes 🙃",
    "Envoie le premier contact de ta liste de messages 📱",
    "Imite un animal pendant 30 secondes 🐸",
    "Révèle ton mot de passe Wi-Fi (ou invente-en un honteux) 📶",
    "Lis tes 3 derniers messages envoyés à voix haute 📣",
    "Danse pendant 30 secondes sans musique 🕺",
    "Fais une grimace et envoie une photo ! 😜",
]

VERITES = [
    "C'est quoi ton plus grand regret ? 😔",
    "T'as déjà menti à quelqu'un de proche ? Sur quoi ? 👀",
    "C'est quoi la chose la plus gênante que t'aies faite ? 😳",
    "T'as un crush en ce moment ? Dis-nous sans dire le nom ! 💘",
    "C'est quoi ton pire défaut selon toi ? 🤔",
    "T'as déjà stalké quelqu'un sur les réseaux ? 🕵️",
    "C'est quoi le truc le plus bête que t'aies fait par amour ? 💔",
    "T'as déjà pleuré devant un film ? Lequel ? 😭",
    "C'est quoi ton péché mignon honteux ? 🍕",
    "T'as déjà menti à tes parents ? Sur quoi ? 🤫",
    "C'est quoi ta peur la plus ridicule ? 😱",
    "T'as déjà lu les messages de quelqu'un sans permission ? 📵",
    "C'est quoi ton opinion impopulaire ? 🌶️",
    "T'as déjà fait semblant d'être malade pour pas aller quelque part ? 🤒",
    "C'est quoi le truc que tu ferais si t'avais 1 million d'euros ? 💰",
    "T'as déjà bloqué quelqu'un et pourquoi ? 🚫",
    "C'est quoi le message le plus bizarre que t'as envoyé ? 💬",
    "T'as déjà trahi un secret d'un ami ? 🤐",
    "C'est quoi ton app la plus utilisée dont t'as honte ? 📲",
    "T'as déjà eu le béguin pour un prof ? 😅",
]

class ActionVerite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_nom(self, ctx, membre=None):
        """Retourne le nom à afficher, compatible MP et serveur"""
        if membre and ctx.guild:
            return membre.display_name, membre.display_avatar.url
        return ctx.author.display_name, ctx.author.display_avatar.url

    @commands.command(name="av", aliases=["actionverite", "truth"])
    async def action_verite(self, ctx, membre: discord.Member = None):
        """Lance un défi Action ou Vérité"""
        nom, avatar = self.get_nom(ctx, membre)
        choix = random.choice(["action", "verite"])

        if choix == "action":
            texte = random.choice(ACTIONS)
            emoji, titre, couleur = "💥", "ACTION !", 0xFF4444
        else:
            texte = random.choice(VERITES)
            emoji, titre, couleur = "👁️", "VÉRITÉ !", 0x4444FF

        embed = discord.Embed(
            title=f"{emoji} {titre}",
            description=f"**{nom}**, voici ton défi :",
            color=couleur
        )
        embed.add_field(name="📋 Défi", value=texte, inline=False)
        embed.set_thumbnail(url=avatar)
        embed.set_footer(text="Action ou Vérité • Bonne chance ! 🎲")
        await ctx.send(embed=embed)

    @commands.command(name="action")
    async def tirer_action(self, ctx, membre: discord.Member = None):
        """Tire uniquement une action"""
        nom, avatar = self.get_nom(ctx, membre)
        texte = random.choice(ACTIONS)

        embed = discord.Embed(
            title="💥 ACTION !",
            description=f"**{nom}**, à toi de jouer !",
            color=0xFF4444
        )
        embed.add_field(name="📋 Action", value=texte, inline=False)
        embed.set_thumbnail(url=avatar)
        await ctx.send(embed=embed)

    @commands.command(name="verite")
    async def tirer_verite(self, ctx, membre: discord.Member = None):
        """Tire uniquement une vérité"""
        nom, avatar = self.get_nom(ctx, membre)
        texte = random.choice(VERITES)

        embed = discord.Embed(
            title="👁️ VÉRITÉ !",
            description=f"**{nom}**, réponds honnêtement !",
            color=0x4444FF
        )
        embed.add_field(name="❓ Question", value=texte, inline=False)
        embed.set_thumbnail(url=avatar)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ActionVerite(bot))
