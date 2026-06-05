import json
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup
from ai_pitch import generate_ai_pitch, generate_competitive_pitch

def scrape_metro():
    try:
        url = "https://www.metrobyt-mobile.com/cell-phone-plans"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Clean: remove script tags before searching
            for script in soup(["script", "style"]):
                script.decompose()
            price_text = soup.get_text()
            # Extract first $ amount
            import re
            prices = re.findall(r'\$(\d+(?:\.\d{2})?)', price_text)
            if prices:
                return {"carrier": "Metro", "price": f"${prices[0]}", "deal": "Unlimited plan", "note": "Live data", "phone_deals": ["Free Samsung A14 with port-in"]}
        return {"carrier": "Metro", "price": "$25", "deal": "Unlimited $25/mo", "note": "Sample data", "phone_deals": ["Free Samsung with switch"]}
    except Exception as e:
        return {"carrier": "Metro", "price": "$25", "deal": "See website", "note": "Error loading", "phone_deals": []}

def scrape_cricket():
    try:
        url = "https://www.cricketwireless.com/cell-phone-plans"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove JavaScript
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            import re
            prices = re.findall(r'\$(\d+(?:\.\d{2})?)', text)
            if prices:
                return {"carrier": "Cricket", "price": f"${prices[0]}", "deal": "Unlimited plan", "note": "Live data", "phone_deals": ["iPhone 11 $49.99 with new line"]}
        return {"carrier": "Cricket", "price": "$30", "deal": "Unlimited $30/mo", "note": "Sample data", "phone_deals": ["iPhone deals available"]}
    except Exception as e:
        return {"carrier": "Cricket", "price": "$30", "deal": "See website", "note": "Error loading", "phone_deals": []}

def scrape_boost():
    return {"carrier": "Boost", "price": "$25", "deal": "Unlimited $25/mo", "note": "Ready for live scraping", "phone_deals": ["Free Motorola phone with switch"]}

def scrape_total():
    return {"carrier": "Total", "price": "$35", "deal": "Unlimited $35/mo", "note": "Ready for live scraping", "phone_deals": ["50% off select phones"]}

print("=" * 60)
print("Wireless Deal Comparator - Enhanced Business Edition")
print("=" * 60)

# Run scrapers
scrapers = [scrape_metro(), scrape_cricket(), scrape_boost(), scrape_total()]
deals = []

for result in scrapers:
    deals.append(result)
    print(f"✓ {result['carrier']}: {result['price']}/mo - {result['deal'][:30]}")

# Generate AI analysis
print("\n🤖 Generating AI analysis...")
best_deal_analysis = generate_ai_pitch(deals)  # Now returns best deal analysis

# Generate competitive pitches for each carrier
for i, deal in enumerate(deals):
    print(f"   Crafting pitch for {deal['carrier']}...")
    deals[i]['competitive_pitch'] = generate_competitive_pitch(deal, deals)

# Phone promotions (expandable)
all_phone_deals = []
for deal in deals:
    all_phone_deals.extend(deal.get('phone_deals', []))

# Save data
output_data = {
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "deals": deals,
    "best_deal_analysis": best_deal_analysis,
    "all_phone_promotions": all_phone_deals
}

with open("output/deals.json", "w") as f:
    json.dump(output_data, f, indent=2)

# Generate HTML report with new layout
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Wireless Deal Comparator - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f0f2f5;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 30px; border-left: 4px solid #1a73e8; padding-left: 15px; }}
        .best-deal {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            font-size: 1.1em;
            line-height: 1.6;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .comparison-table th, .comparison-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .comparison-table th {{
            background: #1a73e8;
            color: white;
            font-weight: bold;
        }}
        .comparison-table tr:hover {{
            background: #f5f5f5;
        }}
        .price {{
            font-size: 1.4em;
            font-weight: bold;
            color: #2e7d32;
        }}
        .deal-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #1a73e8;
        }}
        .carrier-name {{
            font-size: 1.6em;
            font-weight: bold;
            color: #1a73e8;
            margin-bottom: 10px;
        }}
        .pitch-bullets {{
            background: #e8f4f8;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .pitch-bullets ul {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .pitch-bullets li {{
            margin: 8px 0;
            line-height: 1.4;
        }}
        .phone-deal {{
            background: #fff3e0;
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 3px solid #ff9800;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .kpi-card {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .kpi-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #1a73e8;
        }}
        .timestamp {{
            text-align: right;
            color: #666;
            font-size: 0.85em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>📱 Wireless Deal Comparator</h1>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <!-- 1. AI-POWERED ANALYSIS - Best deal in 3 lines -->
    <div class="best-deal">
        <h2>🏆 AI-Powered Best Deal Analysis</h2>
        <p>{best_deal_analysis}</p>
    </div>
    
    <!-- 2. COMPARISON TABLE -->
    <h2>📊 Carrier Comparison Table</h2>
    <table class="comparison-table">
        <tr>
            <th>Carrier</th>
            <th>Monthly Price</th>
            <th>Plan</th>
            <th>Contract</th>
            <th>Network</th>
        </tr>
"""
for deal in deals:
    html_content += f"""
        <tr>
            <td><strong>{deal['carrier']}</strong></td>
            <td class="price">{deal['price']}/mo</td>
            <td>{deal['deal']}</td>
            <td>No contract</td>
            <td>{'T-Mobile' if deal['carrier'] == 'Metro' else 'AT&T' if deal['carrier'] == 'Cricket' else 'T-Mobile/AT&T' if deal['carrier'] == 'Boost' else 'Verizon'}</td>
        </tr>
"""
html_content += f"""
        <tr style="background: #ffebee;">
            <td><strong>VS Postpaid</strong></td>
            <td class="price">$70-90/mo</td>
            <td>Similar unlimited</td>
            <td>2-year contract</td>
            <td>Same towers</td>
        </tr>
    </table>
    <p><small>💡 VS Postpaid shows traditional carrier plans (Verizon/AT&T/T-Mobile direct) - You save 30-50% with prepaid!</small></p>
    
    <!-- 3. PHONE PROMOTIONS -->
    <h2>📱 Phone Promotions</h2>
"""
for phone in all_phone_deals:
    html_content += f'<div class="phone-deal">📞 {phone}</div>'

html_content += """
    <!-- 4. CARRIER DEALS WITH SALES PITCHES -->
    <h2>💼 Carrier Deep Dive & Sales Pitches</h2>
"""

for deal in deals:
    html_content += f"""
    <div class="deal-card">
        <div class="carrier-name">{deal['carrier']}</div>
        <div class="price">{deal['price']}/mo</div>
        <p><strong>Plan:</strong> {deal['deal']}</p>
        <div class="pitch-bullets">
            <strong>🎯 Sales Pitch to Win Business:</strong>
            <ul>
                {''.join([f'<li>{bullet}</li>' for bullet in deal.get('competitive_pitch', ['Competitive pricing', 'No contracts', 'Great network quality'])])}
            </ul>
        </div>
        <div style="font-size:0.9em; color:#666;">{deal['note']}</div>
    </div>
"""

# Additional KPIs
html_content += """
    <h2>📈 Key Performance Indicators</h2>
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">4</div>
            <div>Carriers Compared</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">30-50%</div>
            <div>Savings vs Postpaid</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">$0</div>
            <div>Contract Fees</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">Weekly</div>
            <div>Updates</div>
        </div>
    </div>
    
    <div class="timestamp">
        🔄 Data refreshes automatically every Monday<br>
        🤖 AI analysis powered by Groq<br>
        📊 Compare & save on wireless today
    </div>
</div>
</body>
</html>
"""

with open("output/report.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ Enhanced report generated!")
print(f"📄 Saved to output/report.html")
print(f"📊 Includes: Best deal AI, comparison table, phone deals, and carrier-specific sales pitches")
