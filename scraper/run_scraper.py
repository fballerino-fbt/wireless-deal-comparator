import json
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup
from ai_pitch import generate_ai_pitch

def scrape_metro():
    try:
        url = "https://www.metrobyt-mobile.com/cell-phone-plans"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = soup.find_all(string=lambda x: x and '$' in x)
            if prices:
                return {"carrier": "Metro", "deal": prices[0][:100], "price": "Check site", "note": "Live data"}
        return {"carrier": "Metro", "deal": "Unlimited $25/mo", "price": 25, "note": "Sample data"}
    except Exception as e:
        return {"carrier": "Metro", "deal": "See website", "price": "?", "note": f"Error"}

def scrape_cricket():
    try:
        url = "https://www.cricketwireless.com/cell-phone-plans"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = soup.find_all(string=lambda x: x and '$' in x)
            if prices:
                return {"carrier": "Cricket", "deal": prices[0][:100], "price": "Check site", "note": "Live data"}
        return {"carrier": "Cricket", "deal": "Unlimited $30/mo", "price": 30, "note": "Sample data"}
    except Exception as e:
        return {"carrier": "Cricket", "deal": "See website", "price": "?", "note": f"Error"}

def scrape_boost():
    return {"carrier": "Boost", "deal": "Unlimited $25/mo", "price": 25, "note": "Ready for live scraping"}

def scrape_total():
    return {"carrier": "Total", "deal": "Unlimited $35/mo", "price": 35, "note": "Ready for live scraping"}

print("=" * 50)
print("Wireless Deal Comparator - With AI")
print("=" * 50)

# Run scrapers
scrapers = [scrape_metro(), scrape_cricket(), scrape_boost(), scrape_total()]
deals = []

for result in scrapers:
    deals.append(result)
    print(f"✓ {result['carrier']}: {result['deal'][:50]}")

# Generate AI pitch
print("\n🤖 Generating AI sales pitch...")
ai_pitch = generate_ai_pitch(deals)

# Phone promotions
phones = [
    "Metro: Free Samsung Galaxy A14 with port-in",
    "Cricket: iPhone 11 $49.99 with new line",
    "Boost: Free Motorola phone with switch",
    "Total: 50% off select phones"
]

# Save data
output_data = {
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "deals": deals,
    "ai_pitch": ai_pitch,
    "phone_promotions": phones
}

with open("output/deals.json", "w") as f:
    json.dump(output_data, f, indent=2)

# Create HTML with AI pitch
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Wireless Deals - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #764ba2; margin-top: 30px; }}
        .ai-pitch {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            font-size: 1.2em;
            line-height: 1.6;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .deal-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #667eea;
            transition: transform 0.2s;
        }}
        .deal-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .carrier {{ font-size: 1.4em; font-weight: bold; color: #667eea; }}
        .price {{ font-size: 2em; color: #27ae60; font-weight: bold; margin: 10px 0; }}
        .phone-deal {{
            background: #e8f4f8;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .timestamp {{
            text-align: right;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>📱 Wireless Deal Comparator</h1>
    
    <div class="ai-pitch">
        <h2>🤖 AI-Powered Analysis</h2>
        <p>{ai_pitch}</p>
    </div>
    
    <h2>📊 Carrier Deals</h2>
"""

for deal in deals:
    price_display = f"${deal['price']}" if isinstance(deal['price'], (int, float)) else deal['price']
    html_content += f"""
    <div class="deal-card">
        <div class="carrier">{deal['carrier']}</div>
        <div class="price">{price_display}/mo</div>
        <div>{deal['deal']}</div>
        <div style="color:#666; font-size:0.9em;">{deal['note']}</div>
    </div>
"""

html_content += """
    <h2>📱 Phone Promotions</h2>
"""

for phone in phones:
    html_content += f'<div class="phone-deal">📞 {phone}</div>'

html_content += """
    <h2>⚡ Comparison Table</h2>
    <table>
        <tr><th>Carrier</th><th>Monthly Price</th><th>Contract</th><th>Network</th></tr>
        <tr><td>Metro</td><td>$25-40</td><td>No contract</td><td>T-Mobile</td></tr>
        <tr><td>Cricket</td><td>$30-55</td><td>No contract</td><td>AT&T</td></tr>
        <tr><td>Boost</td><td>$25-50</td><td>No contract</td><td>T-Mobile/AT&T</td></tr>
        <tr><td>Total</td><td>$35-60</td><td>No contract</td><td>Verizon</td></tr>
        <tr style="background:#e8f4f8;"><td><strong>VS Postpaid</strong></td><td>$70-90</td><td>2-year contract</td><td>Same towers</td></tr>
    </table>
    
    <div class="timestamp">
        🔄 Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """<br>
        📊 Data refreshed weekly with AI analysis
    </div>
</div>
</body>
</html>
"""

with open("output/report.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ AI pitch generated!")
print(f"📄 Saved to output/report.html")
print(f"🤖 AI Preview: {ai_pitch[:100]}...")