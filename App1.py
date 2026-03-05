import streamlit as st
import base64
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
import io
import os

# ==========================================
# 1. APP CONFIGURATION & PERSISTENT STATE
# ==========================================
st.set_page_config(page_title="KrishivanX", page_icon="🌱", layout="wide")

# Initialize Memory Vaults
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'stored_lang' not in st.session_state:
    st.session_state.stored_lang = 'English'
if 'img_response' not in st.session_state:
    st.session_state.img_response = None
if 'aud_response' not in st.session_state:
    st.session_state.aud_response = None

def save_lang():
    st.session_state.stored_lang = st.session_state.lang_widget

# !!! IMPORTANT: PASTE YOUR REAL TOKEN HERE !!!
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=GITHUB_TOKEN)

# 12 Supported Languages
SUPPORTED_LANGUAGES = {
    "English": ("en-IN", "en"),
    "Hindi (हिंदी)": ("hi-IN", "hi"),
    "Marathi (मराठी)": ("mr-IN", "mr"),
    "Bengali (বাংলা)": ("bn-IN", "bn"),
    "Telugu (తెలుగు)": ("te-IN", "te"),
    "Tamil (தமிழ்)": ("ta-IN", "ta"),
    "Kannada (ಕನ್ನಡ)": ("kn-IN", "kn"),
    "Malayalam (മലയാളം)": ("ml-IN", "ml"),
    "Gujarati (ગુજરાતી)": ("gu-IN", "gu"),
    "Punjabi (ਪੰਜਾਬੀ)": ("pa-IN", "pa"),
    "Odia (ଓଡ଼ିଆ)": ("or-IN", "or"),
    "Assamese (অসমীয়া)": ("as-IN", "as")
}

# ==========================================
# 2. THE CSS SLEDGEHAMMER (AUTO-SYNCS WITH BROWSER)
# ==========================================
@st.cache_data
def get_cached_css():
    css = """
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

        /* 1. CSS VARIABLES (AUTO-DETECT BROWSER THEME) */
        :root {
            --bg-color: #ffffff;
            --text-color: #000000;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --input-bg: #f8f9fa;
            --primary-green: #8CC63F;
        }

        /* If the user's system is in dark mode, these colors take over automatically! */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #121212;
                --text-color: #ffffff;
                --card-bg: #1E1E1E;
                --border-color: #333333;
                --input-bg: #2b2b2b;
            }
        }

        /* 2. FORCE GLOBAL BACKGROUNDS & ZERO PADDING */
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: var(--bg-color) !important;
            background-image: none !important;
            padding: 0px !important;
        }
        
        .main .block-container { 
            padding-top: 0rem !important; 
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
            max-width: 1200px; 
        }
        
        header[data-testid="stHeader"] { display: none !important; }
        
        html, body, p, span, h1, h2, h3, h4, h5, h6, label, div {
            color: var(--text-color) !important;
            font-family: 'Segoe UI', Tahoma, sans-serif !important;
        }

        /* 3. FIX DROPDOWN MENUS (SOLID COLORS BASED ON THEME) */
        [data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
        }
        [data-testid="stSelectbox"] span { color: var(--text-color) !important; font-weight: bold !important; }
        div[data-baseweb="popover"] > div, ul[data-baseweb="menu"] { background-color: var(--card-bg) !important; }
        ul[data-baseweb="menu"] li {
            color: var(--text-color) !important;
            background-color: var(--card-bg) !important;
            font-weight: bold !important;
        }
        ul[data-baseweb="menu"] li:hover, ul[data-baseweb="menu"] li[aria-selected="true"] {
            background-color: var(--primary-green) !important; color: #ffffff !important;
        }

        /* 4. FIX TOGGLE BUTTONS (Take Photo/Upload) */
        [data-testid="stRadio"] [role="radio"] { display: none !important; }
        [data-testid="stRadio"] label {
            background-color: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            padding: 10px 24px !important;
            border-radius: 25px !important;
            cursor: pointer !important;
            margin-right: 10px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stRadio"] label p { font-weight: bold !important; font-size: 16px !important; margin: 0 !important; }
        [data-testid="stRadio"] label[data-checked="true"] {
            background-color: var(--primary-green) !important; border-color: var(--primary-green) !important;
        }
        [data-testid="stRadio"] label[data-checked="true"] p { color: #ffffff !important; }
        [data-testid="stRadio"] > div { display: flex; justify-content: center; }

        /* 5. MAIN ACTION BUTTONS */
        button[kind="primary"] {
            background-color: var(--primary-green) !important;
            color: #ffffff !important; border-radius: 25px !important; border: none !important;
            padding: 10px 30px !important; font-weight: bold !important;
        }
        button[kind="primary"]:hover { transform: scale(1.05); }
        
        button[kind="secondary"] {
            border-radius: 25px !important; font-weight: bold !important; padding: 10px 30px !important;
            border: 2px solid var(--primary-green) !important; color: var(--text-color) !important;
            background-color: transparent !important;
        }

        /* 6. CARDS & UPLOADERS */
        .custom-card {
            background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px;
            padding: 30px; margin-top: 20px; margin-bottom: 20px; text-align: center;
        }
        [data-testid="stDropzone"] {
            background-color: var(--input-bg) !important; 
            border: 2px dashed var(--primary-green) !important; border-radius: 12px !important;
        }

        /* 7. GREEN BANNER */
        .green-banner {
            background-color: var(--primary-green); color: #ffffff !important;
            padding: 40px 20px; display: flex; justify-content: space-around;
            margin-top: 60px; margin-bottom: 0px; margin-left: -5rem; margin-right: -5rem;
        }
        .banner-item { display: flex; align-items: center; gap: 15px; flex: 1; padding: 0 20px; }
        .banner-item i, .banner-item h3, .banner-item p { color: #ffffff !important; }
        .banner-item h3 { font-size: 18px; font-weight: 900; margin: 0 0 5px 0; }
        .banner-item p { font-size: 13px; margin: 0; }
        
        .header-pad { padding-top: 20px; }
        .footer-pad { padding-bottom: 20px; }
    </style>
    """
    return css

def inject_custom_css():
    css = get_cached_css()
    st.markdown(css, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def generate_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        sound_file = io.BytesIO()
        tts.write_to_fp(sound_file)
        sound_file.seek(0)
        st.audio(sound_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Audio error: {e}")

# ==========================================
# 4. TOP NAVIGATION BAR
# ==========================================
def render_top_nav(current_page):
    st.markdown('<div class="header-pad"></div>', unsafe_allow_html=True)
    c_logo, c_nav = st.columns([1, 2], vertical_alignment="center")
    with c_logo:
        st.markdown(f"<h2 style='margin:0;'><i class='fa-solid fa-leaf' style='color:#8CC63F;'></i> KrishivanX</h2>", unsafe_allow_html=True)
    with c_nav:
        nav = st.radio("Navigation", ["Home", "Image Input", "Audio Input"], index=["Home", "Image Input", "Audio Input"].index(current_page), horizontal=True, label_visibility="collapsed", key=f"nav_{current_page}")
        if nav != current_page:
            st.session_state.page = nav
            st.rerun()

# ==========================================
# 5. PAGE 1: HOME (LANDING PAGE)
# ==========================================
def page_home():
    st.markdown('<div class="header-pad"></div>', unsafe_allow_html=True)
    # Notice we removed the theme dropdown column to make it cleaner!
    c1, c2, c3 = st.columns([5, 1, 1], vertical_alignment="center")
    with c1:
        st.markdown(f"<h2 style='margin:0;'><i class='fa-solid fa-leaf' style='color:#8CC63F;'></i> KrishivanX</h2>", unsafe_allow_html=True)
    with c3:
        current_lang_idx = list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.stored_lang)
        st.selectbox("Language", list(SUPPORTED_LANGUAGES.keys()), index=current_lang_idx, key="lang_widget", on_change=save_lang, label_visibility="collapsed")

    st.markdown("""
        <div style="text-align: center; margin-top: 80px; margin-bottom: 40px;">
            <i class="fa-solid fa-tractor" style="font-size: 100px;"></i>
            <h1 style="font-size: 45px; font-weight: 900; margin-top: 20px;">Welcome to KrishivanX</h1>
        </div>
    """, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("Get started", type="primary", use_container_width=True):
            st.session_state.page = "Image Input"
            st.rerun()

    st.markdown("""
        <div class="green-banner">
            <div class="banner-item">
                <i class="fa-solid fa-camera"></i>
                <div><h3>Photo Upload</h3><p>Easily analyze your crops with images.</p></div>
            </div>
            <div class="banner-item">
                <i class="fa-solid fa-volume-high"></i>
                <div><h3>Audio Feedback</h3><p>Hear insights and guidance from experts.</p></div>
            </div>
            <div class="banner-item">
                <i class="fa-solid fa-sun"></i>
                <div><h3>Weather Insights</h3><p>Stay updated with real-time forecasts.</p></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='padding: 20px 0;'><b><i class='fa-solid fa-leaf' style='color:#8CC63F;'></i> KrishivanX</b> <span style='float:right;'><i class='fa-regular fa-face-smile'></i> KrishivanX</span></div>", unsafe_allow_html=True)
    st.markdown('<div class="footer-pad"></div>', unsafe_allow_html=True)

# ==========================================
# 6. PAGE 2: IMAGE INPUT
# ==========================================
def page_image():
    render_top_nav("Image Input")

    st.markdown("<h2 style='text-align:center; margin-top:30px;'>Upload or Capture Your Image</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'>Choose an option below to get started</div>", unsafe_allow_html=True)

    img_mode = st.radio("mode", ["Take Photo", "Upload Image"], horizontal=True, label_visibility="collapsed")

    img_to_process = None
    if img_mode == "Take Photo":
        img_to_process = st.camera_input("Take a picture", label_visibility="collapsed")
    else:
        img_to_process = st.file_uploader("Upload Image", type=["jpg", "png"], label_visibility="collapsed")

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;'>Generated Responses</h4>", unsafe_allow_html=True)
    
    res_placeholder = st.empty()
    
    if img_to_process is not None and st.button("Run AI Diagnostics", type="primary"):
        with st.spinner("Analyzing..."):
            base64_image = base64.b64encode(img_to_process.read()).decode('utf-8')
            lang_name = st.session_state.stored_lang 
            sys_prompt = f"Identify disease and list 2 treatments. Be concise. Respond in {lang_name}."
            
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}], 
                temperature=0.3)
            
            st.session_state.img_response = response.choices[0].message.content

    if st.session_state.img_response:
        res_placeholder.markdown(f'<div style="text-align:left; border:1px solid var(--border-color); padding:15px; border-radius:8px; margin-bottom:20px;">{st.session_state.img_response}</div>', unsafe_allow_html=True)
        
        _, c_aud, c_clear, _ = st.columns([1, 1.5, 1.5, 1])
        with c_aud:
            st.button("Hear Audio Response", type="primary", on_click=generate_audio, args=(st.session_state.img_response, SUPPORTED_LANGUAGES[st.session_state.stored_lang][1]), use_container_width=True)
        with c_clear:
            if st.button("Clear Response", type="secondary", use_container_width=True):
                st.session_state.img_response = None
                st.rerun()
    elif img_to_process is None:
        st.session_state.img_response = None
        res_placeholder.markdown("<p>Awaiting image upload...</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-pad"></div>', unsafe_allow_html=True)

# ==========================================
# 7. PAGE 3: AUDIO INPUT
# ==========================================
def page_audio():
    render_top_nav("Audio Input")

    st.markdown("<h2 style='text-align:center; margin-top:30px;'>Audio Input for Farmer Queries</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Follow the instructions below to record your query. Once submitted, you will receive a response which you can listen to.</p>", unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<div style='background-color:#8CC63F; width:80px; height:80px; border-radius:50%; display:flex; justify-content:center; align-items:center; margin: 0 auto 20px auto;'><i class='fa-solid fa-microphone' style='font-size:35px; color:white;'></i></div>", unsafe_allow_html=True)
    st.markdown("<p>Press the microphone button below to start recording your query.</p>", unsafe_allow_html=True)
    
    audio_value = st.audio_input("Record", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;'>Your Responses</h4>", unsafe_allow_html=True)
    
    res_placeholder = st.empty()
    
    if audio_value is not None and st.button("Process Query", type="primary"):
        with st.spinner("Listening & Fetching..."):
            r = sr.Recognizer()
            lang_name = st.session_state.stored_lang
            stt_code = SUPPORTED_LANGUAGES[lang_name][0]
            
            try:
                with sr.AudioFile(audio_value) as source:
                    audio_data = r.record(source)
                    user_spoken_text = r.recognize_google(audio_data, language=stt_code)
                    
                sys_prompt = f"Answer the agricultural scheme query concisely. Respond in {lang_name}."
                response = client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_spoken_text}], temperature=0.3)
                
                st.session_state.aud_response = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error processing audio: {e}")

    if st.session_state.aud_response:
        res_placeholder.markdown(f"<div style='text-align:left; border:1px solid var(--border-color); padding:15px; border-radius:8px; margin-bottom:20px;'><b>Query processed:</b><br>{st.session_state.aud_response}</div>", unsafe_allow_html=True)
        
        _, c_aud, c_clear, _ = st.columns([1, 1.5, 1.5, 1])
        with c_aud:
            st.button("Hear Audio Response", type="primary", on_click=generate_audio, args=(st.session_state.aud_response, SUPPORTED_LANGUAGES[st.session_state.stored_lang][1]), use_container_width=True)
        with c_clear:
            if st.button("Clear Response", type="secondary", use_container_width=True):
                st.session_state.aud_response = None
                st.rerun()
    elif audio_value is None:
        st.session_state.aud_response = None
        res_placeholder.markdown("<p>Awaiting audio input...</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-pad"></div>', unsafe_allow_html=True)

# ==========================================
# 8. ROUTING ENGINE
# ==========================================
if st.session_state.page == 'Home':
    page_home()
elif st.session_state.page == 'Image Input':
    page_image()
elif st.session_state.page == 'Audio Input':

    page_audio()
