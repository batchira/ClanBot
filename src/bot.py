import discord
import os
from dotenv import load_dotenv
from discord import app_commands
import logging
from src import logging_additions
import logging.handlers

if not os.path.exists("../logs"):
    os.mkdir("../logs")

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    filename='../logs/discord.log',
    maxBytes=32 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8')
handler.doRollover()
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)

# Logging on console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging_additions.ConsoleColoredFormatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))
logger.addHandler(console)


# .env reading
if not os.path.exists("../.env"):
    logger.critical(".env not found, exiting...")
    exit(1)
try:
    load_dotenv()
except Exception as e:
    logger.critical("Error while reading .env, exiting...")
    logger.critical("Stacktrace :")
    logger.critical(e)
    exit(1)

# Constants
try:
    TOKEN = os.environ["TOKEN"]
    GUILD_ID = int(os.environ["GUILD_ID"])
except KeyError as e:
    logger.critical("TOKEN or GUILD_ID not found in .env, exiting...")
    logger.critical("Stacktrace :")
    logger.critical(e)
    exit(1)


class ClanBotClient(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        logger.info('Bot ready, starting...')
        await client.wait_until_ready()
        logger.info('Logged in as {0.user}'.format(client))
        logger.info('=' * 60)
        logger.info('Guilds :')
        for guild in client.guilds:
            logger.info(' - {0.name} ({0.id})'.format(guild))
        logger.info('=' * 60)
        logger.info('Syncing...')
        if not self.synced:
            await tree.sync()
            self.synced = True


client = ClanBotClient()
tree = discord.app_commands.CommandTree(client)

"""
 Commandes :
"""

guild = client.get_guild(GUILD_ID)


@tree.command(name="newclan", guild=guild, description="Créer un nouveau clan")
@app_commands.describe(
    nom="Nom du clan",
)
async def new_clan(ctx: discord.Interaction, nom: str):
    # Admin only
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("Vous n'avez pas la permission de faire cela", ephemeral=True, delete_after=15)
        return

    # Check if the clan already exists
    if discord.utils.get(ctx.guild.roles, name="Membre " + nom):
        embed = discord.Embed(title="Création de clan",
                                description="Le clan " + nom + " existe déjà", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
    else:
        try:
            await ctx.guild.create_role(name="Membre " + nom, mentionable=True, hoist=True,
                                        reason="Création du clan " + nom + " par " + ctx.user.name)
            await ctx.guild.create_role(name="Chef " + nom, mentionable=True, hoist=True,
                                        reason="Création du clan " + nom + " par " + ctx.user.name)

            embed = discord.Embed(title="Création de clan",
                                  description="Le clan " + nom + " a été créé", color=0x00ff00)
            await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        except discord.Forbidden as e:
            embed = discord.Embed(title="Création de clan",
                                  description="Je n'ai pas la permission de créer des rôles", color=0xff0000)
            await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("Permission error while creating role " + nom)
            logger.error("Stacktrace :")
            logger.error(e)
        except discord.HTTPException as e:
            embed = discord.Embed(title="Création de clan",
                                  description="Une erreur est survenue lors de la création du clan " + nom,
                                  color=0xff0000)
            await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("HTTP error while creating role " + nom)
            logger.error("Stacktrace :")
            logger.error(e)


@tree.command(name="deleteclan", guild=guild, description="Supprimer un clan")
@app_commands.describe(
    nom="Nom du clan"
)
async def delete_clan(ctx: discord.Interaction, nom: str):
    # Check if the clan exists
    if not discord.utils.get(ctx.guild.roles, name="Membre " + nom):
        embed = discord.Embed(title="Suppression du clan " + nom,
                                description="Le clan " + nom + " n'existe pas", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        return

    # Admin only or clan chief
    if not ctx.user.guild_permissions.administrator:
        if not discord.utils.get(ctx.user.roles, name="Chef " + nom):
            embed = discord.Embed(title="Suppression du clan " + nom,
                                  description="Vous n'avez pas la permission de faire cela", color=0xff0000)
            await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            return

    embed = discord.Embed(title="Suppression du clan " + nom,
                          description="Êtes-vous sûr de vouloir supprimer le clan " + nom + " ?")
    embed.set_footer(text="Cette action est irréversible")
    await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15, view=DeleteClanUI(nom))


@tree.command(name="leaveclan", guild=guild, description="Quitter un clan")
@app_commands.describe(
    nom="Nom du clan"
)
async def leave_clan(ctx: discord.Interaction, nom: str):
    # Check if the clan exists
    if not discord.utils.get(ctx.guild.roles, name="Membre " + nom):
        embed = discord.Embed(title="Quitter le clan " + nom,
                                description="Le clan " + nom + " n'existe pas", color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        return

    # Check if the user is in the clan
    if not discord.utils.get(ctx.user.roles, name="Membre " + nom) and not discord.utils.get(ctx.user.roles, name="Chef " + nom):
        embed = discord.Embed(title="Quitter le clan " + nom,
                                description="Vous n'êtes pas dans le clan " + nom, color=0xff0000)
        await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        return

    embed = discord.Embed(title="Quitter le clan " + nom,
                          description="Êtes-vous sûr de vouloir quitter le clan " + nom + " ?")
    await ctx.response.send_message(embed=embed, ephemeral=True, delete_after=15, view=LeaveClanUI(nom))


@tree.context_menu(name="Ajouter comme chef à un clan", guild=guild)
async def add_chief_menu(interaction: discord.Interaction, user: discord.Member):
    # No bot user
    if user.bot:
        embed = discord.Embed(title="Ajouter " + user.name + " comme chef d'un clan",
                              description="Vous ne pouvez pas ajouter un bot comme chef d'un clan", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        return

    targetted_member = user
    origin_member = interaction.user
    embed = discord.Embed(title="Ajouter " + targetted_member.name + " comme chef d'un clan",
                            description="Dans quel clan voulez-vous ajouter " + targetted_member.name + " ?",
                            color=0x00ff00)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15, view=AddChiefUI(targetted_member, origin_member))


@tree.context_menu(name="Inviter ce membre à un clan", guild=guild)
async def add_member_menu(interaction: discord.Interaction, user: discord.Member):
    # No bot user
    if user.bot:
        embed = discord.Embed(title="Inviter " + user.name + " dans un clan",
                              description="Vous ne pouvez pas inviter un bot dans un clan", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        return

    targetted_member = user
    origin_member = interaction.user

    embed = discord.Embed(title="Inviter " + targetted_member.name + " dans un clan",
                          description="Dans quel clan voulez-vous inviter " + targetted_member.name + " ?",
                          color=0x00ff00)
    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15,
                                            view=AddMemberUI(targetted_member, origin_member))

# UIs


class AddMemberUI(discord.ui.View):
    def __init__(self, member: discord.Member, initiator: discord.Member):
        super().__init__(timeout=60)
        self.member = member
        self.initiator = initiator
        self.clans = []
        for role in initiator.roles:
            if role.name.startswith("Chef "):
                self.clans.append(role.name[5:])
        if len(self.clans) == 0:
            self.add_item(discord.ui.Button(label="Vous n'êtes chef d'aucun clan", style=discord.ButtonStyle.danger,
                                            disabled=True))
        else:
            self.add_item(ClanListInvite(options=[discord.SelectOption(label=clan) for clan in self.clans],
                                   placeholder="Choisissez un clan", member=self.member, initiator=self.initiator))


class AddChiefUI(discord.ui.View):
    def __init__(self, member: discord.Member, initiator: discord.Member):
        super().__init__(timeout=60)
        self.member = member
        self.initiator = initiator
        self.clans = []
        if not initiator.guild_permissions.administrator:
            for role in initiator.roles:
                if role.name.startswith("Chef "):
                    self.clans.append(role.name[5:])
        else:
            for role in initiator.guild.roles:
                if role.name.startswith("Chef "):
                    self.clans.append(role.name[5:])
        if len(self.clans) == 0:
            self.add_item(discord.ui.Button(label="Vous n'êtes chef d'aucun clan", style=discord.ButtonStyle.danger,
                                            disabled=True))
        else:
            self.add_item(ClanListChief(options=[discord.SelectOption(label=clan) for clan in self.clans],
                                   placeholder="Choisissez un clan", member=self.member, initiator=self.initiator))


class JoinClanUI(discord.ui.View):
    def __init__(self, member: discord.Member, clan: str):
        super().__init__(timeout=60)
        self.member = member
        self.clan = clan

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message("Vous avez accepté l'invitation à rejoindre le clan " + self.clan + ".",
                                                    ephemeral=True, delete_after=15)
            await self.member.add_roles(discord.utils.get(self.member.guild.roles, name="Membre " + self.clan),
                                        reason="Acceptation de l'invitation à rejoindre le clan " +
                                               self.clan + " par " + self.member.name)
            self.stop()
        except discord.Forbidden as e:
            await interaction.response.send_message("Je n'ai pas les permissions pour ajouter le rôle Membre " + self.clan + " à " + self.member.name + ".",
                                                    ephemeral=True, delete_after=15)
            self.stop()
            logger.error("Permission error when adding role Membre " + self.clan + " to " + self.member.name)
            logger.error("Stacktrace :")
            logger.error(e)
        except discord.HTTPException as e:
            await interaction.response.send_message("Une erreur est survenue lors de l'ajout du rôle Membre " + self.clan + " à " + self.member.name + ".",
                                                    ephemeral=True, delete_after=15)
            self.stop()
            logger.error("HTTP error when adding role Membre " + self.clan + " to " + self.member.name)
            logger.error("Stacktrace :")
            logger.error(e)

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.danger)
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Vous avez refusé l'invitation à rejoindre le clan " + self.clan + ".",
                                                ephemeral=True, delete_after=15)
        self.stop()


class DeleteClanUI(discord.ui.View):
    def __init__(self, name: str):
        super().__init__(timeout=60)
        self.name = name

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            embed = discord.Embed(title="Suppression du clan " + self.name,
                                  description="Le clan " + self.name + " a été supprimé.", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            await interaction.guild.get_role(
                discord.utils.get(interaction.guild.roles, name="Chef " + self.name).id).delete()
            await interaction.guild.get_role(
                discord.utils.get(interaction.guild.roles, name="Membre " + self.name).id).delete()
            self.stop()
        except discord.errors.Forbidden as e:
            embed = discord.Embed(title="Suppression du clan " + self.name,
                                  description="Je n'ai pas les permissions de faire cela", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("Permission error while deleting clan " + self.name)
            logger.error("Stacktrace :")
            logger.error(e)
            self.stop()
        except discord.HTTPException as e:
            embed = discord.Embed(title="Suppression du clan " + self.name,
                                  description="Une erreur est survenue", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("HTTP error while deleting clan " + self.name)
            logger.error("Stacktrace :")
            logger.error(e)
            self.stop()

    @discord.ui.button(label="Non", style=discord.ButtonStyle.danger)
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Suppression du clan " + self.name,
                                description="Le clan " + self.name + " n'a pas été supprimé.", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        self.stop()


class LeaveClanUI(discord.ui.View):
    def __init__(self, name: str):
        super().__init__(timeout=60)
        self.name = name

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            embed = discord.Embed(title="Quitter le clan " + self.name,
                                    description="Vous avez quitté le clan " + self.name + ".", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="Membre " + self.name),
                                                reason="Quitter le clan " + self.name)
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="Chef " + self.name),
                                                reason="Quitter le clan " + self.name)
        except discord.errors.Forbidden as e:
            embed = discord.Embed(title="Quitter le clan " + self.name,
                                    description="Je n'ai pas les permissions de faire cela", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("Permission error while leaving clan " + self.name)
            logger.error("Stacktrace :")
            logger.error(e)
        except discord.errors.HTTPException as e:
            embed = discord.Embed(title="Quitter le clan " + self.name,
                                    description="Une erreur est survenue", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("HTTP error while leaving clan " + self.name)
            logger.error("Stacktrace :")
            logger.error(e)
        self.stop()

    @discord.ui.button(label="Non", style=discord.ButtonStyle.danger)
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Quitter le clan " + self.name,
                                description="Vous n'avez pas quitté le clan " + self.name + ".", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        self.stop()

# Select menus for clan list


class ClanListInvite(discord.ui.Select):

    def __init__(self, options, placeholder, member, initiator):
        super().__init__(placeholder=placeholder, options=options)
        self.member = member
        self.initiator = initiator

    async def callback(self, interaction: discord.Interaction):
        try:
            # Checks if the user who is invited is not leader of the clan
            if discord.utils.get(self.member.roles, name="Chef " + self.values[0]) is not None:
                embed = discord.Embed(title="Invitation à rejoindre le clan " + self.values[0],
                                        description="Ce membre est déjà chef du clan " + self.values[0] + ".", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
                return
            embed = discord.Embed(title="Invitation à rejoindre le clan " + self.values[0],
                                  description="Une invitation a été envoyée à " + self.member.name + " pour rejoindre le clan " +
                                              self.values[0] + ". Elle expirera dans 60 secondes", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            await self.member.send("Vous avez été invité à rejoindre le clan " + self.values[0] + " par " +
                                   self.initiator.name + ".", view=JoinClanUI(self.member, self.values[0]), delete_after=60)
        except discord.Forbidden as e:
            embed = discord.Embed(title="Invitation à rejoindre le clan " + self.values[0],
                                  description="Impossible d'envoyer un message privé à " + self.member.name + ".",
                                  color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("Permission error when trying to send a private message to " + self.member.name + ".")
            logger.error("Stacktrace :")
            logger.error(e)
        except discord.HTTPException as e:
            embed = discord.Embed(title="Invitation à rejoindre le clan " + self.values[0],
                                  description="Impossible d'envoyer un message privé à " + self.member.name + ".",
                                  color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("HTTP error when trying to send a private message to " + self.member.name + ".")
            logger.error("Stacktrace :")
            logger.error(e)


class ClanListChief(discord.ui.Select):

    def __init__(self, options, placeholder, member, initiator):
        super().__init__(placeholder=placeholder, options=options)
        self.member = member
        self.initiator = initiator

    async def callback(self, interaction: discord.Interaction):
        try:
        # If the member is already chief of the clan
            if discord.utils.get(self.member.roles, name="Chef " + self.values[0]) is not None:
                embed = discord.Embed(title="Promotion dans le clan " + self.values[0],
                                        description="Ce membre est déjà chef du clan " + self.values[0] + ".", color=0xff0000)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
                return
            # If the member is already member of the clan then remove the member role and add the chief role
            if discord.utils.get(self.member.roles, name="Membre " + self.values[0]) is not None:
                await self.member.remove_roles(discord.utils.get(self.member.guild.roles, name="Membre " + self.values[0]),
                                               reason="Promotion dans le clan " + self.values[0] + " par " +
                                                      self.initiator.name)
                await self.member.add_roles(discord.utils.get(self.member.guild.roles, name="Chef " + self.values[0]),
                                            reason="Promotion dans le clan " + self.values[0] + " par " +
                                                   self.initiator.name)
                embed = discord.Embed(title="Promotion dans le clan " + self.values[0],
                                      description=self.member.name + " a été promu chef du clan " + self.values[0] + ".",
                                      color=0x00ff00)
                await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
                return
            # If the member is not member of the clan then add the chief role
            await self.member.add_roles(discord.utils.get(self.member.guild.roles, name="Chef " + self.values[0]),
                                        reason="Promotion dans le clan " + self.values[0] + " par " +   self.initiator.name)
            embed = discord.Embed(title="Promotion dans le clan " + self.values[0],
                                    description=self.member.name + " a été promu chef du clan " + self.values[0] + ".",
                                    color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        except discord.errors.Forbidden as e:
            embed = discord.Embed(title="Promotion dans le clan " + self.values[0],
                                  description="Je n'ai pas la permission de promouvoir " + self.member.name + " chef du clan " + self.values[0] + ".",
                                  color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("Permission error when promoting " + self.member.name + " to chief of clan " + self.values[0] + ".")
            logger.error("Stack trace : ")
            logger.error(e)
        except discord.errors.HTTPException as e:
            embed = discord.Embed(title="Promotion dans le clan " + self.values[0],
                                  description="Une erreur est survenue lors de la promotion de " + self.member.name + " chef du clan " + self.values[0] + ".",
                                  color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            logger.error("HTTP error when promoting " + self.member.name + " to chief of clan " + self.values[0] + ".")
            logger.error("Stack trace : ")
            logger.error(e)


client.run(TOKEN, log_handler=None)
