import discord
from discord.ext import commands
import discord.utils 
import asyncio
from discord import app_commands
import requests
from minecraft_utils import minecraftSKin
import io
import requests
from datetime import datetime
import re
import json
from discord.ext import tasks



with open('mayor_skins.json', 'r') as file:
    candidate_skins = json.load(file)

    
def getInfo(call):
    response = requests.get(call)
    return response.json()

def UsernameToID(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    uuid = getInfo(mojang_url)
    return uuid['id']

def remove_minecraft_formatting(text):
    return re.sub(r'§[0-9a-fklmnor]', '', text)

def output_skin(candidate):
    if candidate in candidate_skins:
        skin_filename = candidate_skins[candidate]
        return skin_filename


url = "https://api.hypixel.net/resources/skyblock/election"
data = getInfo(url)


def get_data():
    candidate_data = []
    total_votes = sum(candidate['votes'] for candidate in data["current"]["candidates"])

    election_year = data["current"]["year"]

    for candidate in data["current"]["candidates"]:
        perks = []
        candidate_name = candidate['name']
        candidate_votes = candidate['votes']
        candidate_key = candidate['key']
        percentage_votes = (candidate_votes / total_votes) * 100


        for perk in candidate['perks']:
            perk_name = perk['name']
            perk_description = perk['description']
            perks.append((perk_name, perk_description))

        candidate_info = {'name': candidate_name, 'votes': candidate_votes, 'percentage_of_total_votes': percentage_votes, 'perks': perks, 'key': candidate_key}
        candidate_data.append(candidate_info)

    return candidate_data, election_year, total_votes



def initial_embed(candidate_data, election_year, total_votes):
    candidate_emojis = {
    "Aatrox": "<:aatrox:1158633410378596382>",
    "Cole": "<:cole:1158633411775303722>",
    "Diana": "<:diana:1158633412547063858>",
    "Foxy": "<:foxy:1158633413419474944>",
    "Jerry": "<:jerry:1158633414149288036>",
    "Marina": "<:marina:1158633415529205770>",
    "Paul": "<:paul:1158633409573306419>",
    "Technoblade": "<:technoblade:1158635069716561970>",
    "Dante": "<:dante:1158635070215684148>",
    "Diaz": "<:diaz:1158635062925996072>",
    "Barry": "<:barry:1158635064171704462>",
    "Finnegan": "<:finnegan:1158635066369511495>",
    "Derpy": "<:derpy:1158635067225161758>",
    "Scorpius": "<:scorpius3:1158635068433121300>"
}
    max_votes_candidate = max(candidate_data, key=lambda candidate: candidate['votes'])
    max_votes_percentage = (max_votes_candidate['votes'] / total_votes) * 100




    embed = discord.Embed(title = f"Next Predicted Mayor: {max_votes_candidate['name']}", description = f"Leading with **``{max_votes_percentage:.2f}%``** of votes", colour=0x00b0f4, timestamp=datetime.now())
    embed.set_thumbnail(url=output_skin(max_votes_candidate["name"]))
    embed.set_footer(text=f"Election Year {election_year}  • Last Updated ")




    embed.add_field(name = f"{max_votes_candidate['name']}'s Perks", value = "")
    for perk_name, perk_description in max_votes_candidate['perks']:
        embed.add_field(name=f"• {remove_minecraft_formatting(perk_name)}", value=remove_minecraft_formatting(perk_description), inline=False)


    embed.add_field(name = f"Other Candidates", value = "")
    for candidate in candidate_data:
        emoji = candidate_emojis.get(candidate['name'], '')
        if candidate['name'] != max_votes_candidate['name']:
            embed.add_field(name = f"{emoji} {candidate['name']}", value = f"**``{candidate['percentage_of_total_votes']:.2f}%``**", inline = False)




    return embed

    





CHANNEL_IDS = [1155725421690761258]

class auto_update_election_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = {}
        self.update_channel.start()

    async def send_or_update_election(self):
        candidate_data, election_year, total_votes = get_data()
        embed = initial_embed(candidate_data, election_year, total_votes)



        for channel_id in CHANNEL_IDS:
            channel = self.bot.get_channel(channel_id)
            if channel_id in self.messages:
                await self.messages[channel_id].edit(embed=embed)
            else:
                self.messages[channel_id] = await channel.send(embed=embed)

    @tasks.loop(hours = 2)
    async def update_channel(self):
        await self.bot.wait_until_ready()
        try:
            await self.send_or_update_election()
        except Exception as e:
            print(f"Failed to update election info: {e}")

    @app_commands.command(name="election_update", description="The current election")
    async def election_command(self, interaction: discord.Interaction):
        await self.send_or_update_election()
        await interaction.response.send_message(content="Updated!", ephemeral=True)

    def cog_unload(self):
        self.update_channel.cancel()

    





async def setup(bot):
    await bot.add_cog(auto_update_election_command(bot))
