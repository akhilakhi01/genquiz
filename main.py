import streamlit as st
import json
from google import generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi as yta
genai.configure(api_key='AIzaSyDwcocYIHnJsdhzM7xUyzquWo645tFHCYA')
model = genai.GenerativeModel("gemini-pro")
def getVideoId(url:str):
    return url.split("=")[1]
st.title("Create a quiz based on youtube video")
youtube_link = st.text_input(label ="Paste the Youtube Link below")
if youtube_link:
    video_id = getVideoId(youtube_link)
    transcripts =  yta.get_transcript(video_id=video_id)
    transcript_text = ". ".join([obj['text'] for obj in transcripts])
    # print(transcript_text)
    prompt = "For the below Context give me a mcq quiz questions with answer in a list of objects and this JSON should able to convert as JSON, each question is represented in python dict and the three keys must be question,options,answer , question(string)  options(list of strings and each string start with A. or B. or C. or D.) and answer should be char of either A or B or C or D. \n Context:"+transcript_text
    result = model.generate_content(contents=prompt)
    if(result):
        try:
            quiz_data = json.loads(result.text.replace("\n",""))
            if(quiz_data):
                print(quiz_data)
            if(quiz_data and len(quiz_data)):
                for i in quiz_data:
                    print(i)
                    st.radio(label=i['question'],options=i['options'],index=None)
        except json.JSONDecodeError as e:
            print("error decoding json",e)