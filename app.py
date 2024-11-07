from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Load the questions data from JSON file
def load_questions():
    with open("questions_data.json", "r") as json_file:
        return json.load(json_file)

questions_data = load_questions()

@app.route("/")
def index():
    return "Welcome to the Trivio!"

@app.route("/questions", methods=["GET"])
def get_questions():
    return jsonify(questions_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
