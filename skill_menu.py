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
import math
from collections import OrderedDict 
import asyncio
import aiohttp

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

def get_current(data, uuid):
    current_profile = "No profile found"
    current_cute_name = "No cute name found"
    current_profile_data = None 
    
    if data.get("profiles") is None:
        return current_profile, current_cute_name, current_profile_data
      
    for profile in data["profiles"]:
        if profile.get("selected", False):
            current_profile_data = profile.get("members", {}).get(uuid, {}).get("experience_skill_runecrafting")
            if current_profile_data is not None:
                current_cute_name = profile.get("cute_name", "No cute name found")
                current_profile = profile.get("profile_id", "Profile found but no data")
            else:
                current_profile = profile.get("profile_id", "Profile fou333333nd but no data")
                current_cute_name = profile.get("cute_name", "No cute name found")

    return current_profile, current_cute_name, current_profile_data


def get_data(data, uuid):
    profiles_without_data = []
    profiles_with_data = []
    cute_names_without_data = []
    cute_names_with_data = []

    for profile in data["profiles"]:
        enchanting_skill = profile.get("members", {}).get(str(uuid)).get("experience_skill_runecrafting")
        if enchanting_skill is None:
            profiles_without_data.append(str(profile["profile_id"]))
            cute_names_without_data.append(str(profile["cute_name"]))
        else:
            profiles_with_data.append(str(profile["profile_id"]))
            cute_names_with_data.append(str(profile["cute_name"]))

    return profiles_without_data, profiles_with_data, cute_names_without_data, cute_names_with_data



def get_skills(profile_id, data, uuid):
    
    for profile in data['profiles']:
        if 'profile_id' in profile and profile['profile_id'] == profile_id:
            skill_data = profile.get("members", {}).get(uuid)
            rune_xp = skill_data.get("experience_skill_runecrafting", "N/A")
            combat_xp = skill_data.get("experience_skill_combat", "N/A")
            mining_xp = skill_data.get("experience_skill_mining", "N/A")
            taming_xp = skill_data.get("experience_skill_taming", "N/A")
            alchemy_xp = skill_data.get("experience_skill_alchemy", "N/A")
            farming_xp = skill_data.get("experience_skill_farming", "N/A")
            enchanting_xp = skill_data.get("experience_skill_enchanting", "N/A")
            fishing_xp = skill_data.get("experience_skill_fishing", "N/A")
            foraging_xp = skill_data.get("experience_skill_foraging", "N/A")
            social_xp = skill_data.get("experience_skill_social2", "N/A")
            carpentry_xp = skill_data.get("experience_skill_carpentry", "N/A")

    return taming_xp, mining_xp, foraging_xp, enchanting_xp, carpentry_xp, farming_xp, combat_xp, fishing_xp, alchemy_xp, rune_xp, social_xp


def calculate_next_level_info(score):
  level_data = [(1, 50), (2, 125), (3, 200), (4, 300), (5, 500), (6, 750),
                (7, 1000), (8, 1500), (9, 2000), (10, 3500), (11, 5000),
                (12, 7500), (13, 10000), (14, 15000), (15, 20000), (16, 30000),
                (17, 50000), (18, 75000), (19, 100000), (20, 200000),
                (21, 300000), (22, 400000), (23, 500000), (24, 600000),
                (25, 700000), (26, 800000), (27, 900000), (28, 1000000),
                (29, 1100000), (30, 1200000), (31, 1300000), (32, 1400000),
                (33, 1500000), (34, 1600000), (35, 1700000), (36, 1800000),
                (37, 1900000), (38, 2000000), (39, 2100000), (40, 2200000),
                (41, 2300000), (42, 2400000), (43, 2500000), (44, 2600000),
                (45, 2750000), (46, 2900000), (47, 3100000), (48, 3400000),
                (49, 3700000), (50, 4000000),(51, 4300000), (52, 4600000), 
                (53, 4900000), (54, 5200000), (55, 5500000), (56, 5800000),
                (57, 6100000), (58, 6400000), (59, 6700000), (60, 7000000)]

  current_level = 0
  next_level = 0
  score_needed_for_next_level = 0

  for level, threshold in level_data:
    if score <= threshold:
      next_level = level
      score_needed_for_next_level = threshold - score
      break
    current_level = level

  progress = 1.0 - (score_needed_for_next_level / (level_data[next_level - 1][1] - level_data[next_level - 2][1]))

  bar_length = 16
  num_blocks = int(bar_length * progress)
  progress_bar = "█" * num_blocks + "░" * (bar_length - num_blocks)

  return current_level, progress_bar

def get_slayer(profile_id, data, uuid):
    for profile in data['profiles']:
        if 'profile_id' in profile and profile['profile_id'] == profile_id:
            slayer_data = profile.get("members", {}).get(uuid).get("slayer_bosses", {})
            wolf = slayer_data.get("wolf", {}).get("xp", 0)
            zombie = slayer_data.get("zombie", {}).get("xp", 0)
            enderman = slayer_data.get("enderman", {}).get("xp", 0)
            blaze = slayer_data.get("blaze", {}).get("xp", 0)
            vampire = slayer_data.get("vampire", {}).get("xp", 0)
            spider = slayer_data.get("spider", {}).get("xp", 0)


    return zombie, spider, wolf, enderman, blaze

def calculate_slayer_level(score):
    level_data = [(1, 5), (2, 15), (3, 200), (4, 1000), (5, 5000), (6, 20000), (7, 100000), (8, 400000), (9, 1000000)]

    current_level = 0
    next_level = 0
    score_needed_for_next_level = 0

    for level, threshold in level_data:
        if score <= threshold:
            next_level = level
            score_needed_for_next_level = threshold - score
            break
        current_level = level

    progress = 1.0 - (score_needed_for_next_level / (level_data[next_level - 1][1] - level_data[next_level - 2][1]))
    bar_length = 10
    num_blocks = int(bar_length * progress)
    progress_bar = "🟥" * num_blocks + "" * (bar_length - num_blocks)

    return current_level, progress_bar

def embed_creation(profile_id, cute_name, username, user_minecraft_skin, data, uuid):
    embed = discord.Embed(title="SkyBlock Skills", description="", type='rich', color=0x00b0f4, timestamp=datetime.now())
    embed.set_footer(text=f"{username} • {cute_name}")
    embed.set_thumbnail(url=user_minecraft_skin)

    skill_names = ["Taming", "Mining", "Foraging", "Enchanting", "Carpentry", "Farming", "Combat", "Fishing", "Alchemy", "Runecrafting", "Social", "Rev Slayer", "Tara Slayer", "Sven Slayer", "Ender Slayer", "Blaze Slayer"]

    
    levels = []
    xp_list = get_skills(profile_id, data, uuid)
    slayer_xp = get_slayer(profile_id, data, uuid)


    for skill_xp, skill_name in zip(xp_list, skill_names):
        if skill_xp == 0:
            level = 1
            progress_bar = "░░░░░░░░░░░░░░░░"
        else:
            level, progress_bar = calculate_next_level_info(skill_xp)
            if skill_name == "Foraging" and level > 50:
                level = 50
                progress_bar = "████████████████"
            if skill_name == "Fishing" and level > 50:
                level = 50
                progress_bar = "████████████████"
            if skill_name == "Alchemy" and level > 50:
                level = 50
                progress_bar = "████████████████"
            if skill_name == "Taming" and level > 50:
                level = 50
                progress_bar = "████████████████"
            if skill_name == "Carpentry" and level > 50:
                level = 50
                progress_bar = "████████████████"
            if skill_name == "Social" and level >= 25:
                level = 25
                progress_bar = "████████████████"
            if skill_name == "Runecrafting" and level >= 25:
                level = 25
                progress_bar = "████████████████"

        levels.append((level, progress_bar))

    for xp in slayer_xp:
        if xp == 0:
            level = 1
            progress_bar = "░░░░░░░░░░░░░░░░"
        else:
            level, progress_bar = calculate_slayer_level(xp)
        levels.append((level, progress_bar))

    for index, (level, progress_bar) in enumerate(levels):
        skill_name = skill_names[index]

        embed.add_field(name=f"{skill_name} Level: {level}", value=f"{progress_bar}", inline=True)

        if (index + 1) % 2 == 0:
            embed.add_field(name='\u200b', value='\u200b', inline=True)


    return embed


class ProfileMenu(discord.ui.View):
    def __init__(self, username, user_minecraft_skin, data, uuid):
        super().__init__(timeout=60)
        self.profiles = []
        self.cute_names = []
        self.username = username
        self.user_minecraft_skin = user_minecraft_skin
        self.data = data
        self.uuid = uuid
        self.selected_profile = None
    async def setup_buttons(self, current_active_profile_id=None):
            profiles_without_data, profiles_with_data, cute_names_without_data, cute_names_with_data = get_data(self.data, self.uuid)
            self.profiles_without_data = profiles_without_data
            self.profiles_with_data = profiles_with_data
            self.cute_names_without_data = cute_names_without_data
            self.cute_names_with_data = cute_names_with_data
            
            for cute_name, profile_id in zip(self.cute_names_with_data, self.profiles_with_data):
                is_active_profile = (profile_id == current_active_profile_id)
                button = discord.ui.Button(style=discord.ButtonStyle.green, label=cute_name, custom_id=f"{profile_id}:{cute_name}", disabled=is_active_profile)
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
        embed = embed_creation(profile_id, cute_name, self.username, self.user_minecraft_skin, self.data, self.uuid)
        await interaction.response.defer()
        if self.selected_profile == custom_id:
                return 
        for button in self.children:
            if button.style != discord.ButtonStyle.red:
                button.disabled = False

        for button in self.children:
            if button.custom_id == custom_id:
                button.disabled = True
                break

        await interaction.edit_original_response(embed=embed, view=self)








class skill_menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="skills",
        description="Display SkyBlock profile skills "
    )

    async def show_initial_menu(self, interaction: discord.Interaction, username: str,):
        try:
            username = format_username(username)
            uuid = UsernameToID(username)
            user_minecraft_skin = minecraftSKin(uuid)
            print(uuid)
            url = f"https://api.hypixel.net/skyblock/profiles?key=d395341a-2e10-426f-8c51-a57ecb822c7b&uuid={uuid}"
            data = getInfo(url)
            initial_menu = ProfileMenu(username, user_minecraft_skin, data, uuid)
            current_profile, current_cute_name, current_profile_data = get_current(data, uuid)
            if current_profile == "No profile found":
                embed = discord.Embed(title="SkyBlock Skills", description="The username you entered does not have any profiles on SkyBlock.", type='rich', color=0x00b0f4, timestamp=datetime.now())
                embed.set_footer(text=f"{username}")
                embed.set_thumbnail(url=user_minecraft_skin)
                await interaction.response.send_message(embed=embed, ephemeral = True)

            elif current_profile_data == None:
                embed = discord.Embed(title="SkyBlock Skills", description="The active SkyBlock profile has skill API disabled. Please select a different profile below.", type='rich', color=0x00b0f4, timestamp=datetime.now())
                embed.set_footer(text=f"{username} • {current_cute_name}")
                embed.set_thumbnail(url=user_minecraft_skin)
                await initial_menu.setup_buttons()
                await interaction.response.send_message(embed=embed, view=initial_menu, ephemeral = True)
            else:
                embed = embed_creation(current_profile, current_cute_name, username, user_minecraft_skin, data, uuid)
                await initial_menu.setup_buttons(current_active_profile_id=current_profile)
                await interaction.response.send_message(embed=embed, view=initial_menu, ephemeral = True)
        except KeyError:
            embed = discord.Embed(title="SkyBlock Skills", description="Please enter a valid username.", type='rich', color=0x00b0f4, timestamp=datetime.now())
            await interaction.response.send_message(embed=embed, ephemeral = True)
        except Exception:
            await interaction.response.send_message(content="There has been an error with this command. Please try again at another time.", ephemeral = True)






async def setup(bot):
    await bot.add_cog(skill_menu(bot))
