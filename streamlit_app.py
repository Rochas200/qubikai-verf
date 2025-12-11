import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os

# ==========================================
# 1. APP CONFIGURATIE (Blauw voor Verf) 🔵
# ==========================================
APP_NAME = "VerfBuddy"
APP_ICON = "🖌️"
ACCENT_COLOR = "#0078D7"  # Helder Blauw
BACKGROUND_COLOR = "#0E1117"

# ==========================================
# 2. SETUP & STYLING 🎨
# ==========================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="centered", # Centered leest vaak fijner op mobiel dan Wide
    initial_sidebar_state="collapsed"
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
        color: #FAFAFA;
        background-color: {BACKGROUND_COLOR};
    }}
    
    /* Navigatie verbergen */
    [data-testid="stSidebarNav"] {{display: none;}}
    
    /* HEADER BALK */
    .nav-bar {{
        padding: 15px;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        margin-bottom: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3em;
        border-left: 6px solid {ACCENT_COLOR};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}

    /* Custom Knoppen */
    div.stButton > button {{
        background-color: {ACCENT_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        width: 100%;
        text-transform: uppercase;
    }}
    div.stButton > button:hover {{
        background-color: #005a9e;
        transform: translateY(-2px);
    }}
    
    /* Resultaat Kaarten (Container Class) */
    .result-card {{
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {ACCENT_COLOR};
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. STATE & API 🧠
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""

# API FIX: Gebruik ALTIJD st.secrets voor veiligheid
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ CRITICAAL: Geen API Key gevonden in Secrets!")
    st.stop()

# ==========================================
# 4. HULPFUNCTIES
# ==========================================
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def def analyze_image(base64_image):
    # HIER ZIT DE NIEUWE INTELLIGENTIE 🧠
    prompt = """
    Jij bent de Meesterschilder van Qubikai met 25 jaar ervaring.
    Je analyseert foto's van kamers/muren om de gebruiker perfect advies te geven.
    
    DOE EERST DIT (INTERN):
    1. Analyseer de ONDERGROND: Is het glad stucwerk? Baksteen? Hout? Behang? (Dit beïnvloedt de verfopname).
    2. Schat de AFMETINGEN: Kijk naar referentiepunten (deuren zijn vaak 2m hoog, stopcontacten 30cm laag).
    3. Bereken de OPPERVLAKTE (Hoogte x Breedte minus ramen/deuren).
    4. Bepaal de VERF SPUITBAARHEID: Ruwe muren zuigen meer verf op (+10-20% extra nodig).
    
    GEEF JE ANTWOORD IN DIT EXACTE MARKDOWN FORMAT:
    
    # [Pakkende Titel, bijv: "Project Woonkamer: Baksteen Muur"]
    
    ### 🕵️‍♂️ Analyse van de muur
    * **Ondergrond:** [Wat zie je? Glad/Ruw/Behang?]
    * **Conditie:** [Ziet het er schoon uit of is voorbehandeling nodig?]
    
    ### 📏 De Berekening
    * **Geschatte afmetingen:** [Hoogte]m x [Breedte]m
    * **Netto Oppervlak:** **[Aantal] m²**
    * **Benodigde Verf:** **[Aantal] Liter** *(Gebaseerd op [Type ondergrond])*
    * **Kostenindicatie:** € [Bedrag] *(uitgaande van kwaliteitsverf à €15/L)*
    
    ### 🛒 Boodschappenlijst
    * **Verf:** [Type verf advies: Latex/Muurverf/Lak]
    * **Roller:** [Advies: Kortharig voor glad, Langharig voor ruw]
    * **Voorstrijk:** [JA/NEE - Waarom?]
    * **Tape:** [Type tape advies]
    
    ### 💡 Meesterschilder Tip
    [Eén gouden tip specifiek voor DEZE situatie op de foto.]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"
    
    Geef antwoord in Markdown:
    # [Korte titel, bijv: "Schatting: 24 m²"]
    
    ### 📏 Metingen & Liters
    * **Geschat Oppervlak:** [Aantal] m²
    * **Verf nodig:** [Aantal] liter (Reken: 1L per 8m²)
    * **Kostenindicatie:** € [Bedrag] (Reken: €15/L)
    
    ### 🛠️ Benodigdheden
    * [Advies over rollers/kwasten]
    * [Advies over afplakken]
    
    ### 💡 Schilder Tip
    [Eén gouden tip over de ondergrond die je ziet]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"

# ==========================================
# 5. PAGINA'S 📱
# ==========================================

# --- HEADER (Altijd zichtbaar) ---
c1, c2 = st.columns([1, 5])
with c1:
    if st.button("🏠", help="Terug naar Home"):
        st.session_state.page = 'home'
        st.rerun()
with c2:
    st.markdown(f"<div class='nav-bar'>{APP_NAME}</div>", unsafe_allow_html=True)


# --- HOME ---
if st.session_state.page == 'home':
    # Check voor logo (optioneel)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
        
    st.markdown("<h2 style='text-align: center;'>Hoeveel verf heb ik nodig? 🤔</h2>", unsafe_allow_html=True)
    st.write("<div style='text-align: center; color: #ccc; margin-bottom: 20px;'>Van foto naar boodschappenlijst in 1 klik.</div>", unsafe_allow_html=True)

    with st.expander("ℹ️ Hoe werkt VerfBuddy?", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 1. Foto")
            st.caption("Maak een foto van je muur.")
        with c2:
            st.markdown("#### 2. Bereken")
            st.caption("Ik reken de liters uit.")
        with c3:
            st.markdown("#### 3. Start")
            st.caption("Jij kunt direct aan de slag.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    c_left, c_btn, c_right = st.columns([1, 2, 1])
    with c_btn:
        if st.button("🚀 START PROJECT", type="primary"):
            st.session_state.page = 'upload'
            st.rerun()

# --- UPLOAD ---
elif st.session_state.page == 'upload':
    st.markdown("### 📸 Stap 1: Upload je muur")
    
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        st.session_state.page = 'processing'
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Terug"):
        st.session_state.page = 'home'
        st.rerun()

# --- PROCESSING ---
elif st.session_state.page == 'processing':
    with st.spinner('📐 Muren opmeten...'):
        image = Image.open(st.session_state.current_image)
        base64_img = encode_image(image)
        result = analyze_image(base64_img)
        st.session_state.analysis_result = result
        st.session_state.page = 'result'
        st.rerun()

# --- RESULTAAT ---
elif st.session_state.page == 'result':
    c_img, c_txt = st.columns([1, 2])
    
    with c_img:
        img = Image.open(st.session_state.current_image)
        st.image(img, use_container_width=True, caption="Jouw muur")
    
    with c_txt:
        # MARKDOWN FIX: Eerst div openen, dan markdown printen, dan sluiten
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.analysis_result)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.write("### Wat nu?")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.link_button("🛒 Bestel Verf (Google)", "https://www.google.com/search?q=verf+kopen")
    with col_b:
        if st.button("🔄 Volgende Muur"):
            st.session_state.page = 'upload'
            st.rerun()