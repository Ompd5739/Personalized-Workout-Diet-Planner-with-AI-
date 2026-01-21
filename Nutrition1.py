from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import requests
from PIL import Image
import base64
import json

# ---------------- CONFIG ----------------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Gemini API key not found in .env file")
    st.stop()

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-1.5-flash:generateContent"
)

# ---------------- GEMINI REST CALL ----------------
def gemini_text(prompt):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        f"{GEMINI_URL}?key={API_KEY}",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        return f"❌ Error: {response.text}"

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def gemini_vision(prompt, image_file):
    image_bytes = image_file.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": image_file.type,
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        f"{GEMINI_URL}?key={API_KEY}",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        return f"❌ Error: {response.text}"

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Health Companion", layout="wide")
st.header("🤖 AI Health Companion")

# ---------------- SESSION STATE ----------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "goals": "Lose 10 pounds in 3 months\nImprove cardiovascular health",
        "conditions": "None",
        "routine": "30-minute walk 3x/week",
        "preferences": "Vegetarian\nLow carb",
        "restrictions": "No dairy\nNo nuts"
    }

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.subheader("Your Health Profile")

    st.session_state.profile["goals"] = st.text_area(
        "Health Goals", st.session_state.profile["goals"]
    )
    st.session_state.profile["conditions"] = st.text_area(
        "Medical Conditions", st.session_state.profile["conditions"]
    )
    st.session_state.profile["routine"] = st.text_area(
        "Fitness Routine", st.session_state.profile["routine"]
    )
    st.session_state.profile["preferences"] = st.text_area(
        "Food Preferences", st.session_state.profile["preferences"]
    )
    st.session_state.profile["restrictions"] = st.text_area(
        "Dietary Restrictions", st.session_state.profile["restrictions"]
    )

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["🥗 Meal Plan", "📷 Food Analysis", "💡 Health Insights"])

# ---------------- MEAL PLAN ----------------
with tab1:
    st.subheader("Personalized Meal Plan")

    if st.button("Generate Meal Plan"):
        profile = st.session_state.profile

        prompt = f"""
You are a professional nutritionist.
Create a 7-day personalized meal plan.

Goals: {profile['goals']}
Conditions: {profile['conditions']}
Routine: {profile['routine']}
Preferences: {profile['preferences']}
Restrictions: {profile['restrictions']}

Include calories and reasons for food choices.
"""
        with st.spinner("Generating with Gemini..."):
            result = gemini_text(prompt)

        st.markdown(result)

# ---------------- FOOD ANALYSIS ----------------
with tab2:
    uploaded = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])

    if uploaded:
        st.image(Image.open(uploaded), use_column_width=True)

        if st.button("Analyze Food"):
            prompt = """
Analyze this food image.
Provide calories, macros, health benefits, and concerns.
"""
            with st.spinner("Analyzing food..."):
                result = gemini_vision(prompt, uploaded)

            st.markdown(result)

# ---------------- HEALTH INSIGHTS ----------------
with tab3:
    question = st.text_input("Ask a health question")

    if st.button("Get Insight"):
        prompt = f"""
You are a certified health expert.
Answer the question clearly and scientifically:

{question}
"""
        with st.spinner("Thinking..."):
            result = gemini_text(prompt)

        st.markdown(result)

st.markdown("---")
st.caption("Gemini REST API • Python 3.14 • Streamlit • Edunet AIML Project")
