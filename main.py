import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents, shard_id=2)

allowedRoleName = "admin"

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
apikey = os.getenv("API_KEY")

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"Ready as {client.user}!")

@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@client.tree.command(name="ownerships", description="Check products owned by user")
async def ownerships(interaction: discord.Interaction, user: discord.User):
    userid = user.id
    if any(role.name == allowedRoleName for role in interaction.user.roles):
        headers = {
            "api-key": apikey,
            "discord-id": str(userid)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.warware.org/api/v1/get-user-ownerships", headers=headers) as response:
                if response.status != 200:
                    if response.status == 404:
                        embed = discord.Embed(
                            title= f"{user.display_name} has not linked their discord to a WARWARE account.",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=embed)
                        return
                    await interaction.response.send_message(f"API request failed. Status: {response.status}", ephemeral=True)
                    return

                data = await response.json()
                ownerships = data.get("ownerships", [])
                products = []
                for ownership in ownerships:
                    title = ownership["product"]["title"]
                    link = f"https://www.warware.org/store/{ownership['product']['id']}"
                    products.append(f"[{title}]({link})")

                description = "\n".join(products)

        embed = discord.Embed(
            title= f"Products owned by {user.display_name}({user.name})" if user.name != user.display_name else f"Products owned by {user.name}",
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)

    

client.run(token)