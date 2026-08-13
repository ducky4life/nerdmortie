# nerdmortie

nerdmortie is a yt-dlp downloader as a discord bot.

both video and audio are supported with extended functions for audio metadata

features:

- download files in custom subfolders
- retrieval of songs using metadata/filename

if you would like to play the audio files on discord, check out https://github.com/ducky4life/smortie! a download from youtube command is built-in to smortie

alternatively, i also have a web version of this (also with docker support) https://github.com/ducky4life/Ducktube

## usage

make sure you have [python](https://www.python.org/downloads/) installed.

1. clone the repository
   ```
   git clone https://github.com/ducky4life/nerdmortie.git
   ```
2. move to directory
   ```
   cd nerdmortie
   ```
3. install dependencies
   ```
   pip install -r requirements.txt
   ```
   note that to use the download from spotify/query feature, please remove `proxies=self.proxy` from line 29 in `youtubesearchpython/core/requests.py`
4. create .env file
   ```
   touch .env
   ```
5. put your secrets in the .env file (without the brackets: `[ ]`)
   ```
   NERD_TOKEN="[your bot token]"
   ```
6. run nerdmortie.py
   ```
   python nerdmortie.py
   ```

altneratively, run the [Dockerfile](https://github.com/ducky4life/nerdmortie/blob/main/Dockerfile):

```
docker build -t nerdmortie:latest -f Dockerfile .
docker run --name nerdmortie nerdmortie:latest
```

note that you might have to replace the first line with `FROM python:3.11-slim` for your archetecture

## todo

- [ ] renaming files and editing metadata for audio files