from flask import Flask, jsonify, request
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
import random
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerationConfig
import time
from flask_cors import CORS
import typing

app = Flask(__name__)

# Allow CORS for all origins
CORS(app, resources={r"/questions": {"origins": "https://www.youtube.com"}})

@app.route("/")
def index():
    return "Welcome to the Trivio!"

@app.route("/questions", methods=["GET"])
def get_questions():
    url = request.headers.get('link')
    video_id = extract_video_id(url)
    chunks = split_text_into_chunks(video_id)
    questions_data = []

    # Process each chunk
    for i, (chunk, timestamp) in enumerate(chunks):
        print(f"Chunk {i + 1}:\n{chunk}\n")
        question_data = generate_questions_and_options(chunk)
        if question_data:
            print(f"Question generated successfully for chunk {i + 1}")
            question_data["timestamp"] = timestamp
            questions_data.append(question_data)  
        time.sleep(0.5)          
    return jsonify(questions_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)

# Utility functions
def pre_processing(video_id):
    t = YouTubeTranscriptApi.get_transcript(video_id)
    timestamps_prefix_sum = []
    running_total = 0
    for segment in t:
        sentence = segment["text"]
        curr_words = segment["text"].split()
        running_total += len(curr_words)
        timestamps_prefix_sum.append((running_total, segment["start"], sentence))
    total_words = timestamps_prefix_sum[-1][0]
    return timestamps_prefix_sum, total_words

def mod_binary_search(target, timestamps_prefix_sum):
    left, right = 0, len(timestamps_prefix_sum) - 1
    while left < right:
        mid = (left + right) // 2
        if timestamps_prefix_sum[mid][0] < target:
            left = mid + 1
        else:
            right = mid
    return left

def split_text_into_chunks(video_id):
    num_questions = random.randint(8, 10)
    print(f"Generating {num_questions} questions from the transcript...")
    prefix_sum, total_words = pre_processing(video_id)
    max_words = total_words // num_questions
    parsed = 0
    chunks = []
    while parsed < total_words:
        parsed = parsed + max_words if parsed + 2 * max_words <= total_words else total_words
        target_index = mod_binary_search(parsed, prefix_sum)
        timestamp = prefix_sum[target_index][1]
        chunk = ' '.join(sentence for _, _, sentence in prefix_sum[:target_index])
        chunks.append((chunk, timestamp))
        prefix_sum = prefix_sum[target_index:]
    return chunks

class QA_data(typing.TypedDict):
    question: str
    answers: list[str]
    correct_answer: list[str]



# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_KEY"))
config = GenerationConfig(temperature=0.9, response_mime_type="application/json", response_schema=QA_data)

def generate_questions_and_options(chunk):
    try:
        prompt = f'''Generate a question from the following text chunk:\n\n{chunk}\n\nProvide 4 options, with only 1 correct option.'''
        response = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction="You are an expert question maker and quizzer. Generate questions strictly from the given information",
            generation_config=config
        )
        result = response.generate_content(prompt)
        dict_to_return = json.loads(result.parts[0].text)
        return dict_to_return
    except Exception as e:
        print("Could not generate questions", {e})

import re
def extract_video_id(youtube_url):
    print(youtube_url)
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:v|embed|watch\?v=)|youtu\.be/)([\w-]{11})'
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        print("Invalid YouTube URL or no video ID found.")
        return None