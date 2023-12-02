from django.shortcuts import render
from googletrans import Translator
import time
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound


def parse_timestamp(timestamp):
    try:
        if isinstance(timestamp, float):

            start_seconds = int(timestamp)
            end_seconds = start_seconds + 4
        else:

            parts = timestamp.split(' -> ')


            if len(parts) == 2:
                start, end = parts


                start_time = time.strptime(start, '%H:%M:%S')
                end_time = time.strptime(end, '%H:%M:%S')


                start_seconds = start_time.tm_hour * 3600 + start_time.tm_min * 60 + start_time.tm_sec
                end_seconds = end_time.tm_hour * 3600 + end_time.tm_min * 60 + end_time.tm_sec
            else:

                return None, None
    except (ValueError, AttributeError):
        return None, None

    return start_seconds, end_seconds


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['hy', 'en'])
    except NoTranscriptFound:
        return "No transcript found for the video."

    sub_items = []
    for i, entry in enumerate(transcript, start=1):
        start_time, end_time = parse_timestamp(entry['start'])
        if start_time is None or end_time is None:
            print(f"Error parsing timestamp for subtitle {i}: {entry['start']}")
            continue

        text = entry['text']

        start_time_str = time.strftime('%H:%M:%S', time.gmtime(start_time))
        end_time_str = time.strftime('%H:%M:%S', time.gmtime(end_time))

        sub_item = f"{i}\n{start_time_str} --> {end_time_str}\n{text}\n\n"
        sub_items.append(sub_item)

    return ''.join(sub_items)


def translate_to_armenian(text):
    if not text:
        return "No text to translate"

    translator = Translator()
    max_length = 5000

    text_parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]

    translated_parts = []
    for part in text_parts:
        try:
            translated_part = translator.translate(part, dest='hy').text
            translated_parts.append(translated_part)
        except Exception as e:
            return f"Translation error: {str(e)}"

    translated_text = ' '.join(translated_parts)
    return translated_text


def index(request):
    cdd = time.time()
    video_id = ''
    transcript_text = ''
    translated_text = ''

    if request.method == 'POST':
        video_id = request.POST.get('video_id', '')

        if video_id:

            transcript_text = get_transcript(video_id)
            translated_text = translate_to_armenian(transcript_text)

    dc = time.time()
    timee = dc - cdd
    return render(request, 'index.html',
                  {'video_id': video_id, 'transcript_text': transcript_text, 'translated_text': translated_text, 'time': timee})
