# bot.py
import os
import random
import discord
import pybase64
import asyncio
import spotipy

from progressBar import filledBar
from PIL import Image
from dotenv import load_dotenv
from discord.ext import tasks
from discord import Spotify
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIFY_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIFY_USER_ID = os.getenv('SPOTIFY_USER_ID')
PRIVATE_CHANNEL_ID = int(os.getenv('PRIVATE_CHANNEL_ID'))
REDIRECT_URL = "http://localhost:8888/callback"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-public ugc-image-upload",
        redirect_uri=REDIRECT_URL,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_SECRET,
        cache_path="token.txt"
    )
)
intents = discord.Intents.all()
intents.message_content = True


# alternative search methods to: member in member_list
def indexSearch(item_list, item):
    try:
        index = item_list.index(item)
    except ValueError:
        index = -1

    return index >= 0


def setSearch(item_list, item):
    rand_list = set(item_list)
    return item in rand_list


def findExistingPlaylist(name):
    results = sp.user_playlists(user=SPOTIFY_USER_ID)
    for playlist in results['items']:
        if playlist['name'] == name:
            return playlist


def getPlaylistIds(playlist_id):
    r = sp.playlist_items(playlist_id)
    t = r['items']
    ids = []
    while r['next']:
        r = sp.next(r)
        t.extend(r['items'])
    for s in t: ids.append(s["track"]["id"])
    return ids


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_list = []
        self.song_list = []
        self.activities = ["League of Legends", "VALORANT", "Among Us", "Omori", "Hollow Knight", "Teamfight Tactics",
                           "Stardew Valley"]

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def setup_hook(self) -> None:
        self.update_lists.start()
        self.refresh_playlists.start()

    async def cycle_activity(self):
        name = self.activities[random.randint(0, len(self.activities) - 1)]
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=name))

    @tasks.loop(seconds=600)
    async def refresh_playlists(self):
        await self.cycle_activity()

        for member in self.member_list:
            await self.update_playlist(member)
            await asyncio.sleep(0.1)

        print("ALL PLAYLISTS UPDATED---------------")

    @tasks.loop(seconds=5)
    async def update_lists(self):
        for member in self.member_list:
            if member.status == discord.Status.invisible or len(member.activities) == 0:
                continue

            for activity in member.activities:
                if isinstance(activity, Spotify):
                    index = self.member_list.index(member)
                    if activity.track_id not in self.song_list[index]:
                        self.song_list[index].append(activity.track_id)
                        print("song added to " + member.name + ": " + activity.title)

    @update_lists.before_loop
    async def before_update_lists(self):
        await self.wait_until_ready()

    @refresh_playlists.before_loop
    async def before_refresh_playlists(self):
        await self.wait_until_ready()

    async def update_playlist(self, member):
        if member in self.member_list:
            index = self.member_list.index(member)
        else:
            return

        if len(self.song_list[index]) == 0:
            return

        if findExistingPlaylist(member.name) is not None:
            playlist = findExistingPlaylist(member.name)

            existing_songs = getPlaylistIds(playlist['id'])
            new_songs = []

            for song in self.song_list[index]:
                if song not in existing_songs:
                    new_songs.append(song)

            if len(new_songs) != 0:
                sp.playlist_add_items(playlist_id=playlist["id"], items=new_songs)
        else:
            playlist = sp.user_playlist_create(user=SPOTIFY_USER_ID,
                                               name=member.name, public=True)
            sp.playlist_add_items(playlist_id=playlist["id"], items=self.song_list[index])
        self.song_list[index] = []

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.channel.id == PRIVATE_CHANNEL_ID:
            guild = message.author.guild
            if str(client.user.id) in message.content:
                if message.content[23:].lower().startswith('updatecovers'):
                    playlists = sp.user_playlists(user=SPOTIFY_USER_ID)
                    existing_playlists = [playlist['name'] for playlist in playlists['items']]
                    update_progress = 0

                    await message.channel.send("updating all covers...")
                    msg = await message.channel.send(filledBar(len(existing_playlists), update_progress)[0])

                    for member in guild.members:
                        if member.name in existing_playlists:
                            playlist = findExistingPlaylist(member.name)

                            file_name = member.name + ".jpg"
                            await member.avatar.save(file_name)

                            image = Image.open(file_name)
                            resized_image = image.resize((512, 512))
                            resized_image = resized_image.convert('RGB')
                            resized_image.save(file_name)

                            with open(file_name, "rb") as f:
                                encoded_img = pybase64.b64encode(f.read()).decode("utf-8")

                            sp.playlist_upload_cover_image(playlist['id'], encoded_img)
                            await asyncio.sleep(0.1)

                            update_progress += 1
                            await msg.edit(content=filledBar(len(existing_playlists), update_progress)[0])

                    await message.channel.send("playlist covers updated")

                if message.content[23:].lower().startswith('test'):
                    await message.channel.send("test")
                    print([user.name for user in self.member_list])
                    print(self.song_list)

                if message.content[23:].lower().startswith('add'):
                    if message.content[28:].lower().startswith('all'):
                        playlists = sp.user_playlists(user=SPOTIFY_USER_ID)
                        existing_playlists = [playlist['name'] for playlist in playlists['items']]

                        for member in guild.members:
                            if member.name in existing_playlists:
                                self.member_list.append(member)
                                self.song_list.append([])
                                print("ADDED NEW USER: " + member.name)
                        await message.channel.send("added " + str(len(existing_playlists)) + " users")
                    else:
                        for member in guild.members:
                            if str(member.id) in message.content[23:]:
                                if member in self.member_list:
                                    await message.channel.send("user already added")
                                else:
                                    self.member_list.append(member)
                                    self.song_list.append([])
                                    await message.channel.send("user successfully added")
                                    print("ADDED NEW USER: " + member.name)

                if message.content[23:].lower().startswith('remove'):
                    for member in guild.members:
                        if str(member.id) in message.content[23:]:
                            if member in self.member_list:
                                index = self.member_list.index(member)
                                self.song_list.remove(self.song_list[index])
                                self.member_list.remove(member)
                                await message.channel.send("user successfully removed")
                                print("REMOVED USER: " + member.name)
                            else:
                                await message.channel.send("user is not being added")

                if message.content[23:].lower().startswith('list'):
                    list_1 = [user.name for user in self.member_list]
                    list_2 = [len(id_list) for id_list in self.song_list]
                    final_list = ' | '.join(f'{i + ": "}{j}' for i, j in zip(list_1, list_2))
                    if len(final_list) == 0:
                        await message.channel.send("no one is added")
                    else:
                        await message.channel.send(final_list)

                if message.content[23:].lower().startswith('getplaylist'):
                    for member in guild.members:
                        if str(member.id) in message.content[23:]:
                            if member in self.member_list:
                                await self.update_playlist(member)
                                playlist = findExistingPlaylist(member.name)
                                await message.channel.send("https://open.spotify.com/playlist/" + str(playlist["id"]))
                            else:
                                await message.channel.send(member.name + " is not being part of the list")

                if message.content[23:].lower().startswith('getallplaylists'):
                    for member in self.member_list:
                        await self.update_playlist(member)
                        playlist = findExistingPlaylist(member.name)
                        await message.channel.send("https://open.spotify.com/playlist/" + str(playlist["id"]))

                if message.content[23:].lower().startswith('updateplaylists'):
                    update_progress = 0
                    await message.channel.send("updating all playlists...")
                    msg = await message.channel.send(filledBar(len(self.member_list), update_progress)[0])

                    for member in self.member_list:
                        await self.update_playlist(member)
                        update_progress += 1
                        await msg.edit(content=filledBar(len(self.member_list), update_progress)[0])

                    print("ALL PLAYLISTS UPDATED---------------")
                    await message.channel.send("all playlists updated")

                if message.content[23:].lower().startswith('help'):
                    embed = discord.Embed(title='Bot Commands', description='There is no bot prefix, all commands must be called after pinging the bot. For more information about commands, use advhelp command')
                    commands_text = "add @pingsomeone, remove @pingsomeone, list, getplaylist @pingsomeone, getallplaylists, updateplaylists, updatecovers "
                    embed.add_field(name="Commands(7)", value=commands_text, inline=True)
                    embed.add_field(name="Info(2)", value='help, advhelp', inline=False)
                    await message.channel.send(embed=embed)

                if message.content[23:].lower().startswith('advhelp'):
                    await message.channel.send("ALL COMMANDS ARE CALLED BY PINGING THE BOT")
                    await message.channel.send("------------------------------------------")
                    await message.channel.send(
                        f"{'add @pingsomeone: ': <30}{'adds a user to the user_list list; all spotify activity will be recordered and the getplaylist command can be called on the user' : <50}")
                    await message.channel.send(
                        f"{'remove @pingsomeone:': <30}{'removes a user from the user_list list' : <50}")
                    await message.channel.send(
                        f"{'list: ': <50}{'returns users inside of user_list and number of recorded songs IDs in the session' : <50}")
                    await message.channel.send(
                        f"{'getplaylist @pingsomeone: ': <30}{'returns the updated spotify playlist for all the songs recorded' : <50}")
                    await message.channel.send(
                        f"{'getallplaylists: ': <30}{'updates and returns all playlists from the user_list' : <50}")
                    await message.channel.send(
                        f"{'updateplaylists: ': <30}{'updates all playlists (getallplaylists without sending the links)' : <50}")
                    await message.channel.send(
                        f"{'updatecovers: ': <30}{'updates all playlist covers of the users in the user_list' : <50}")

        if message.content.lower() == "among us":
            await message.add_reaction("👍")


client = MyClient(intents=intents)
client.run(TOKEN)
