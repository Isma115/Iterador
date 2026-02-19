# youtube_transcript.py
import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """Extracts the YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(url):
    """
    Fetches the public transcript of a YouTube video.
    
    Returns a dict with keys: title, content, source, link
    Raises ValueError on invalid URL or if transcript is unavailable.
    """
    video_id = extract_video_id(url.strip())
    if not video_id:
        raise ValueError("URL de YouTube no válida. Formatos aceptados:\n"
                         "• https://www.youtube.com/watch?v=XXXXX\n"
                         "• https://youtu.be/XXXXX\n"
                         "• https://youtube.com/shorts/XXXXX")

    api = YouTubeTranscriptApi()
    try:
        # Try Spanish first, then English, then let it pick any available
        try:
            transcript = api.fetch(video_id, languages=['es', 'es-ES'])
        except Exception:
            try:
                transcript = api.fetch(video_id, languages=['en'])
            except Exception:
                # List all available and fetch the first one
                transcript_list = api.list(video_id)
                first = next(iter(transcript_list))
                transcript = first.fetch()
    except Exception as e:
        error_msg = str(e)
        if 'disabled' in error_msg.lower():
            raise ValueError("Las transcripciones están desactivadas para este vídeo.")
        elif 'no transcript' in error_msg.lower() or 'not found' in error_msg.lower():
            raise ValueError("No se encontró transcripción disponible para este vídeo.")
        else:
            raise ValueError(f"Error al obtener la transcripción: {error_msg}")

    # Join all transcript segments into a single text
    lines = []
    for entry in transcript:
        text = entry.text.strip() if hasattr(entry, 'text') else str(entry).strip()
        if text:
            lines.append(text)

    if not lines:
        raise ValueError("La transcripción del vídeo está vacía.")

    content = ' '.join(lines)

    return {
        'title': f'Transcripción de YouTube ({video_id})',
        'content': content,
        'source': 'YouTube',
        'link': url.strip(),
    }
