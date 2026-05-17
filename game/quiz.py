import discord
from discord.ext import commands
import random
import asyncio

QUESTIONS = {
    "Culture Générale": [
        {"q": "Quelle est la capitale de la France ?", "r": "paris", "choix": ["Paris", "Lyon", "Marseille", "Bordeaux"]},
        {"q": "Combien de continents y a-t-il sur Terre ?", "r": "7", "choix": ["5", "6", "7", "8"]},
        {"q": "Quel est le plus grand océan du monde ?", "r": "pacifique", "choix": ["Atlantique", "Indien", "Pacifique", "Arctique"]},
        {"q": "En quelle année a eu lieu la Révolution française ?", "r": "1789", "choix": ["1789", "1776", "1804", "1815"]},
        {"q": "Qui a peint la Joconde ?", "r": "léonard de vinci", "choix": ["Michel-Ange", "Léonard de Vinci", "Raphaël", "Botticelli"]},
        {"q": "Quel est le pays le plus grand du monde ?", "r": "russie", "choix": ["Canada", "Chine", "Russie", "États-Unis"]},
        {"q": "Combien de jours compte une année bissextile ?", "r": "366", "choix": ["364", "365", "366", "367"]},
        {"q": "Quelle est la langue la plus parlée au monde ?", "r": "anglais", "choix": ["Chinois", "Anglais", "Espagnol", "Hindi"]},
    ],
    "Manga & Anime": [
        {"q": "Quel est le vrai nom de Naruto ?", "r": "naruto uzumaki", "choix": ["Naruto Uzumaki", "Naruto Namikaze", "Naruto Uchiha", "Naruto Hyuga"]},
        {"q": "Dans One Piece, comment s'appelle le fruit qu'a mangé Luffy ?", "r": "gomu gomu", "choix": ["Gomu Gomu", "Mera Mera", "Hie Hie", "Gura Gura"]},
        {"q": "Dans Dragon Ball Z, quel est le niveau max de Super Saiyan classique ?", "r": "3", "choix": ["2", "3", "4", "5"]},
        {"q": "Quel est le nom du titan de l'Attaque des Titans ?", "r": "eren", "choix": ["Armin", "Levi", "Eren", "Mikasa"]},
        {"q": "Dans Demon Slayer, quel est le style de respiration de Tanjiro ?", "r": "eau", "choix": ["Feu", "Eau", "Vent", "Foudre"]},
        {"q": "Qui est le mentor de Naruto ?", "r": "jiraiya", "choix": ["Kakashi", "Jiraiya", "Minato", "Iruka"]},
        {"q": "Dans Bleach, comment s'appelle l'épée de Ichigo ?", "r": "zangetsu", "choix": ["Senbonzakura", "Zangetsu", "Hyorinmaru", "Zabimaru"]},
    ],
    "Football": [
        {"q": "Qui a remporté la Coupe du Monde 2022 ?", "r": "argentine", "choix": ["France", "Argentine", "Brésil", "Allemagne"]},
        {"q": "Combien de fois le Brésil a-t-il gagné la Coupe du Monde ?", "r": "5", "choix": ["4", "5", "6", "7"]},
        {"q": "Quel club a remporté le plus de Ligues des Champions ?", "r": "real madrid", "choix": ["FC Barcelone", "Real Madrid", "Bayern Munich", "Liverpool"]},
        {"q": "Qui détient le record de buts en Coupe du Monde ?", "r": "miroslav klose", "choix": ["Ronaldo", "Messi", "Miroslav Klose", "Gerd Müller"]},
        {"q": "Dans quel pays se trouve le stade de Wembley ?", "r": "angleterre", "choix": ["France", "Allemagne", "Angleterre", "Espagne"]},
    ],
    "Science": [
        {"q": "Quelle est la formule chimique de l'eau ?", "r": "h2o", "choix": ["H2O", "CO2", "O2", "H2O2"]},
        {"q": "Combien de planètes y a-t-il dans notre système solaire ?", "r": "8", "choix": ["7", "8", "9", "10"]},
        {"q": "Qui a découvert la gravité ?", "r": "newton", "choix": ["Einstein", "Newton", "Galilée", "Darwin"]},
        {"q": "Quelle est la vitesse de la lumière ?", "r": "300000 km/s", "choix": ["150000 km/s", "300000 km/s", "500000 km/s", "1000000 km/s"]},
        {"q": "Quel est l'élément chimique le plus léger ?", "r": "hydrogène", "choix": ["Hélium", "Hydrogène", "Lithium", "Oxygène"]},
    ],
}

CATEGORIES = list(QUESTIONS.keys())
NUMEROS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parties = {}
        self.scores = {}

    @commands.command(name="quiz")
    async def quiz(self, ctx, categorie: str = None):
        """Lance un quiz ! !quiz <categorie> ou !quiz pour aléatoire"""
        if ctx.author.id in self.parties:
            await ctx.send("❌ Tu as déjà un quiz en cours ! Réponds d'abord à la question.")
            return

        # Choisir la catégorie
        if categorie:
            cat_trouve = None
            for cat in CATEGORIES:
                if categorie.lower() in cat.lower():
                    cat_trouve = cat
                    break
            if not cat_trouve:
                cats = ", ".join(CATEGORIES)
                await ctx.send(f"❌ Catégorie introuvable ! Choisis parmi : **{cats}**")
                return
            cat = cat_trouve
        else:
            cat = random.choice(CATEGORIES)

        question = random.choice(QUESTIONS[cat])
        choix = question["choix"][:]
        random.shuffle(choix)

        self.parties[ctx.author.id] = {
            "reponse": question["r"],
            "choix": choix,
            "channel": ctx.channel.id
        }

        embed = discord.Embed(
            title=f"❓ Quiz — {cat}",
            description=f"**{question['q']}**",
            color=0x3498DB
        )

        for i, c in enumerate(choix):
            embed.add_field(name=f"{NUMEROS[i]} {c}", value="\u200b", inline=True)

        embed.set_footer(text="Réponds avec le numéro : 1, 2, 3 ou 4 • Tu as 30 secondes !")
        msg = await ctx.send(embed=embed)

        # Ajouter les réactions
        for num in NUMEROS[:len(choix)]:
            await msg.add_reaction(num)

        def check(reaction, user):
            return (user == ctx.author and
                    str(reaction.emoji) in NUMEROS[:len(choix)] and
                    reaction.message.id == msg.id)

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
            idx = NUMEROS.index(str(reaction.emoji))
            reponse_joueur = choix[idx].lower()
            bonne = question["r"]

            uid = ctx.author.id
            if uid not in self.scores:
                self.scores[uid] = 0

            if reponse_joueur == bonne or bonne in reponse_joueur:
                self.scores[uid] += 1
                embed2 = discord.Embed(title="✅ Bonne réponse !", color=0x00FF00)
                embed2.add_field(name="🎉 Bravo !", value=f"La réponse était bien **{choix[idx]}** !", inline=False)
            else:
                embed2 = discord.Embed(title="❌ Mauvaise réponse !", color=0xFF0000)
                bonne_affichage = next((c for c in choix if c.lower() == bonne or bonne in c.lower()), bonne)
                embed2.add_field(name="💡 Réponse correcte", value=f"C'était **{bonne_affichage}**", inline=False)

            embed2.add_field(name="📊 Score", value=f"{self.scores.get(uid, 0)} bonne(s) réponse(s)", inline=False)
            embed2.set_footer(text="!quiz pour une autre question !")
            await ctx.send(embed=embed2)

        except asyncio.TimeoutError:
            bonne_affichage = next((c for c in choix if c.lower() == question["r"] or question["r"] in c.lower()), question["r"])
            await ctx.send(f"⏰ Temps écoulé ! La réponse était **{bonne_affichage}**.")

        finally:
            self.parties.pop(ctx.author.id, None)

    @commands.command(name="quizcats", aliases=["categories"])
    async def categories(self, ctx):
        """Voir les catégories du quiz"""
        embed = discord.Embed(title="📚 Catégories Quiz", color=0x3498DB)
        for cat in CATEGORIES:
            nb = len(QUESTIONS[cat])
            embed.add_field(name=cat, value=f"{nb} questions", inline=True)
        embed.set_footer(text="!quiz <categorie> pour jouer")
        await ctx.send(embed=embed)

    @commands.command(name="quizscore")
    async def quiz_score(self, ctx):
        """Voir ton score au quiz"""
        score = self.scores.get(ctx.author.id, 0)
        embed = discord.Embed(title="📊 Ton Score Quiz", color=0x3498DB)
        embed.add_field(name=ctx.author.display_name, value=f"**{score}** bonne(s) réponse(s)", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Quiz(bot))
