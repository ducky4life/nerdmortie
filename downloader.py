import yt_dlp

async def download(url, audio=False, path="local"):
    if audio:
        ydl_opts = {
            'outtmpl': f'{path}/'+'%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'writesubtitles': 'true',
            'writethumbnail': 'true',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }, {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }, {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }]
        }
    else:
        ydl_opts = {
            'outtmpl': f'{path}/'+'%(title)s.%(ext)s',
            'format': 'best[ext=mp4][acodec!=none][vcodec!=none]/bestvideo+bestaudio/best',
            'writethumbnail': True,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'EmbedThumbnail',
            }, {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }]
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename