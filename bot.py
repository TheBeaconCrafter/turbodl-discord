import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import uuid

# Required ENV variables: DISCORD_TOKEN, ROLE_ID, PORT, HOST
# ROLE_ID for users allowed to download
# PORT for the web server
# HOST (example: "example.org")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ROLE_ID = int(os.getenv("ROLE_ID"))
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
PORT = os.getenv("PORT", 9318)
HOST = os.getenv("HOST", "localhost")

BASE_DIR = os.getcwd()
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Set Content-Disposition header for download
        self.send_header("Content-Disposition", f'attachment; filename="{self.path.split("/")[-1]}"')
        super().end_headers()

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except ConnectionResetError:
            print(f"Client disconnected while downloading - this is normal")
        except BrokenPipeError:
            print(f"Broken pipe while downloading - this is normal")

def start_server():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.chdir(UPLOADS_DIR)
    server = HTTPServer(('0.0.0.0', int(PORT)), CustomHTTPRequestHandler)
    server.serve_forever()

# Start the web server in a separate daemon thread
threading.Thread(target=start_server, daemon=True).start()

@bot.event
async def on_ready():
    print("Bot is ready.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@bot.tree.command(name="download", description="Download from YouTube")
@app_commands.describe(url="YouTube link", filetype="mp3 or mp4")
async def download(interaction: discord.Interaction, url: str, filetype: str):
    if ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Validate YouTube URL
    if not any(x in url for x in ['youtube.com/', 'youtu.be/']):
        await interaction.response.send_message("Please provide a valid YouTube URL.", ephemeral=True)
        return

    await interaction.response.defer()
    filename = f"download_audio_{uuid.uuid4().hex}"
    download_path = os.path.join(UPLOADS_DIR, filename)
    ydl_opts = {"outtmpl": download_path + ".%(ext)s"}
    if filetype.lower() == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        })
        final_filename = filename + ".mp3"
    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        })
        final_filename = filename + ".mp4"

    final_path = os.path.join(UPLOADS_DIR, final_filename)
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    threshold_mb = 8
    file_size = os.path.getsize(final_path)
    if file_size > threshold_mb * 1024 * 1024:
        # Host the file on the web server
        upload_link = f"http://{HOST}:{PORT}/{final_filename}"
        await interaction.followup.send(
            f"File is available here: {upload_link}. It will be deleted in 2 minutes.",
            ephemeral=True
        )
        # Schedule file deletion after 2 minutes
        threading.Timer(120, lambda: os.remove(final_path)).start()
    else:
        try:
            await interaction.followup.send(file=discord.File(final_path))
            os.remove(final_path)
        except discord.HTTPException as e:
            if e.code == 40005:
                file_size = os.path.getsize(final_path)
                await interaction.followup.send(
                    f"Request entity too large. "
                    f"File size: {file_size} bytes. "
                    f"Zipping was not attempted.",
                    ephemeral=True
                )
                os.remove(final_path)
                return
            raise

bot.run(TOKEN)