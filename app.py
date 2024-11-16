from flask import Flask, jsonify, request
import json
import os
from youtube_transcript_api import YouTubeTranscriptApi
import random
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerationConfig
import json
import os
import time
from flask_cors import CORS
app = Flask(__name__)
CORS(app)



# created a schema/format to give to the llm ki aise format ki json me data return kar
import typing_extensions as typing

# CORS(app)

# Load the questions data from JSON file
# def load_questions():
#     with open("questions_data.json", "r") as json_file:
#         return json.load(json_file)

# questions_data = load_questions()

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
        if (question_data):
            print(f"question generated successfully for chunk {i + 1}")
            question_data["timestamp"] = timestamp
            questions_data.append(question_data)  
        time.sleep(0.5)          
    return jsonify(questions_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)


# utility functions
def pre_processing(video_id):
    t=YouTubeTranscriptApi.get_transcript(video_id)

    timestamps_prefix_sum = []
    running_total  = 0
    for segment in t:
        sentence = segment["text"]
        curr_words = segment["text"].split()
        running_total += len(curr_words)
        # potential problem here.. the 2nd value of this tuple is sometimes exceeding the length of the vid (in seconds).
        # timestamps_prefix_sum.append((running_total, segment["start"] + segment["duration"], sentence))

        # best solution according to me: use segment["start"] instead of segment["start"] + segment["duration"]
        timestamps_prefix_sum.append((running_total, segment["start"], sentence))

    total_words = timestamps_prefix_sum[-1][0]
    return timestamps_prefix_sum, total_words

def mod_binary_search(target, timestamps_prefix_sum):
    left = 0
    right = len(timestamps_prefix_sum) - 1
    while left < right:
        mid = (left + right) // 2
        if timestamps_prefix_sum[mid][0] < target:
            left = mid + 1
        else:
            right = mid
    return left 


def split_text_into_chunks(video_id):
    num_questions = random.randint(8, 10) # you can change the number of questions you want to generate
    print(f"Generating {num_questions} questions from the transcript...")
    prefix_sum, total_words = pre_processing(video_id)
    max_words = total_words // num_questions
    parsed = 0
    chunks = []
    while (parsed < total_words):
        if (parsed + 2 * max_words > total_words):
            parsed = total_words
        else:
            parsed = parsed + max_words
        target_index = mod_binary_search(parsed, prefix_sum)
        timestamp = prefix_sum[target_index][1]
        chunk = ' '.join(sentence for _, _, sentence in prefix_sum[:target_index])
        chunks.append((chunk, timestamp))
        prefix_sum = prefix_sum[target_index:]
    return chunks


class QA_data(typing.TypedDict):
    question: str
    answers: list[str]
    correct_answer: str


# Load environment variables, particularly GEMINI_KEY
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_KEY"))
config = GenerationConfig(temperature=0.9, response_mime_type="application/json", response_schema=QA_data)


def generate_questions_and_options(chunk):

    try:
        prompt = f'''You are a teacher. Generate one relevant multiple-choice question based on the information delimited by triple quotes below.
        Provide four answer choices and indicate the correct answer.
        
        Make sure the question starts directly without prefacing it with any other text.

        Follow the example format below

        Example format: 

        What color is the sky?
        A) Blue
        B) Green
        C) Purple
        D) Yellow
        Correct answer: A'''
        
        # Call the Gemini API
        response = genai.GenerativeModel("gemini-1.5-flash",
                                        system_instruction="You are an expert question maker and quizzer. Generate questions strictly from the given information.",
                                         generation_config=config)
        result = response.generate_content(prompt)
        
        # parsed the response object
        dict_to_return = json.loads(result.parts[0].text)
        return dict_to_return

    except Exception as e:
        print("could not generate questions", {e})
    

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