# region setup
import discord
from discord import app_commands
from discord.ext import commands
import os
import music_tag
from dotenv import load_dotenv
from downloader import download
from downloader import search_youtube
from spotify_scraper import SpotifyClient

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

bot_prefix = "nerd"
token = os.getenv("NERD_TOKEN")
download_path = "local"
video_path = "videos"

client = commands.Bot(
    command_prefix=[f"!{bot_prefix} ", f"!{bot_prefix} "],
    intents=intents)

if not os.path.exists(download_path):
    os.makedirs(download_path)


@client.event
async def on_ready():
    print('Roboduck is ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="ITS NERDMORTIE THE SHEEP!"))
    await client.tree.sync()
# endregion

def canonicalize_path(filename: str):
    return filename.replace(".webm", ".mp3").replace("\\", "/")

def get_metadata(file: str, metadata_name: str):
    f = music_tag.load_file(file)
    return str(f[metadata_name])

def set_metadata(file: str, metadata_name: str, value: str):
    f = music_tag.load_file(file)
    try:
        f[metadata_name] = value
        f.save()
        return "done"
    except Exception as e:
        return str(e)

async def search_songs(filter:str="title", query:str="None"):
    all_songs = []
    songs = []
    distinct_songs = []
    query = query.strip("```").replace("\\", "/")
    for path, subdirs, files in os.walk(download_path):
        if ".git" in path:
            continue
        for name in files:
            if name not in distinct_songs:
                distinct_songs.append(name)
                rel_path = os.path.join(path, name).removeprefix(download_path).replace("\\", "/")
                all_songs.append(rel_path)

    def safe_tag(tags, key):
        try:
            value = tags[key]
            return "" if value is None else str(value)
        except Exception:
            return ""

    song_dicts = []
    for song in all_songs:
        file_path = f"{download_path}/{song}"
        try:
            tags = music_tag.load_file(file_path)
        except Exception as e:
            tags = None

        song_dicts.append({
            "title": safe_tag(tags, "title"),
            "artist": safe_tag(tags, "artist"),
            "album": safe_tag(tags, "album"),
            "tracknumber": int(safe_tag(tags, "tracknumber").split("/")[0]) if safe_tag(tags, "tracknumber") != "" else 1,
            "file_path": song
        })

    if filter == "title":
        songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['title']).lower() or query.lower() in str(song['file_path']).lower()]
    elif filter == "artist":
        songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['artist']).lower()]
    elif filter == "album":
        songs_meta = [song for song in song_dicts if query.lower() in str(song['album']).lower()]
        songs_meta.sort(key=lambda song: song['tracknumber'])
        songs = [song['file_path'] for song in songs_meta]
    elif filter == "title_artist":
        try:
            query_list = query.split(",")
            title = query_list[0]
            artist = query_list[1]
            songs = [song['file_path'] for song in song_dicts if (title.lower() in str(song['title']).lower() or title.lower() in str(song['file_path']).lower()) and artist.lower() in str(song['artist']).lower()]
        except IndexError:
            songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['title']).lower() or query.lower() in str(song['file_path']).lower()]

    return(songs)

async def send_codeblock(ctx, msg, *, view=None):
    if len(msg) > 1993:
        if len(msg) > 3993:
            first_msg = msg[:1993]
            second_msg = msg[1993:3987]
            third_msg = msg[3987:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
            await ctx.send(f"```{third_msg}```")
        else:
            first_msg = msg[:1993]
            second_msg = msg[1993:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
    else:
        await ctx.send(f"```{msg}```", view=view)

async def download_from_youtube(url=None, *, folder=None):
    path = download_path
    if folder != None:
        path = download_path + "/" + folder

    filename = canonicalize_path(await download(url, audio=True, path=path))
    return filename

@client.hybrid_command(description="download audio from youtube")
@app_commands.describe(url="wat link i download", folder="wat folder under local")
async def download_audio(ctx, url=None, *, folder=None):
    await ctx.defer()

    filename = await download_from_youtube(url, folder)
    await ctx.send(f"saved it as `{filename}`", file=discord.File(filename))

@client.hybrid_command(description="download video from youtube")
@app_commands.describe(url="wat link i download", folder="wat folder under videos")
async def download_video(ctx, url=None, *, folder=None):
    await ctx.defer()

    if not os.path.exists(video_path):
        os.makedirs(video_path)

    path = video_path
    if folder != None:
        path = video_path + "/" + folder

    filename = canonicalize_path(await download(url, audio=False, path=path))
    await ctx.send(f"saved it as `{filename}`", file=discord.File(filename))

@client.hybrid_command()
async def get_local_file(ctx, filename=None):

    songs = await search_songs("title", filename)
    file = discord.File(download_path + songs[0])

    await ctx.send("ok", file=file)

@client.hybrid_command()
async def get_song_metadata(ctx, filename=None, metadata_name=None):

    songs = await search_songs("title", filename)
    metadata = get_metadata(download_path + songs[0], metadata_name)

    if metadata == "":
        metadata = "empty output"

    await send_codeblock(ctx, metadata)

@client.hybrid_command()
async def set_song_metadata(ctx, filename=None, metadata_name=None, metadata_value=None):

    songs = await search_songs("title", filename)
    metadata = set_metadata(download_path + songs[0], metadata_name, metadata_value)

    if metadata == "":
        metadata = "empty output"

    await send_codeblock(ctx, metadata)

@client.hybrid_command()
async def download_from_query(ctx, query=None):

    song_link = await search_youtube(query)

    await ctx.defer()
    filename = await download_from_youtube(song_link)
    await ctx.send(f"saved it as `{filename}`", file=discord.File(filename))

@client.hybrid_command()
async def download_from_spotify(ctx, url=None):

    with SpotifyClient() as client:
        results = client.get_track(url)
        track_name = results.name
        track_artist = results.artists[0].name

        song_link = await search_youtube(track_name + " " + track_artist)

    await ctx.defer()
    filename = await download_from_youtube(song_link)
    await ctx.send(f"saved it as `{filename}`", file=discord.File(filename))

@client.hybrid_command()
async def get_metadata_list(ctx):

    metadata = """
album
albumartist
artist
artwork
comment
compilation
composer
discnumber
genre
lyrics
totaldiscs
totaltracks
tracknumber
tracktitle
year
isrc
#bitrate (read only)
#codec (read only)
#length (read only)
#channels (read only)
#bitspersample (read only)
#samplerate (read only)
"""

    await send_codeblock(ctx, metadata)

@client.hybrid_command()
@app_commands.choices(filter=[
    app_commands.Choice(name='title', value="title"),
    app_commands.Choice(name='artist', value="artist"),
    app_commands.Choice(name='album', value='album'),
    app_commands.Choice(name='title + artist', value="title_artist")
])
async def search(ctx, filter="title", query=None):

    songs = await search_songs(filter, query)

    msg = "\n".join(songs)
    await send_codeblock(ctx, msg)

client.run(token)