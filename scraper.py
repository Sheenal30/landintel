import urllib.request
import xml.etree.ElementTree as ET
import google.generativeai as genai
import json
import re
import os
import ssl
from datetime import datetime
from dotenv import load_dotenv

# Bypass SSL for local development scraping issues
ssl._create_default_https_context = ssl._create_unverified_context

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 1. RETRIEVE YOUR FREE GEMINI API KEY
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_live_context(query):
    print(f"📡 Scraping context for: {query}...")
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        headlines = []
        for item in root.findall('.//item')[:15]: 
            headlines.append(item.find('title').text)
            
        return "\n".join(headlines)
    except Exception as e:
        print(f"⚠️ Failed to scrape {query}, using fallback.", e)
        return ""

def generate_real_ai_analysis(infra_news, land_news):
    print("🧠 Connecting to Google Gemini LLM for locality-wide intelligence...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Using gemini-flash-latest
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    You are a veteran, brutally honest real estate expert in Jaipur, Rajasthan.
    
    CONTEXT 1: Today's Infrastructure News in Jaipur:
    "{infra_news}"
    
    CONTEXT 2: Recent Land & Plot Sales Headlines in Jaipur:
    "{land_news}"
    
    TASK:
    1. Identify 5 REALISTIC land investment listings currently trending in Jaipur (e.g., Jagatpura, Ajmer Road, Sikar Road, Mahindra SEZ). Use the context above.
    2. PROVIDE DEEP INTEL FOR THE FOLLOWING 8 LOCALITIES IN JAIPUR:
       [Jagatpura, Ajmer Road/SEZ, Sikar Road, Kalwar Road, Sirsi Road, Tonk Road, Vaishali Nagar Extension, Mansarovar Extension]
    
    For each locality, use your internal knowledge of the JDA Master Plan 2025 and recent infrastructure news to provide a "Brutal Reality Report".
    
    The output MUST be strictly valid JSON matching this structure:
    {{
        "last_updated": "{datetime.now().strftime('%d %b %Y')}",
        "listings": [
            {{
                "title": "Plot Type & Location",
                "priceTxt": "Realistic Price",
                "price": 80,
                "lat": 26.8250,
                "lng": 75.8650,
                "desc": "Short summary.",
                "ai_report": {{
                    "recommendation": "Harsh verdict.",
                    "projections": "ROI %",
                    "infra": "Infra impact.",
                    "catalysts": "Future drivers.",
                    "civilization": "Schools/Hospitals/Elite factor.",
                    "utilities": "Water/Electricity/Sewerage truth.",
                    "sources": ["Scrape", "JDA Plan"]
                }}
            }}
        ],
        "localities": [
            {{
                "name": "Locality Name",
                "lat": 26.8250,
                "lng": 75.8650,
                "infra_score": "e.g. 7/10",
                "civilization_score": "e.g. 5/10",
                "utility_status": "Water, Electricity, Sewerage reality.",
                "major_projects": ["Project 1", "Project 2"],
                "brutal_truth": "Brutally honest 2-3 sentence assessment of the area's current habitability vs investment hype."
            }}
        ]
    }}
    """
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    if result.startswith("```json"):
        result = result[7:-3].strip()
    elif result.startswith("```"):
        result = result[3:-3].strip()
    
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        cleaned_result = re.search(r'\{.*\}', result, re.DOTALL)
        if cleaned_result:
            return json.loads(cleaned_result.group())
        raise

def main():
    print("🚀 Booting LandIntel Locality Intelligence Pipeline...")
    
    # 1. Get Context
    infra_news = get_live_context("Jaipur JDA infrastructure projects metro ring road")
    land_news = get_live_context("Jaipur land plots for sale listings price")
    
    # 2. Call the LLM
    try:
        ai_data = generate_real_ai_analysis(infra_news, land_news)
        
        # 3. Save to file
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=4)
            
        print("✅ SUCCESS! Locality-wide Intel written to 'data.json'.")
        
    except Exception as e:
        print("❌ Error generating AI data.", e)

if __name__ == "__main__":
    main()