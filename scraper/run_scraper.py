import json
import os
import re
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright
from ai_pitch import generate_ai_pitch, generate_competitive_pitch

# ==================== CREATE OUTPUT FOLDER ====================
os.makedirs("output", exist_ok=True)
os.makedirs("archives", exist_ok=True)

# ==================== ARCHIVE SYSTEM ====================
def archive_previous_data():
    if os.path.exists("output/deals.json"):
        archive_dir = f"archives/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(archive_dir, exist_ok=True)
        shutil.copy("output/deals.json", f"{archive_dir}/deals.json")
        print(f"📦 Archived to {archive_dir}")
        shutil.copy("output/deals.json", "output/latest_good.json")

def load_cached_deals(carrier_name):
    if os.path.exists("output/latest_good.json"):
        with open("output/latest_good.json", "r") as f:
            cached = json.load(f)
            for deal in cached.get("deals", []):
                if deal["carrier"] == carrier_name:
                    print(f"   → Using cached data for {carrier_name}")
                    return deal
    return None

# ==================== SCRAPERS ====================
def scrape_with_playwright(url, carrier_name):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"   Loading {carrier_name}...")
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()
            
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', html)
            price = f"${price_match.group(1)}" if price_match else "Check site"
            
            phone_deals = []
            if "free" in html.lower() and "phone" in html.lower():
                phone_deals.append(f"Free phone promotion at {carrier_name}")
            
            return {
                "carrier": carrier_name,
                "price": price,
                "deal": "Unlimited plan",
                "note": "Live data",
                "phone_deals": phone_deals if phone_deals else ["Check website for current promotions"]
            }
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

def scrape_metro():
    print("📡 Scraping Metro...")
    result = scrape_with_playwright("https://www.metrobyt-mobile.com/cell-phone-plans", "Metro")
    if result:
        return result
    cached = load_cached_deals("Metro")
    if cached:
        return cached
    return {"carrier": "Metro", "price": "$25", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": []}

def scrape_cricket():
    print("📡 Scraping Cricket...")
    result = scrape_with_playwright("https://www.cricketwireless.com/cell-phone-plans", "Cricket")
    if result:
        return result
    cached = load_cached_deals("Cricket")
    if cached:
        return cached
    return {"carrier": "Cricket", "price": "$30", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": []}

def scrape_boost():
    print("📡 Scraping Boost...")
    result = scrape_with_playwright("https://www.boostmobile.com/plans", "Boost")
    if result:
        return result
    cached = load_cached_deals("Boost")
    if cached:
        return cached
    return {"carrier": "Boost", "price": "$25", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": []}

def scrape_total():
    print("📡 Scraping Total Wireless...")
    result = scrape_with_playwright("https://www.totalwireless.com/plans", "Total")
    if result:
        return result
    cached = load_cached_deals("Total")
    if cached:
        return cached
    return {"carrier": "Total", "price": "$35", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": []}

# ==================== MAIN EXECUTION ====================
print("=" * 60)
print("📱 Wireless Deal Comparator - AI Powered")
print("=" * 60)

# Archive before running
archive_previous_data()

# Run all scrapers
scrapers = [scrape_metro(), scrape_cricket(), scrape_boost(), scrape_total()]
deals = []

for result in scrapers:
    deals.append(result)
    print(f"✅ {result['carrier']}: {result['price']}/mo")

# Generate AI analysis
print("\n🤖 Generating AI analysis...")
best_deal_analysis = generate_ai_pitch(deals)

# Generate competitive pitches for each carrier
for i, deal in enumerate(deals):
    print(f"   Crafting pitch for {deal['carrier']}...")
    deals[i]['competitive_pitch'] = generate_competitive_pitch(deal, deals)

# Collect all phone deals
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

# Generate HTML report (your existing HTML generation from original file goes here)
# For brevity, using simplified HTML – but your original full HTML template works
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Wireless Deals - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f0f2f5; }}
        .container {{ background: white; border-radius: 20px; padding: 30px; }}
        h1 {{ color: #1a73e8; }}
        .best-deal {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; }}
        .deal {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 15px 0; border-left: 5px solid #1a73e8; }}
        .price {{ font-size: 2em; color: #2e7d32; font-weight: bold; }}
    </style>
</head>
<body>
<div class="container">
    <h1>📱 Wireless Deal Comparator</h1>
    <p>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="best-deal">
        <h2>🏆 AI-Powered Best Deal</h2>
        <p>{best_deal_analysis}</p>
    </div>
"""

for deal in deals:
    html_content += f"""
    <div class="deal">
        <h2>{deal['carrier']}</h2>
        <div class="price">{deal['price']}/month</div>
        <p><strong>Plan:</strong> {deal['deal']}</p>
        <p><strong>Sales Pitch:</strong></p>
        <ul>
            {''.join([f'<li>{bullet}</li>' for bullet in deal.get('competitive_pitch', ['Competitive pricing', 'No contracts'])])}
        </ul>
    </div>
    """

html_content += """
</div>
</body>
</html>
"""

with open("output/report.html", "w") as f:
    f.write(html_content)

print(f"\n✅ Success! Report saved to output/report.html")
print(f"📊 AI analysis complete")
