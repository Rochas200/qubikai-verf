import streamlit as st
import base64
from openai import OpenAI

# 1. Configuratie
st.set_page_config(page_title="Qubikai - VerfBuddy", page_icon="🎨")

# --- STYLING (Qubikai Klus Thema: Blauw/Groen) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Grote Knoppen (Blauw) */
    div.stButton > button {
        width: 100%;
        background-color: #0078D7;
        color: white;
        font-size: 20px;
        font-weight: 700;
        padding: 15px 0px;
        border-radius: 12px;
        border: none;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #005a9e;
        transform: translateY(-2px);
        color: white;
    }
    /* Input velden strakker */
    [data-testid="stNumberInput"] {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    h1 {text-align: center;}
</style>
""", unsafe_allow_html=True)

# 2. Titel
st.title("🎨 VerfBuddy")
st.write("Foto van de muur + de maten = Direct weten wat je moet kopen.")

# 3. API Setup
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("⚠️ Oeps! API Key mist nog in de Secrets.")
    st.stop()

# 4. De Inputs (Foto + Maten)
col1, col2 = st.columns(2)
with col1:
    hoogte = st.number_input("Hoogte (meters)", value=2.6, step=0.1)
with col2:
    breedte = st.number_input("Breedte (meters)", value=4.0, step=0.5)

uploaded_file = st.file_uploader("Maak een foto van de muur (voor advies over ondergrond)", type=['png', 'jpg', 'jpeg'])

# 5. De Magie
def analyze_wall(image_bytes, h, b):
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    oppervlakte = h * b
    
    prompt = f"""
    Jij bent VerfBuddy, de expert schilder van Qubikai.
    De gebruiker heeft een muur van {h}m hoog en {b}m breed (Totaal: {oppervlakte:.1f} m2).
    
    Kijk naar de foto van de muur en geef advies:
    1. ONDERGROND: Wat zie je? (Glad stucwerk, baksteen, oud behang, zuigende muur?)
    2. LITERS NODIG: Reken met 8m2 per liter (voor zekerheid). Reken uit: {oppervlakte} / 8. Rond af naar boven op hele liters.
    3. ADVIES: Heb ik voorstrijk nodig? Welke roller (kortharig/langharig)? 
    
    Hou het kort, krachtig en als een lijstje.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "Je bent een behulpzame klus-expert. Geef antwoord in Markdown met dikgedrukte koppen."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ],
            }
        ],
        max_tokens=400
    )
    return response.choices[0].message.content

# 6. De Actie Knop
if uploaded_file is not None:
    st.image(uploaded_file, caption='Jouw muur', use_column_width=True)
    
    if st.button('🧮 Bereken mijn Verf'):
        with st.spinner('Muur inspecteren en rekenen...'):
            try:
                bytes_data = uploaded_file.getvalue()
                resultaat = analyze_wall(bytes_data, hoogte, breedte)
                
                st.success("Berekening Compleet!")
                st.markdown("### 📋 Jouw Boodschappenlijstje")
                st.markdown(resultaat)
                
            except Exception as e:
                st.error(f"Foutje: {e}")