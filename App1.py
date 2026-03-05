import streamlit as st
import os
import base64
import io
import uuid
from datetime import datetime
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS

# Azure Cosmos DB imports
from azure.cosmos import CosmosClient, exceptions

# --- 1. PAGE CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="KrishivanX - AI Crop Doctor", page_icon="🌾", layout="centered")

# Custom CSS for adaptive Dark/Light mode and styling
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #2E7D32; text-align: center; }
    .sub-title { font-size: 1.2rem; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; background-color: #2E7D32; color: white; border-radius: 8px; }
    .history-card { padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CREDENTIALS & API SETUP ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
COSMOS_URI = os.environ.get("COSMOS_URI")
COSMOS_KEY = os.environ.get("COSMOS_KEY")

# Initialize OpenAI Client (using GitHub Models API)
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=GITHUB_TOKEN,
)

# Initialize Azure Cosmos DB Client
container = None
if COSMOS_URI and COSMOS_KEY:
    try:
        cosmos_client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
        database = cosmos_client.get_database_client("KrishivanData")
        container = database.get_container_client("ChatHistory")
    except Exception as e:
        st.sidebar.error("Database connection issue. Running in stateless mode.")

# --- 3. HELPER FUNCTIONS ---
def save_to_database(user_query, ai_response, interaction_type):
    """Saves the chat history to Azure Cosmos DB"""
    if container is None:
        return
    
    chat_item = {
        "id": str(uuid.uuid4()),
        "userId": "farmer_001",  # Hardcoded for the demo
        "type": interaction_type,
        "query": user_query,
        "response": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        container.create_item(body=chat_item)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

def encode_image(image_file):
    """Encodes uploaded image to Base64 for GPT-4o Vision"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def generate_audio(text, lang_code):
    """Converts text to audio using gTTS"""
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except Exception as e:
        st.error("Audio generation failed for this language.")
        return None

def process_voice_input(audio_bytes, lang_code):
    """Converts user's voice to text using SpeechRecognition"""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
        # Convert to text using Google's free Web Speech API
        text = r.recognize_google(audio_data, language=lang_code)
        return text
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except Exception as e:
        return f"Error processing audio: {e}"

# --- 4. APP LAYOUT & LOGIC ---
st.markdown('<div class="main-title">🌾 KrishivanX</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your AI Agricultural Assistant</div>', unsafe_allow_html=True)

# Language Selection Dictionary (Mapping to gTTS/SpeechRecognition codes)
LANGUAGES = {
    "English": "en", "Hindi": "hi", "Marathi": "mr", "Bengali": "bn",
    "Telugu": "te", "Tamil": "ta", "Kannada": "kn", "Malayalam": "ml",
    "Gujarati": "gu", "Punjabi": "pa"
}
selected_lang_name = st.selectbox("Select Your Language / अपनी भाषा चुनें", list(LANGUAGES.keys()))
lang_code = LANGUAGES[selected_lang_name]

# App Tabs
tab1, tab2, tab3 = st.tabs(["📷 Crop Doctor", "🎙️ Voice Assistant", "🗄️ My History"])

# --- TAB 1: CROP DOCTOR (VISION) ---
with tab1:
    st.write(f"**Upload a photo of your crop to instantly identify diseases.** ({selected_lang_name})")
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Crop Image", use_container_width=True)
        
        if st.button("Run AI Diagnostics"):
            if not GITHUB_TOKEN:
                st.error("API Key missing. Please check your Azure environment variables.")
            else:
                with st.spinner("Analyzing crop health..."):
                    base64_image = encode_image(uploaded_image)
                    
                    system_prompt = f"You are an expert Indian agronomist. Identify the crop disease in the image and provide a low-cost treatment. Respond strictly in {selected_lang_name}. Keep it under 50 words."
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": [
                                    {"type": "text", "text": "What is wrong with this plant?"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]}
                            ],
                            temperature=0.3
                        )
                        
                        ai_answer = response.choices[0].message.content
                        st.success("Analysis Complete!")
                        st.write(ai_answer)
                        
                        # Save to Database
                        save_to_database("Uploaded Image for Diagnosis", ai_answer, "Vision")
                        
                    except Exception as e:
                        st.error(f"AI Error: {e}")

# --- TAB 2: VOICE ASSISTANT ---
with tab2:
    st.write(f"**Ask about government schemes, weather, or farming advice.** ({selected_lang_name})")
    
    # Text Input Fallback
    text_query = st.text_input("Type your question here:")
    
    # Native Streamlit Audio Input
    audio_value = st.audio_input("Or click the microphone to speak")
    
    user_query = ""
    if audio_value:
        with st.spinner("Processing your voice..."):
            user_query = process_voice_input(audio_value.getvalue(), lang_code)
            st.info(f"You asked: {user_query}")
    elif text_query:
        user_query = text_query

    if user_query and user_query != "Sorry, could not understand the audio.":
        if st.button("Get AI Answer"):
            with st.spinner("Fetching information..."):
                system_prompt = f"You are a helpful agricultural assistant for Indian farmers. Answer the following query accurately. Respond strictly in {selected_lang_name}. Keep it simple and under 50 words."
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_query}
                        ],
                        temperature=0.5
                    )
                    
                    ai_answer = response.choices[0].message.content
                    st.write("### AI Response:")
                    st.write(ai_answer)
                    
                    # Generate Audio Output
                    audio_response = generate_audio(ai_answer, lang_code)
                    if audio_response:
                        st.audio(audio_response, format="audio/mp3")
                    
                    # Save to Database
                    save_to_database(user_query, ai_answer, "Chat/Voice")
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")

# --- TAB 3: MY HISTORY (COSMOS DB) ---
with tab3:
    st.write("**Your Past AI Consultations (Saved securely in Azure Cosmos DB)**")
    
    if st.button("Refresh History"):
        if container is None:
            st.warning("Database is not connected.")
        else:
            try:
                # Query the database for the user's history
                query = "SELECT * FROM c WHERE c.userId='farmer_001' ORDER BY c.timestamp DESC"
                items = list(container.query_items(query=query, enable_cross_partition_query=True))
                
                if not items:
                    st.info("No history found yet. Ask the AI a question!")
                else:
                    for item in items:
                        st.markdown(f"""
                        <div class="history-card">
                            <small style="color: gray;">{item.get('timestamp', '')[:10]} | Type: {item.get('type', 'Unknown')}</small><br>
                            <b>Q:</b> {item.get('query', '')}<br>
                            <b>A:</b> {item.get('response', '')}
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to fetch history: {e}")
