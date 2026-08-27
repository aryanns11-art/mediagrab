import yt_dlp

def get_video_info(url):

    options={
        'quiet':True,
        'no_warnings':True,
        'skip_download':True,
        }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)


    format = []


    for video_format in info.get('formats',[]):

        height = video_format.get('height')
        ext = video_format.get('ext')
        video_codec = video_format.get('vcodec')
        audio_codec = video_format.get('acodec')

        if(height and ext and video_codec and audio_codec):
            format.append({
                'format_id':video_format.get('format_id'),
                'height':height,
                'ext':ext,
                'video_codec':video_codec,
                'audio_codec':audio_codec
            })

    return {
        'title': info.get('title','Unknown'),
        'channel': info.get('channel','Unknown Channel'),
        'duration':info.get('duration',0),
        'thumbnail':info.get('thumbnail','Unknown Thumbnail'),
        'formats': format
    }