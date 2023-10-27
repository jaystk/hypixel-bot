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

    return candidate_data, election_year

def get_current():
    current_mayor_data = []
    mayor = data['mayor']
    perks = []
    mayor_name = mayor['name']
    mayor_key = mayor['key']

    for perk in mayor['perks']:
        perk_name = perk['name']
        perk_description = perk['description']
        perks.append((perk_name, perk_description))

    mayor_info = {
        'name': mayor_name,
        'key': mayor_key,
        'perks': perks
    }
    current_mayor_data.append(mayor_info)

    return current_mayor_data


def embed_creation(custom_id, candidate_data, election_year):
    embed = discord.Embed(title = "Mayor Candidate", colour=0x00b0f4, timestamp=datetime.now())
    embed.set_thumbnail(url=output_skin(custom_id))
    embed.set_footer(text = f"Election Year {election_year}")
    for candidate in candidate_data:
        if candidate['name'] == custom_id:
            embed.add_field(name = "Mayor Name", value = custom_id, inline =  True)
            embed.add_field(name="\u200b", value="\u200b", inline=True) 
            embed.add_field(name = "Votes", value = candidate['votes'], inline =  True)

            for perk_name, perk_description in candidate['perks']:
                embed.add_field(name = remove_minecraft_formatting(perk_name), value = remove_minecraft_formatting(perk_description), inline = True)
    return embed
            




class candidate_menu(discord.ui.View):
    def __init__(self, candidate_data, current_mayor_data, election_year):
        super().__init__(timeout=60)
        self.candidate_data = candidate_data
        self.current_mayor_data = current_mayor_data
        self.election_year = election_year
        
    
    async def setup_buttons(self):
        for candidate in self.candidate_data:
            candidate_name = candidate['name']
            votes_percentage = candidate['percentage_of_total_votes']
            candidate_label = f"{candidate_name} {votes_percentage:.2f}%"

            button = discord.ui.Button(style=discord.ButtonStyle.green, label=candidate_label, custom_id=f"{candidate_name}")
            button.callback = self.button_callback
            self.add_item(button)

    

        current_mayor = self.current_mayor_data[0]
        mayor_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=f"{current_mayor['name']}", custom_id="button", disabled = True)
        mayor_button.callback = self.mayor_button_callback
        self.add_item(mayor_button)

    async def button_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        embed = embed_creation(custom_id, self.candidate_data, self.election_year)
        await interaction.response.defer()
        for button in self.children:
            button.disabled = False

        for button in self.children:
            if button.custom_id == custom_id:
                button.disabled = True
                break

        await interaction.edit_original_response(embed=embed, view=self)

    async def mayor_button_callback(self, interaction: discord.Interaction):
        current_mayor = self.current_mayor_data[0]
        initial_menu = candidate_menu(self.candidate_data, self.current_mayor_data, self.election_year)
        

        embed = discord.Embed(title="Current Mayor", description="", color=0x00b0f4, timestamp=datetime.now())
        embed.set_thumbnail(url=output_skin(current_mayor['name']))

        embed.add_field(name="Mayor Name", value=current_mayor['name'], inline=True)
        embed.add_field(name="Mayor Key", value=current_mayor['key'], inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        for perk_name, perk_description in current_mayor['perks']:
            embed.add_field(name=remove_minecraft_formatting(perk_name), value=remove_minecraft_formatting(perk_description), inline=True)


        await interaction.response.defer()
        await initial_menu.setup_buttons()
        await interaction.edit_original_response(embed=embed, view=initial_menu)



class election_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
            name = "election",
            description = "The current election"
            )
    async def election_command(self, interaction: discord.Interaction):
        candidate_data, election_year = get_data()
        current_mayor_data = get_current()
        current_mayor = current_mayor_data[0] 

        embed = discord.Embed(title="Current Mayor",  color=0x00b0f4, timestamp=datetime.now())
        embed.set_thumbnail(url=output_skin(current_mayor['name']))

        embed.add_field(name="Mayor Name", value=current_mayor['name'], inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)


        for perk_name, perk_description in current_mayor['perks']:
            embed.add_field(name=remove_minecraft_formatting(perk_name), value=remove_minecraft_formatting(perk_description), inline=True)

        view = candidate_menu(candidate_data, current_mayor_data, election_year)
        await view.setup_buttons()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)





    





async def setup(bot):
    await bot.add_cog(election_command(bot))
