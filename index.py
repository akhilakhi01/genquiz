import streamlit as st
import json
from google import generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi as yta

genai.configure(api_key='AIzaSyDwcocYIHnJsdhzM7xUyzquWo645tFHCYA')
model = genai.GenerativeModel("gemini-pro")

def getVideoId(url: str):
    return url.split("=")[1]
def get_quiz_data(text_result:str):
    return json.loads(text_result.replace("\n", ""))
def generate_quiz(youtube_link):
    video_id = getVideoId(youtube_link)
    transcripts = yta.get_transcript(video_id=video_id)
    transcript_text = ". ".join([obj['text'] for obj in transcripts])
    prompt = "For the below Context give me a mcq quiz questions with answer in a list of objects and this response should able to convert as JSON using json.loads function, each question is represented in python dict and the three keys must be question,options,answer , question(string)  options(list of strings and each string start with A. or B. or C. or D.) and answer should be exact option in the options. \n Context:" + transcript_text
    result = model.generate_content(contents=prompt)
    quiz_data = []
    if result:
        try:
            i1 = result.text.find('[')
            i2 = result.text.rfind(']')
            result_text = result.text[i1:i2+1]
            print(result_text)
            quiz_data = get_quiz_data(result_text)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    
    return quiz_data

def main():
    st.title("Create a quiz based on YouTube video")
    youtube_link = st.sidebar.text_input(label="Paste the YouTube Link below")
    
    if st.sidebar.button("Generate Quiz"):
        quiz_data = generate_quiz(youtube_link)
        st.session_state.quiz_data = quiz_data
        st.session_state.question_index = 0
        st.session_state.user_responses = {}
    if "quiz_data" in st.session_state:
        quiz_data = st.session_state.quiz_data
        question_index = st.session_state.question_index
        user_responses = st.session_state.user_responses
        
        if question_index < len(quiz_data):
            question = quiz_data[question_index]
            total_questions = len(quiz_data)
            st.write(f"Question {question_index + 1} of {total_questions}")
            selected_option = st.radio(label=question['question'], options=question['options'], key=question_index,index=None)
            user_responses[question['question']] = selected_option
            
            if st.button("Next"):
                st.session_state.question_index += 1
                st.experimental_rerun() 
        else:
            st.write("Quiz completed!")
            score = calculate_score(quiz_data, user_responses)
            st.write(f"Your score is: {score}/{len(quiz_data)}")

def calculate_score(quiz_data, user_responses):
    score = 0
    for question in quiz_data:
        if question['question'] in user_responses and user_responses[question['question']] == question['answer']:
            score += 1
    return score

if __name__ == "__main__":
    main()