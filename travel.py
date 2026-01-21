import streamlit as st
import google.generativeai as genai
import os
import base64
import json
import re
from dotenv import load_dotenv
from fpdf import FPDF
import folium
from streamlit_folium import st_folium

# Api setup
load_dotenv()
GOOGLE_API_KEY = "Api key"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Explore India", layout="wide",)

#css
def load_css():
    st.markdown("""
    <style>
    /* Global Text Styles */
    .stApp, .stMarkdown, p, h1, h2, h3, span, label, div {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Input Fields Styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        border: 1px solid #ff9933; /* Saffron border */
    }
    
    /* Navigation Cards */
    .nav-card {
        background: linear-gradient(135deg, rgba(255,153,51,0.2), rgba(19,136,8,0.2));
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        transition: transform 0.3s ease;
        margin-bottom: 20px;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(5px);
    }
    .nav-card:hover {
        transform: scale(1.03);
        border-color: #ff9933;
        background-color: rgba(0, 0, 0, 0.8);
    }
    
    /* Section Main Box */
    .main-box {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 30px;
        border-radius: 15px;
        border-left: 5px solid #ff9933;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #ff9933;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    if os.path.exists(png_file):
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
        }
        </style>
        """, unsafe_allow_html=True)

def generate_pdf(text, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    text = text.replace("₹", "Rs. ").replace("*", "")
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Logics
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_home(): st.session_state.page = 'home'
def go_s1(): st.session_state.page = 'section1'
def go_s2(): st.session_state.page = 'section2'
def go_s3(): st.session_state.page = 'section3'

#Section 1
def render_section_1():
    st.button("⬅️ Back to Home", on_click=go_home)
    st.markdown('<div class="main-box"><h1>Lets Explore Next Destination</h1><p>Confused where to go for the college trip? Let\'s find a spot!</p></div>', unsafe_allow_html=True)

    with st.form("discovery_form"):
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox("Region Preferred", ["Anywhere in India","North Cold/snowy", "North India", "South India", "North East India", "Rajasthan/Desert", "Goa/Beaches"])
            vibe = st.selectbox("Trip Vibe", ["Chill/Relaxing", "Trekking/Adventure", "Party/Nightlife", "Heritage/Culture", "Spiritual/Peace"])
            season = st.selectbox("Travel Season", ["Summer Break (May-July)", "Winter Break (Dec-Jan)", "Monsoon", "Long Weekend"])
        
        with col2:
            budget_range = st.number_input("Min Budget per Person (₹)", value=1000, max_value=50000, step=500)
            crowd = st.selectbox("Crowd Preference", ["Popular Student Hubs", "Hidden Gems (Less Crowded)", "Balanced"])
            transport_pref = st.multiselect("Preferred Travel Mode", ["Train (general/Sleeper/3AC)", "Volvo Bus", "Flight", "Road Trip/Bike"])

        submitted = st.form_submit_button(" Let's Find Places")

    if submitted:
        with st.spinner("Asking seniors... just kidding, asking AI..."):
            prompt = f"""
            Act as an expert Indian student travel guide. Suggest 5 best travel destinations in India based on:
            - Region: {region}
            - Vibe: {vibe}
            - Season: {season}
            - Budget: {budget_range}
            - Transport: {', '.join(transport_pref)}

            For EACH suggestion provide:
            1. **Place Name:**
            2. **Why for Students:** (e.g. cheap cafes, trekking spots, student crowd).
            3. **Estimated Cost Breakdown (INR):** Travel, Stay (Hostels/Dorms), Food.
            4. **Safety Score:** (Safe for solo/female travelers?).
            5. **One 'Jugaad' Tip:** How to save money there.
            """
            result = get_gemini_response(prompt)
            st.session_state['result_s1'] = result
            
    if 'result_s1' in st.session_state:
        st.markdown(f'<div class="main-box">{st.session_state["result_s1"]}</div>', unsafe_allow_html=True)
        st.download_button("Download Plan", st.session_state['result_s1'], "student_trips.txt")

#Section 2
def render_section_2():
    st.button("⬅️ Back to Home", on_click=go_home)
    st.markdown('<div class="main-box"><h1>Lets Find Travel Agencies</h1><p>Looking for a pre-planned package? Ideal for your big groups as well as small groups.</p></div>', unsafe_allow_html=True)

    with st.form("agency_form"):
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("Destination", placeholder="e.g. Manali, Goa, Banaras")
            people = st.number_input("Group Size", 1, 60, 4)
            duration = st.number_input("Days", 1, 15, 4)
        with col2:
            budget_limit = st.number_input("Max Budget per Person (₹)", min_value=1000, value=2000, step=500)
            inclusions = st.multiselect("Must Haves", ["AC/sleeper Bus", "Bonfire/Music", "Trekking Guide", "Meals Included", "Jungle Camp Stay"])
        
        submitted = st.form_submit_button("Let's Find Travel Agencies")

    if submitted and dest:
        with st.spinner("Finding budget-friendly operators..."):
            prompt = f"""
            You are a travel broker for Indian students. Find suitable tour operators/packages for:
            - Destination: {dest}
            - Group Size: {people}
            - Budget Limit: ₹{budget_limit}/person
            - Requirements: {', '.join(inclusions)}

            Provide a report:
            1. **Suggested Agencies/Operators:** (Mention popular youth-centric travel communities in India).
            2. **Expected Package Cost:** Realistically what can they get for ₹{budget_limit}?
            3. **Itinerary Snapshot:** What a typical package covers.
            4. **Negotiation Tip:** How to bargain for a student group discount in India.
            """
            result = get_gemini_response(prompt)
            st.session_state['result_s2'] = result

    if 'result_s2' in st.session_state:
        st.markdown(f'<div class="main-box">{st.session_state["result_s2"]}</div>', unsafe_allow_html=True)
        st.download_button("Download Details", st.session_state['result_s2'], "package_info.txt")

# Section 3
def render_section_3():
    st.button("⬅️ Back to Home", on_click=go_home)
    st.markdown('<div class="main-box"><h1>Lets Plan Travel Itinerary</h1><p>Plan the OG Trip with AI!</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Destination", placeholder="e.g. Manali, Goa, Banaras")
        days = st.number_input("Number of Days", 1, 30, 3)
        total_budget = st.number_input("Total Trip Budget (₹)", min_value=1000, value=10000, step=500)
    with col2:
        travelers = st.number_input("Travelers", 1, 20, 1)
        group_type = st.selectbox("Group Type", ["Solo (Backpacker)", "College Friends", "Couple", "All Girls Trip"])
        food_pref = st.selectbox("Food Preference", ["Street Food & Local Dhabas (Cheap)", "Cafes & Restaurants", "Mix of Both"])

    interests = st.multiselect("Interests", ["Photography", "Cafes", "Trekking", "Historical Spots", "Shopping (Cheap markets)", "Beaches"])
    
    if st.button("Generate Itinerary & Map"):
        if not destination:
            st.error("Please enter a destination first!")
        else:
            with st.spinner("Drafting your plan..."):
                prompt = f"""
                Create a detailed {days}-day student itinerary for {destination}, India.
                - Travelers: {travelers} ({group_type})
                - Total Budget: ₹{total_budget}
                - Food: {food_pref}
                - Interests: {', '.join(interests)}

                TRAVEL ITINERARY
                1. **Travel Guide:** Best train/bus to take.
                2. **Accommodation:** Cheap Hostels/Dorms.
                3. **Day-by-Day Plan:** Detailed timing, free spots.
                4. **Food:** Local street food.
                5. **Budget Breakdown:** Costs for Travel, Stay, Food.
                6. **Safety & Packing:** Student essentials.

                TRAVEL SPOT MAP
                At the very end of your response, strictly output a JSON object identified by "###JSON_START###" and "###JSON_END###". 
                The JSON must contain a list of coordinates for the MAIN locations mentioned in the itinerary. 
                Structure: 
                {{
                    "locations": [
                        {{"name": "Location Name", "lat": latitude_float, "lon": longitude_float, "day": "Day 1"}},
                        ...
                    ]
                }}
                """
                
                full_response = get_gemini_response(prompt)
                
                try:
                    text_part = full_response.split("###JSON_START###")[0]
                    st.session_state['result_s3_text'] = text_part
                    
                    json_match = re.search(r'###JSON_START###(.*?)###JSON_END###', full_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        json_str = json_str.replace('```json', '').replace('```', '')
                        st.session_state['result_s3_json'] = json.loads(json_str)
                    else:
                        st.session_state['result_s3_json'] = None
                        
                except Exception as e:
                    st.session_state['result_s3_text'] = full_response
                    st.session_state['result_s3_json'] = None
                    print(f"Map generation error: {e}")

    if 'result_s3_text' in st.session_state:
        
        st.markdown(f'<div class="main-box">{st.session_state["result_s3_text"]}</div>', unsafe_allow_html=True)
        
        if st.session_state.get('result_s3_json'):
            st.markdown("### Trip Map")
            locations = st.session_state['result_s3_json'].get('locations', [])
            
            if locations:
                avg_lat = sum([l['lat'] for l in locations]) / len(locations)
                avg_lon = sum([l['lon'] for l in locations]) / len(locations)
                
                m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
                
                coordinates = []
                for loc in locations:
                    folium.Marker(
                        [loc['lat'], loc['lon']], 
                        popup=f"{loc['name']} ({loc['day']})",
                        tooltip=loc['name'],
                        icon=folium.Icon(color='orange', icon='info-sign')
                    ).add_to(m)
                    coordinates.append([loc['lat'], loc['lon']])
                
                if len(coordinates) > 1:
                    folium.PolyLine(coordinates, color="blue", weight=2.5, opacity=0.8).add_to(m)

                st_data = st_folium(m, width=1400, height=500)

        st.markdown("---")
        col_d1, col_d2 = st.columns(2)
        col_d1.download_button("📥 Download Text Plan", st.session_state['result_s3_text'], f"itinerary.txt")
        col_d2.download_button("📄 Download PDF Plan", generate_pdf(st.session_state['result_s3_text'], "Student Itinerary"), f"itinerary.pdf")

#Home
def render_home():
    st.markdown("<h1 style='text-align: center; color: #ff9933; margin-bottom: 10px;'>Explore India</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 50px;'> AI Travel Companion for Indian Students & Backpackers</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h3>Explore Next Destinations</h3>
            <p>Don't know where to go? Find budget-friendly spots based on your vibe.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Let's Explore", on_click=go_s1, use_container_width=True)

    with col2:
        st.markdown("""
        <div class="nav-card">
            <h3>Find Travel Agencies</h3>
            <p>Planning a mass bunk? Find tour operators and group package estimates.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Let's Find ", on_click=go_s2, use_container_width=True)

    with col3:
        st.markdown("""
        <div class="nav-card">
            <h3>Travel Plan</h3>
            <p>Plan it yourself! Get day-wise plans, train info, hostel hacks, and street food guides.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Let's Plan Our Trip", on_click=go_s3, use_container_width=True)

load_css()
if os.path.exists("background.jpg"):
    set_background("background.jpg")
else:
    set_background("default")

if st.session_state.page == 'home': render_home()
elif st.session_state.page == 'section1': render_section_1()
elif st.session_state.page == 'section2': render_section_2()
elif st.session_state.page == 'section3': render_section_3()