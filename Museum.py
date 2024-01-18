import discord
from discord.ext import commands
import discord.utils 
import asyncio
from discord import app_commands
import requests
from minecraft_utils import minecraftSKin
from datetime import datetime
import re
import json
import math
from collections import OrderedDict 
import asyncio
import aiohttp



item_names_to_check = OrderedDict()
armor_names_to_check = OrderedDict()
rarities_names_to_check = OrderedDict()

with open("item_emojis.json", "r") as f:
    item_emojis = json.load(f)

with open('item_names.txt', 'r') as file:
    for line in file:
        item_names_to_check[line.strip()] = {}

with open('armor_names.txt', 'r') as file:
    for line in file:
        armor_names_to_check[line.strip()] = {}

with open('rarities_names.txt', 'r') as file:
    for line in file:
        rarities_names_to_check[line.strip()] = {}

with open('display_names.json', 'r') as file:
    display_name_mapping = json.load(file)

with open('item_prices.json', 'r') as file:
    item_prices = json.load(file)

def getInfo(call):
    response = requests.get(call)
    return response.json()

def UsernameToID(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    uuid = getInfo(mojang_url)
    return uuid['id']

def format_username(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    formatted_username = getInfo(mojang_url)
    return formatted_username['name']

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()
        
async def check_profiles_with_data(username):
    uuid = UsernameToID(username)

    api_key = "f1d8278e-47fd-4ee9-ab01-d78ce73087c9"
    url = f"https://api.hypixel.net/skyblock/profiles?key={api_key}&uuid={uuid}"
    profiles_with_data = []
    profiles_without_data = []
    cute_names_with_data = []
    cute_names_without_data = []

    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_data(session, url)
            profiles = data.get("profiles", [])

            tasks = []
            for profile in profiles:
                profile_id = profile.get("profile_id")
                api2_url = f"https://api.hypixel.net/skyblock/museum?key={api_key}&profile={profile_id}"
                tasks.append(fetch_data(session, api2_url))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for idx, result in enumerate(results):
                if isinstance(result, dict) and result.get("success") and result.get("members"):
                    profiles_with_data.append(profiles[idx]["profile_id"])
                    cute_name = profiles[idx].get("cute_name")
                    if cute_name:
                        cute_names_with_data.append(cute_name)
                else:
                    profiles_without_data.append(profiles[idx]["profile_id"])
                    cute_name = profiles[idx].get("cute_name")
                    if cute_name:
                        cute_names_without_data.append(cute_name)

        except aiohttp.ClientError:
            pass

    return profiles_with_data, cute_names_with_data, cute_names_without_data 


def get_data(selected_profile_id, username):
    url = f"https://api.hypixel.net/skyblock/museum?key=f1d8278e-47fd-4ee9-ab01-d78ce73087c9&profile={selected_profile_id}"
    dataset = getInfo(url)
    uuid = UsernameToID(username)
    data = dataset.get("members", {}).get(uuid, {}).get("items", [])
    return data


def read_item_conditions(filename):
    item_conditions = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                condition, dependency = line.split()
                item_conditions.append((condition, dependency))
    return item_conditions


def remove_minecraft_formatting(text):
    return re.sub(r'§[0-9a-fklmnor]', '', text)

def getInfo(call):
    response = requests.get(call)
    return response.json()

def UsernameToID(username):
    mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    uuid = getInfo(mojang_url)
    return uuid['id']


def remove_minecraft_formatting(text):
    return re.sub(r'§[0-9a-fklmnor]', '', text)


def initial_embed_creation(data, user_minecraft_skin):
        embed = discord.Embed(title=f"Museum", description=f"The Museum is a compendium of all your items in SkyBlock. This displays what you have donated based on the selected profile. ", type = 'rich', colour=0x00b0f4, timestamp=datetime.now() )
        embed.set_thumbnail(url=user_minecraft_skin)

        armor_count = 0
        item_count = 0
        rarities_count = 0
        for item_name in data:
            if item_name in armor_names_to_check:
                armor_count += 1
            if item_name in item_names_to_check:
                item_count += 1
            if item_name in rarities_names_to_check:
                rarities_count += 1
            
        armor_file_count = len(armor_names_to_check)
        armor_percent = (armor_count / armor_file_count) * 100

        item_file_count = len(item_names_to_check)
        item_percent = (item_count / item_file_count) * 100

        rarities_file_count = len(rarities_names_to_check)
        rarities_percent = (rarities_count / rarities_file_count) * 100

        total_items_donated = armor_count + item_count + rarities_count
        total_museum_items = armor_file_count + item_file_count + rarities_file_count

        total_items_percent = (total_items_donated / total_museum_items * 100)



        embed.add_field(name="", value="")
        embed.add_field(name=f"Items Donated: {total_items_percent:.2f}%", value=f"{total_items_donated}/{total_museum_items}", inline= True)

        embed.add_field(name="", value="\u200b")
        embed.add_field(name = "items", value= f"{item_percent:.2f}%", inline = True)
        embed.add_field(name = "armor", value= f"{armor_percent:.2f}%", inline = True)
        embed.add_field(name = "rarities", value= f"{rarities_percent:.2f}%", inline = True)

        embed.add_field(name="", value="\u200b")
        embed.add_field(name="", value="\u200b")
        embed.add_field(name="", value="\u200b")

        return embed


class weapons(discord.ui.View):
    def __init__(self, data, user_minecraft_skin, username, cute_name):
        super().__init__()
        self.current_page = 1
        self.data = data
        self.show_filtered_items = False
        self.filtered_item_names = []
        self.pages = 9
        self.user_minecraft_skin = user_minecraft_skin
        self.username = username
        self.cute_name = cute_name


    async def send(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def calculate_page_number(self):
        self.filtered_item_names = []

        for item_name in item_names_to_check:
            if self.filtered_item_names and item_name not in self.data and item_name in item_names_to_check:
                self.filtered_item_names.append(item_name)

        if self.show_filtered_items:
            self.pages = math.ceil(len(self.filtered_item_names) / 14)
        else:
            self.pages = math.ceil(len(item_names_to_check) / 14)

    def create_embed(self):
        embed = discord.Embed(title=f"Weapons **`Page:{self.current_page}/{self.pages}`**", description="", colour=0x00b0f4, timestamp=datetime.now())
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/6/6a/Diamond_Sword_JE2_BE2.png/revision/latest?cb=20200217235945")
        embed.set_footer(text=f"{self.username} • {self.cute_name}", icon_url=self.user_minecraft_skin)

        

        item_names_to_check_list = list(item_names_to_check)
        all_items_to_display = []
        total_items = len(item_names_to_check_list)
        items_per_page = 14
        start_index = (self.current_page - 1) * items_per_page
        end_index = min(start_index + items_per_page, total_items)
        self.filtered_item_names = []

        for index in range(total_items):
            item_name = item_names_to_check_list[index]
            emoji = item_emojis.get(item_name, "<:grey_dye:1153937769022898196>")
            display_item_name = display_name_mapping.get(item_name, item_name)

            if item_name in self.data:
                value = "<:YesYesYes:1146507491568533544>"
            else:
                value = "<:NoNoNo:1146507501966204999>"

            if self.show_filtered_items and item_name not in self.data and item_name in item_names_to_check:
                self.filtered_item_names.append(f"{emoji} {display_item_name} {value}")

            if not self.show_filtered_items:
                all_items_to_display.append(f"{emoji} {display_item_name} {value}")

        if self.show_filtered_items:
            if self.filtered_item_names:
                all_items_to_display.extend(self.filtered_item_names)

        if self.show_filtered_items and not self.filtered_item_names:
            embed.add_field(name="t", value="Congrats you are a loser")
        else:
            items_to_display = all_items_to_display[start_index:end_index]
            for item in items_to_display:
                embed.add_field(name=item, value = "", inline=False)




        self.calculate_page_number()
        self.update_buttons()
        return embed

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.primary)
    async def go_to_museum_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = initial_embed_creation(self.data, self.user_minecraft_skin)
        initial_menu = InitialMenu(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        self.remove_item(self.go_to_museum_button)
        await interaction.edit_original_response(embed=embed, view=initial_menu)

    @discord.ui.button(label="<", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        if self.current_page > self.pages:
            self.current_page = self.pages
        await self.update_message(interaction)



    @discord.ui.button(label="Not present", style=discord.ButtonStyle.red, custom_id="toggle_button")
    async def toggle_rarities_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.show_filtered_items = not self.show_filtered_items
        self.calculate_page_number()
        
        if self.current_page > self.pages:
            self.current_page = self.pages
        if self.current_page < 1:
            self.current_page = 1
        button.label = "Not present" if not self.show_filtered_items else "Show All"
        button.style = discord.ButtonStyle.red if not self.show_filtered_items else discord.ButtonStyle.green
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.create_embed(), view=self)


    def update_buttons(self):
        if self.current_page == 1:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False
        if self.pages == 0:
            self.next_button.disabled = True
            self.prev_button.disabled = True
        elif self.current_page == self.pages:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False


class rarities(discord.ui.View):
    def __init__(self, data, user_minecraft_skin, username, cute_name):
        super().__init__()
        self.current_page = 1
        self.data = data
        self.show_filtered_rarities = False
        self.filtered_rarity_names = []
        self.pages = 8
        self.user_minecraft_skin = user_minecraft_skin
        self.username = username
        self.cute_name = cute_name

    async def send(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def calculate_page_number(self):
        self.filtered_rarity_names = []

        for rarity_name in rarities_names_to_check:
            if self.show_filtered_rarities and rarity_name not in self.data and rarity_name in rarities_names_to_check:
                self.filtered_rarity_names.append(rarity_name)

        if self.show_filtered_rarities:
            self.pages = math.ceil(len(self.filtered_rarity_names) / 14)
        else:
            self.pages = math.ceil(len(rarities_names_to_check) / 14)


    def create_embed(self):
        embed = discord.Embed(title=f"Museum Menu", description=f"Pages: {self.current_page} / {self.pages}. Currently displaying profile: {self.cute_name}")
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/8/80/Block_of_Emerald_JE1_BE1.png/revision/latest?cb=20191229174639")
        embed.set_footer(text=f"{self.username}• {self.cute_name}", icon_url=self.user_minecraft_skin)
   

        rarities_names_to_check_list = list(rarities_names_to_check)
        all_rarities_to_display = []
        total_items = len(rarities_names_to_check_list)
        items_per_page = 14
        start_index = (self.current_page - 1) * items_per_page
        end_index = min(start_index + items_per_page, total_items)
        self.filtered_rarity_names = []

        for index in range(total_items):
            rarity_name = rarities_names_to_check_list[index]
            emoji = item_emojis.get(rarity_name, "❓")
            display_item_name = display_name_mapping.get(rarity_name, rarity_name)

            if rarity_name in self.data:
                value = "<:YesYesYes:1146507491568533544>"
            else:
                value = "<:NoNoNo:1146507501966204999>"

            if self.show_filtered_rarities and rarity_name not in self.data and rarity_name in rarities_names_to_check:
                self.filtered_rarity_names.append(f"{emoji} {display_item_name} {value}")

            if not self.show_filtered_rarities:
                all_rarities_to_display.append(f"{emoji} {display_item_name} {value}")

        if self.show_filtered_rarities:
            if self.filtered_rarity_names:
                all_rarities_to_display.extend(self.filtered_rarity_names)


        if self.show_filtered_rarities and not self.filtered_rarity_names:
            embed.add_field(name="t", value="Congrats you are a loser")
        else:
            rarities_to_display = all_rarities_to_display[start_index:end_index]
            for rarity in rarities_to_display:
                embed.add_field(name=rarity, value = "", inline=False)

        self.calculate_page_number()
        self.update_buttons()
        return embed

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.primary)
    async def go_to_museum_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = initial_embed_creation(self.data, self.user_minecraft_skin)
        initial_menu = InitialMenu(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        self.remove_item(self.go_to_museum_button)
        await interaction.edit_original_response(embed=embed, view=initial_menu)

    @discord.ui.button(label="<", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        if self.current_page > self.pages:
            self.current_page = self.pages
        await self.update_message(interaction)



    @discord.ui.button(label="Not present", style=discord.ButtonStyle.red, custom_id="toggle_button")
    async def toggle_rarities_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        self.show_filtered_rarities = not self.show_filtered_rarities
        self.calculate_page_number()  
        

        button.label = "Not present" if not self.show_filtered_rarities else "Show All"
        button.style = discord.ButtonStyle.red if not self.show_filtered_rarities else discord.ButtonStyle.green

        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.create_embed(), view=self)


    def update_buttons(self):
        if self.current_page == 1:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False
        if self.pages == 0:
            self.next_button.disabled = True
            self.prev_button.disabled = True
        elif self.current_page == self.pages:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False

class armor(discord.ui.View):
    def __init__(self, data, user_minecraft_skin, username, cute_name):
        super().__init__()
        self.current_page = 1
        self.data = data
        self.show_filtered_armor = False
        self.filtered_armor_names = []
        self.pages = 8
        self.user_minecraft_skin = user_minecraft_skin
        self.username = username
        self.cute_name = cute_name

    async def send(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def calculate_page_number(self):
        self.filtered_armor_names = []

        for armor_name in armor_names_to_check:
            if self.show_filtered_armor and armor_name not in self.data and armor_name in armor_names_to_check:
                self.filtered_armor_names.append(armor_name)

        if self.filtered_armor_names:
            self.pages = math.ceil(len(self.filtered_armor_names) / 14)
        else:
            self.pages = math.ceil(len(armor_names_to_check) / 14)



    def create_embed(self):
        embed = discord.Embed(title=f"Museum Menu", description=f"Pages: {self.current_page} / {self.pages}. Currently displaying profile: {self.cute_name}", timestamp=datetime.now())
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/minecraft_gamepedia/images/3/3d/Diamond_Chestplate_%28item%29_JE2_BE2.png/revision/latest?cb=20190406141332")
        embed.set_footer(text=f"{self.username} • {self.cute_name}", icon_url=self.user_minecraft_skin)

        armor_names_to_check_list = list(armor_names_to_check)
        all_armor_to_display = []
        total_items = len(armor_names_to_check_list)
        items_per_page = 14
        start_index = (self.current_page - 1) * items_per_page
        end_index = min(start_index + items_per_page, total_items)
        self.filtered_armor_names = []


        for index in range(total_items):
            armor_name = armor_names_to_check_list[index]
            emoji = item_emojis.get(armor_name, "❓")
            display_item_name = display_name_mapping.get(armor_name, armor_name)

            if armor_name in self.data:
                value = "<:YesYesYes:1146507491568533544>"
            else:
                value = "<:NoNoNo:1146507501966204999>"

            if self.show_filtered_armor and armor_name not in self.data and armor_name in armor_names_to_check:
                self.filtered_armor_names.append(f"{emoji} {display_item_name} {value}")

            if not self.show_filtered_armor:
                all_armor_to_display.append(f"{emoji} {display_item_name} {value}")

        if self.show_filtered_armor:
            if self.filtered_armor_names:
                all_armor_to_display.extend(self.filtered_armor_names)


        if self.show_filtered_armor and not self.filtered_armor_names:
            embed.add_field(name="t", value="Congrats you are a loser")
        else:
            armors_to_display = all_armor_to_display[start_index:end_index]
            for armor in armors_to_display:
                embed.add_field(name=armor, value = "", inline=False)

        self.calculate_page_number()
        self.update_buttons()
        return embed

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.primary)
    async def go_to_museum_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = initial_embed_creation(self.data, self.user_minecraft_skin)
        initial_menu = InitialMenu(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        self.remove_item(self.go_to_museum_button)
        await interaction.edit_original_response(embed=embed, view=initial_menu)

    @discord.ui.button(label="<", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        if self.current_page > self.pages:
            self.current_page = self.pages
        await self.update_message(interaction)



    @discord.ui.button(label="Not present", style=discord.ButtonStyle.red, custom_id="toggle_button")
    async def toggle_rarities_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.show_filtered_armor = not self.show_filtered_armor
        self.calculate_page_number()
        
        if self.current_page > self.pages:
            self.current_page = self.pages
        if self.current_page < 1:
            self.current_page = 1
        button.label = "Not present" if not self.show_filtered_armor else "Show All"
        button.style = discord.ButtonStyle.red if not self.show_filtered_armor else discord.ButtonStyle.green
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.edit_original_response(embed=self.create_embed(), view=self)


    def update_buttons(self):
        if self.current_page == 1:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False
        if self.pages == 0:
            self.next_button.disabled = True
            self.prev_button.disabled = True
        elif self.current_page == self.pages:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False


class InitialMenu(discord.ui.View):
    def __init__(self, data, user_minecraft_skin, username, cute_name):
        super().__init__()
        self.view_museum_button = None
        self.data = data
        self.user_minecraft_skin = user_minecraft_skin
        self.username = username
        self.cute_name = cute_name


    @discord.ui.button(label="Weapons", style=discord.ButtonStyle.blurple)
    async def view_museum(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.paginate(interaction)
        except Exception as e:
            print("Error in view_museum:", e)

    @discord.ui.button(label="Armor", style=discord.ButtonStyle.blurple)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.paginate2(interaction)
        except Exception as e:
            print("Error in menu1:", e)

    @discord.ui.button(label="Rarities", style=discord.ButtonStyle.blurple)
    async def menu3(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.paginate3(interaction)
        except Exception as e:
            print("Error in menu1:", e)

    async def paginate(self, interaction: discord.Interaction):
        pagination_view = weapons(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        try:
            await pagination_view.send(interaction)
        except Exception as e:
            print("Error in paginate:", e)

    async def paginate2(self, interaction: discord.Interaction):
        pagination_view = armor(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        try:
            await pagination_view.send(interaction)
        except Exception as e:
            print("Error in paginate3:", e)

    async def paginate3(self, interaction: discord.Interaction):
        pagination_view = rarities(self.data, self.user_minecraft_skin, self.username, self.cute_name)
        try:
            await pagination_view.send(interaction)
        except Exception as e:
            print("Error in paginate3:", e)





class ProfileMenu(discord.ui.View):
    def __init__(self, username, user_minecraft_skin):
        super().__init__()
        self.username = username
        self.user_minecraft_skin = user_minecraft_skin
        self.profiles = []
        self.cute_names = []




        
    async def setup_buttons(self):
        profiles_with_data, cute_names_with_data, cute_names_without_data = await check_profiles_with_data(self.username)
        self.profiles_with_data = profiles_with_data
        self.cute_names_with_data = cute_names_with_data
        self.cute_names_without_data = cute_names_without_data
    
        for cute_name, profile_id in zip(self.cute_names_with_data, self.profiles_with_data):
            button = discord.ui.Button(style=discord.ButtonStyle.green, label=cute_name, custom_id=f"{profile_id}:{cute_name}")
            button.label = cute_name
            button.callback = self.button_callback
            self.add_item(button)

        for cute_name in self.cute_names_without_data:
            button = discord.ui.Button(style=discord.ButtonStyle.red, label=cute_name)
            button.disabled = True
            self.add_item(button)


    async def button_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        profile_id, cute_name = custom_id.split(':')
        data = get_data(profile_id, self.username)
        item_conditions = read_item_conditions("item_conditions.txt")

        for condition, dependency in item_conditions:
            if condition in data and dependency not in data:
                data[dependency] = True

        embed = initial_embed_creation(data, self.user_minecraft_skin)
        initial_menu = InitialMenu(data, self.user_minecraft_skin, self.username, cute_name)
        await interaction.response.defer()
        await interaction.edit_original_response(embed = embed, view=initial_menu)










class museum_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="museum",
        description="Access the museum information"
    )
    
    async def show_initial_menu(self, interaction: discord.Interaction, username: str,):
        username = format_username(username)
        user_minecraft_skin = minecraftSKin(UsernameToID(username))
        try:
            initial_menu = ProfileMenu(username, user_minecraft_skin)
            await initial_menu.setup_buttons()
            embed = discord.Embed(title=f"{interaction.user}", description=f"Displaying active skyblock profiles ", colour=0x00b0f4, timestamp=datetime.now())
            embed.set_thumbnail(url=user_minecraft_skin)
            await interaction.response.send_message(embed=embed, view=initial_menu, ephemeral = True)
        except TypeError:
                embed = discord.Embed(title="Museum", description="The username you entered does not have any profiles on SkyBlock.", type='rich', color=0x00b0f4, timestamp=datetime.now())
                embed.set_footer(text=f"{username}")
                embed.set_thumbnail(url=user_minecraft_skin)
                await interaction.response.send_message(embed=embed, ephemeral = True)
        except KeyError: 
                embed = discord.Embed(title="Museum", description="The username does not exist.", type='rich', color=0x00b0f4, timestamp=datetime.now())
                embed.set_footer(text=f"{username}")
                embed.set_thumbnail(url=user_minecraft_skin)
                await interaction.response.send_message(embed=embed, ephemeral = True)
        except Exception:
            await interaction.response.send_message(content="There has been an error with this command. Please try again at another time.", ephemeral = True)






async def setup(bot):
    await bot.add_cog(museum_command(bot))
