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
    print("🧠 Connecting to Google Gemini LLM for expert market synthesis...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Using gemini-2.0-flash or gemini-flash-latest
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    You are a veteran, brutally honest real estate expert in Jaipur, Rajasthan.
    
    CONTEXT 1: Today's Infrastructure News in Jaipur:
    "{infra_news}"
    
    CONTEXT 2: Recent Land & Plot Sales Headlines in Jaipur:
    "{land_news}"
    
    TASK:
    1. Identify 5 REALISTIC land investment listings currently trending in Jaipur (e.g., Jagatpura, Ajmer Road, Sikar Road, Mahindra SEZ). Use the context above to make them highly specific.
    2. For each listing, provide a "Brutal Reality Report". Do NOT sugarcoat. Mention water issues (Bisalpur status), JDA approval risks, and traffic/sewerage realities.
    3. Update the 2 major infrastructure markers (Jaipur Ring Road and Shivdaspura Aero City) with DEEP AI insights about their current impact on "Civilization" (schools, hospitals, habitability).

    The output MUST be strictly valid JSON matching this structure:
    {{
        "last_updated": "{datetime.now().strftime('%d %b %Y')}",
        "listings": [
            {{
                "title": "Specific Plot Type & Location (e.g. 200 sq.yd JDA Plot, Jagatpura Extension)",
                "priceTxt": "Realistic Price (e.g. ₹85 Lakh)",
                "price": 85,
                "lat": 26.8250,
                "lng": 75.8650,
                "desc": "Short 1 sentence summary of the deal.",
                "ai_report": {{
                    "recommendation": "Harsh verdict: Buy/Hold/Avoid.",
                    "projections": "5-Year: X% | 10-Year: Y%",
                    "infra": "Specific infra impact (e.g. 500m from upcoming elevated road).",
                    "catalysts": "What will drive price (e.g. New hospital nearby).",
                    "civilization": "Truth about nearby schools, hospitals, and elite factor.",
                    "utilities": "Status of water (Bisalpur), electricity, and sewerage.",
                    "sources": ["Google News Real-time Scrape", "JDA Master Plan 2025"]
                }}
            }}
        ],
        "infrastructure": [
            {{
                "name": "Jaipur Ring Road",
                "status": "Operational / Under Extension",
                "lat": 26.7550,
                "lng": 75.8200,
                "civilization_score": "e.g. 4/10",
                "utility_status": "e.g. Industrial power ready, but domestic water lagging.",
                "desc": "Deep AI Insight: How this road is actually changing local life and which sectors are still 'ghost towns'."
            }},
            {{
                "name": "Shivdaspura Aero City / Junction",
                "status": "Delayed / Planning Stage",
                "lat": 26.7200,
                "lng": 75.8200,
                "civilization_score": "e.g. 2/10",
                "utility_status": "e.g. Zero sewerage, tankers only.",
                "desc": "Deep AI Insight: The brutal truth about the 'Aero City' hype vs the ground reality of land acquisition."
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
    print("🚀 Booting LandIntel Expert AI Pipeline...")
    
    # 1. Get Context
    infra_news = get_live_context("Jaipur JDA infrastructure projects metro ring road")
    land_news = get_live_context("Jaipur land plots for sale listings price")
    
    # 2. Call the LLM
    try:
        ai_data = generate_real_ai_analysis(infra_news, land_news)
        
        # 3. Save to file
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=4)
            
        print("✅ SUCCESS! Real AI Expert data written to 'data.json'.")
        
    except Exception as e:
        print("❌ Error generating AI data.", e)

if __name__ == "__main__":
    main()