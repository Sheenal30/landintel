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

def get_live_jaipur_news():
    print("📡 Scraping live infrastructure news for Jaipur...")
    url = "https://news.google.com/rss/search?q=Jaipur+infrastructure+OR+real+estate+OR+metro+OR+JDA&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        headlines = []
        for item in root.findall('.//item')[:10]: # Get top 10 latest news
            headlines.append(item.find('title').text)
            
        print(f"✅ Scraped {len(headlines)} live news headlines.")
        return "\n".join(headlines)
    except Exception as e:
        print("⚠️ Failed to scrape news, using fallback local context.", e)
        return "Jaipur real estate market: Metro Phase 2 developments, Ring Road expansion, and new JDA housing schemes in Jagatpura."

def generate_real_ai_analysis(live_news):
    print("🧠 Connecting to Google Gemini LLM for brutal market analysis...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Using gemini-flash-latest
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    You are a veteran, brutally honest real estate investor in Jaipur.
    I am providing you with today's live news headlines regarding Jaipur infrastructure:
    "{live_news}"
    
    Based on your deep knowledge of Jaipur and these news headlines, generate a JSON object containing 5 highly realistic, specific land investment zones in Jaipur (e.g., Jagatpura, Shivdaspura, VKI, Ajmer Road, Sikar Road).
    
    DO NOT be overly positive. Identify severe risks (e.g., water shortage, JDA legal issues, delayed airport, heavy traffic).
    
    The output MUST be strictly valid JSON matching this exact structure, with NO markdown formatting, NO backticks, and NO extra text outside the JSON:
    {{
        "last_updated": "{datetime.now().strftime('%d %b %Y')}",
        "listings": [
            {{
                "title": "Zone Name / Plot Type (e.g., 200 sq.yd Plot, Jagatpura)",
                "priceTxt": "Realistic Price (e.g. ₹80 Lakh)",
                "price": 80,
                "lat": 26.8250,
                "lng": 75.8650,
                "desc": "Short 1 sentence description",
                "ai_report": {{
                    "recommendation": "A harsh, expert verdict on whether to buy, hold, or run away.",
                    "projections": "5-Year: 15% | 10-Year: 40%",
                    "infra": "Brutal truth about nearby infrastructure (e.g., Metro Phase 2 delayed).",
                    "catalysts": "Specific future events that might drive prices.",
                    "civilization": "Brutal truth about schools, hospitals, and neighborhood quality.",
                    "utilities": "Status of water (Bisalpur), sewerage, and electricity.",
                    "sources": ["Google News Real-time Scrape", "JDA Master Plan Knowledge"]
                }}
            }}
        ]
    }}
    """
    
    response = model.generate_content(prompt)
    
    # Clean the LLM output to ensure it's valid JSON
    result = response.text.strip()
    if result.startswith("```json"):
        result = result[7:-3].strip()
    elif result.startswith("```"):
        result = result[3:-3].strip()
    
    # Final check for JSON validity
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        # Fallback if LLM fails to provide valid JSON
        cleaned_result = re.search(r'\{.*\}', result, re.DOTALL)
        if cleaned_result:
            return json.loads(cleaned_result.group())
        raise

def main():
    print("🚀 Booting LandIntel Real AI Pipeline...")
    
    # 1. Scrape the web
    live_news = get_live_jaipur_news()
    
    # 2. Call the LLM
    try:
        ai_data = generate_real_ai_analysis(live_news)
        
        # We will add a few hardcoded infrastructure markers just so the map has context points,
        # but the actual listings and analysis are 100% AI generated.
        ai_data["infrastructure"] = [
            {"name": "Jaipur Ring Road", "status": "Operational", "lat": 26.7550, "lng": 75.8200, "desc": "Southern corridor active."},
            {"name": "Shivdaspura Aero City", "status": "Delayed", "lat": 26.7200, "lng": 75.8200, "desc": "Greenfield airport site."}
        ]
        
        # 3. Save to file
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=4)
            
        print("✅ SUCCESS! Real AI data written to 'data.json'.")
        
    except Exception as e:
        print("❌ Error generating AI data. Check API key and network.", e)

if __name__ == "__main__":
    main()