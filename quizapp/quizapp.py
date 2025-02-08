import streamlit as st
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Retrieve the Gemini API key from environment variables
api_key = os.getenv("API KEY")  # Ensure this is set in your .env file
API_URL = "https://api.gemini.com/v1/roles"  # Gemini API endpoint (check the docs for the correct one)

# Function to fetch questions from Gemini API
@st.cache_data
def fetch_questions(text_content, quiz_level):
    
    RESPONSE_JSON = {
        "mcqs": [
            {
                "mcq": "multiple choice question1",
                "options": {
                    "a": "choice here1",
                    "b": "choice here2",
                    "c": "choice here3",
                    "d": "choice here4",
                },
                "correct": "correct choice option in the form of a, b, c or d",
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "correct choice option in the form of a, b, c or d",
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "correct choice option in the form of a, b, c or d",
            }
        ]
    }

    # Template for Gemini API request
    PROMPT_TEMPLATE = """
    Text: {text_content}
    You are an expert in generating MCQ type quiz on the basis of provided content. 
    Given the above text, create a quiz of 3 multiple choice questions keeping difficulty level as {quiz_level}. 
    Make sure the questions are not repeated and check all the questions to be conforming the text as well.
    Make sure to format your response like RESPONSE_JSON below and use it as a guide.
    Ensure to make an array of 3 MCQs referring the following response json:
    
    {RESPONSE_JSON}
    """

    formatted_template = PROMPT_TEMPLATE.format(text_content=text_content, quiz_level=quiz_level, RESPONSE_JSON=json.dumps(RESPONSE_JSON))

    # Headers for Gemini API request
    headers = {
        "Authorization": f"Bearer {api_key}",  # Authorization header with the Gemini API key
        "Content-Type": "application/json"
    }

    # Request data to send to Gemini API
    data = {
        "model": "gemini",  # Replace with the appropriate model identifier if needed
        "prompt": formatted_template,
        "temperature": 0.3,
        "max_tokens": 1000,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    # Make the API request to Gemini
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        # Extract response JSON
        try:
            response_data = response.json()
            extracted_response = response_data.get("choices", [{}])[0].get("text", "").strip()

            # Convert extracted response to JSON and return the MCQs
            return json.loads(extracted_response).get("mcqs", [])
        except json.JSONDecodeError:
            st.error("Error decoding the response from Gemini.")
            return []
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return []

def main():
    st.title("Quiz Generator App")

    text_content = st.text_area("Paste the text content here:")

    quiz_level = st.selectbox("Select quiz level:", ["Easy", "Medium", "Hard"])

    quiz_level_lower = quiz_level.lower()

    session_state = st.session_state

    if 'quiz_generated' not in session_state:
        session_state.quiz_generated = False

    if not session_state.quiz_generated:
        session_state.quiz_generated = st.button("Generate Quiz")

    if session_state.quiz_generated:
        questions = fetch_questions(text_content=text_content, quiz_level=quiz_level_lower)

        selected_options = []
        correct_answers = []
        for question in questions:
            options = list(question["options"].values())
            selected_option = st.radio(question["mcq"], options, index=None)
            selected_options.append(selected_option)
            correct_answers.append(question["options"][question["correct"]])

        # Submit button
        if st.button("Submit"):
            # Display selected options
            marks = 0
            st.header("Quiz Result:")
            for i, question in enumerate(questions):
                    selected_option = selected_options[i]
                    correct_option = correct_answers[i]
                    st.subheader(f"{question['mcq']}")
                    st.write(f"You selected: {selected_option}")
                    st.write(f"Correct answer: {correct_option}")
                    if selected_option == correct_option:
                        marks += 1
            st.subheader(f"You scored {marks} out of {len(questions)}")

if __name__ == "__main__":
    main()
