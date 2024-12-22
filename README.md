# TurboDL Discord Bot

A Discord bot that downloads YouTube videos as MP3 or MP4 files.

## Features

- Download YouTube videos as MP3 or MP4
- Role-based access control
- Automatic file hosting for large files
- Auto-cleanup of downloaded files

## Prerequisites

- Python 3.8+
- FFmpeg
- Screen (for Linux deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TheBeaconCrafter/turbodl-discord
cd turbodl-discord
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install discord.py python-dotenv yt-dlp
```

4. Create a `.env` file with the following variables:
```
DISCORD_TOKEN=your_bot_token
ROLE_ID=role_id_for_access
HOST=your_domain_or_ip
PORT=9318
```

## Usage

### Starting the Bot

On Linux:
```bash
chmod +x start.sh
./start.sh
```

The bot will run in a screen session named 'turbodl'.

### Discord Commands

- `/download url:<youtube-url> filetype:<mp3/mp4>` - Download a YouTube video

### Managing the Bot

- Attach to screen: `screen -r turbodl`
- Detach from screen: Press `Ctrl+A` then `D`
- Stop the bot: Attach to screen and press `Ctrl+C`

## Notes

- Files larger than 8MB will be hosted on the built-in web server
- Hosted files are automatically deleted after 2 minutes
- The web server runs on port 9318 by default
