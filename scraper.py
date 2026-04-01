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

def generate_real_ai_analysis(news_context):
    print("🧠 Connecting to Google Gemini LLM for high-density infrastructure mapping...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Using gemini-flash-latest
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    You are a veteran, brutally honest real estate expert and urban planner for Jaipur, Rajasthan.
    
    CONTEXT (Latest News & Infrastructure Updates):
    "{news_context}"
    
    TASK:
    Generate a HIGH-DENSITY data set for the LandIntel map. Focus heavily on Tonk Road, Ajmer Road, Mahindra SEZ, and the Outer Ring Road (including border areas like Chaksu, Phagi, and Bagru).
    
    1. INTEL POINTS (Generate 25+ specific infrastructure markers):
       - Cloverleaf interchanges on the Ring Road (Ajmer Rd / Tonk Rd junctions).
       - New Sector Roads (e.g., 200ft road connecting Tonk Rd and Phagi Rd).
       - Metro Phase 2 stations/corridors (Prahladpura to Sitapura).
       - Mahindra SEZ internal expansions and the new DTA zone.
       - Shivdaspura Satellite Township (JDA land pooling sites).
       - Northern Ring Road survey points (Kalwar Road, Sikar Road junctions).
       - Flagship projects: IPD Tower, B2B Crossing underpass, Elevated roads (MI Road to B2B).
       - Border town developments: Chaksu, Phagi, and Bagru.

    2. LOCALITY INTEL (Generate deep reports for 12+ specific sub-localities):
       - [Jagatpura, Mahindra SEZ, Shivdaspura, Chaksu, Phagi, Bagru, Bhankrota, Vatika, Sikar Road (Daulatpura), Kalwar Road, Sirsi Road, Tonk Road Ext].
    
    3. REALISTIC LISTINGS (Generate 5 trending land listings in these specific growth corridors).

    The output MUST be strictly valid JSON matching this structure:
    {{
        "last_updated": "{datetime.now().strftime('%d %b %Y')}",
        "listings": [
            {{
                "title": "Plot Type & Location",
                "priceTxt": "Realistic Price",
                "price": 85,
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
                "infra_score": "7/10",
                "civilization_score": "5/10",
                "utility_status": "Reality check.",
                "major_projects": ["Project A", "Project B"],
                "brutal_truth": "2-3 sentence assessment."
            }}
        ],
        "infrastructure": [
            {{
                "name": "Specific Project Name",
                "type": "Road / Metro / Township / Utility",
                "status": "Under Construction / Planned / Operational",
                "lat": 26.7550,
                "lng": 75.8200,
                "desc": "Technical detail + market impact insight."
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
    print("🚀 Booting LandIntel High-Density Pipeline...")
    
    # Get combined context
    context_queries = [
        "Jaipur JDA master plan 2047 projects",
        "Jaipur Ring Road cloverleaf Tonk Road Ajmer Road",
        "Jaipur Mahindra SEZ expansion 2025",
        "Jaipur Shivdaspura land pooling scheme",
        "Jaipur elevated road Tonk Road projects"
    ]
    
    full_context = ""
    for q in context_queries:
        full_context += get_live_context(q) + "\n"
    
    # Call the LLM
    try:
        ai_data = generate_real_ai_analysis(full_context)
        
        # Save to file
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(ai_data, f, indent=4)
            
        print("✅ SUCCESS! High-Density Intel written to 'data.json'.")
        
    except Exception as e:
        print("❌ Error generating AI data.", e)

if __name__ == "__main__":
    main()