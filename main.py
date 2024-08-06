import openai
import os
import sys
import re
import shutil
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
#this is just a place holder for now
openai.api_key = os.environ['OPENAI_API_KEY']
client = OpenAI()

def extract_youtube_id(url):
    # This pattern looks for '?v=' followed by exactly 11 characters (alphanumeric and underscore)
    pattern = r'(?<=v=)[\w-]{11}'
    match = re.search(pattern, url)
    if match:
        return match.group()
    else:
        return None

def get_transcription(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_transcript = ''.join([line['text'] + '\n' for line in transcript])
    return full_transcript

def generate_podcast_summary(transcription):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You will create podcast summaries. The user will submit a text that you will analyze. It will be an AI-focused podcast and you need to provide detailed notes for it. Please provide a thorough and accurate summary with the following structure:\n1. Introduction (100-150 words):\n   - Brief overview of the podcast\n   - Key speakers\n   - Main topic\n   - Context of the discussion\n2. Key Points (10 points, 100-150 words each):\n   - Highlight the 10 most important ideas or concepts discussed\n   - Provide specific information or quotes where relevant\n   - Aim for a balance between breadth and depth\n3. Concise Summary (200-250 words):\n   - Encapsulate the main themes and insights\n   - Tie together the key points\n   - Provide an overarching understanding of the podcast's content\nBefore you start writing, take a pause and think step-by-step about this request. Then create your output in .md file format, aiming for a total word count of approximately 1500-2000 words"
            },
            {
                "role": "user",
                "content": transcription
            }
        ],
        temperature=1,
        max_tokens=16383,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    content = response.choices[0].message.content
        
    
    return content
    
transcription = ""
url = ""
content = ""
urls = input("Enter URLs separated by commas: ").split(",")
for url in urls:
    url = url.strip()  # Remove any extraneous whitespace
    video_id = extract_youtube_id(url)
    if video_id:
        transcription = get_transcription(video_id)
        content += str(generate_podcast_summary(transcription))
    else:
        print(f'Failed to extract video ID from {url}')

# Check for text files in podcast_texts directory
podcast_texts_dir = 'podcast_texts'
podcast_texts_reviewed_dir = 'podcast_texts_reviewed'

if not os.path.exists(podcast_texts_reviewed_dir):
    os.makedirs(podcast_texts_reviewed_dir)

for filename in os.listdir(podcast_texts_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(podcast_texts_dir, filename)
        with open(file_path, 'r') as file:
            text_content = file.read()
            content += str(generate_podcast_summary(text_content))

        # Move the file to the reviewed directory
        shutil.move(file_path, os.path.join(podcast_texts_reviewed_dir, filename))
    

# Call the function to generate the podcast summary
if os.path.exists('podcast_summary.md'):
    with open('podcast_summary.md', 'a') as f:
        f.write(content)
else:
    with open('podcast_summary.md', 'w') as f:
        f.write(content)

print(content)
