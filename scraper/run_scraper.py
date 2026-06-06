import json
import os
import shutil
import re
import sys
sys.path.append('.')
from ai_pitch import generate_ai_pitch, generate_competitive_pitch
from datetime import datetime
from playwright.sync_api import sync_playwright
#from ai_pitch import generate_ai_pitch, generate_competitive_pitch

# ==================== ARCHIVE SYSTEM (Rollback ready) ====================
def archive_previous_data():
    """Save current deals.json to archives folder with today's date"""
    if os.path.exists("output/deals.json"):
        archive_dir = f"archives/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(archive_dir, exist_ok=True)
        shutil.copy("output/deals.json", f"{archive_dir}/deals.json")
        print(f"📦 Archived to {archive_dir}")
        
        # Also keep a latest-good copy
        shutil.copy("output/deals.json", "output/latest_good.json")

def load_cached_deals(carrier_name):
    """If a carrier fails, load their last known data from latest_good.json"""
    if os.path.exists("output/latest_good.json"):
        with open("output/latest_good.json", "r") as f:
            cached = json.load(f)
            for deal in cached.get("deals", []):
                if deal["carrier"] == carrier_name:
                    print(f"   → Using cached data for {carrier_name}")
                    return deal
    return None

# ==================== SCRAPERS WITH PLAYWRIGHT ====================
def scrape_with_playwright(url, carrier_name):
    """Generic function for JavaScript-heavy sites"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"   Loading {carrier_name}...")
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)  # Wait for JavaScript to render
            html = page.content()
            browser.close()
            
            # Extract price using regex on the rendered HTML
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', html)
            price = f"${price_match.group(1)}" if price_match else "Check site"
            
            # Look for phone deals
            phone_deals = []
            if "free" in html.lower() and ("phone" in html.lower() or "samsung" in html.lower()):
                phone_deals.append(f"Free phone promotion available at {carrier_name}")
            
            return {
                "carrier": carrier_name,
                "price": price,
                "deal": "Unlimited plan",
                "note": "Live data (Playwright)",
                "phone_deals": phone_deals if phone_deals else ["Check website for current phone promotions"]
            }
    except Exception as e:
        print(f"   ❌ Playwright failed for {carrier_name}: {e}")
        return None

def scrape_metro():
    print("📡 Scraping Metro...")
    result = scrape_with_playwright("https://www.metrobyt-mobile.com/cell-phone-plans", "Metro")
    if result:
        return result
    # Fallback to cache
    cached = load_cached_deals("Metro")
    if cached:
        return cached
    return {"carrier": "Metro", "price": "$25", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": ["Free Samsung with port-in"]}

def scrape_cricket():
    print("📡 Scraping Cricket...")
    result = scrape_with_playwright("https://www.cricketwireless.com/cell-phone-plans", "Cricket")
    if result:
        return result
    cached = load_cached_deals("Cricket")
    if cached:
        return cached
    return {"carrier": "Cricket", "price": "$30", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": ["iPhone deals available"]}

def scrape_boost():
    print("📡 Scraping Boost...")
    # Boost Mobile site structure – using Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.boostmobile.com/plans", timeout=30000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()
            
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', html)
            price = f"${price_match.group(1)}" if price_match else "$25"
            
            return {
                "carrier": "Boost",
                "price": price,
                "deal": "Unlimited plan",
                "note": "Live data (Playwright)",
                "phone_deals": ["Free Motorola phone with switch" if "free" in html.lower() else "Check phone promotions"]
            }
    except Exception as e:
        print(f"   ❌ Boost failed: {e}")
        cached = load_cached_deals("Boost")
        if cached:
            return cached
        return {"carrier": "Boost", "price": "$25", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": ["Free Motorola with switch"]}

def scrape_total():
    print("📡 Scraping Total Wireless...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.totalwireless.com/plans", timeout=30000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()
            
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', html)
            price = f"${price_match.group(1)}" if price_match else "$35"
            
            return {
                "carrier": "Total",
                "price": price,
                "deal": "Unlimited plan",
                "note": "Live data (Playwright)",
                "phone_deals": ["50% off select phones" if "50%" in html else "Check current promotions"]
            }
    except Exception as e:
        print(f"   ❌ Total failed: {e}")
        cached = load_cached_deals("Total")
        if cached:
            return cached
        return {"carrier": "Total", "price": "$35", "deal": "Unlimited plan", "note": "Sample fallback", "phone_deals": ["50% off select phones"]}

# ==================== MAIN EXECUTION ====================
print("=" * 60)
print("📱 Wireless Deal Comparator - Production Ready")
print("=" * 60)

# Archive before running
archive_previous_data()

# Run all scrapers
scrapers = [scrape_metro(), scrape_cricket(), scrape_boost(), scrape_total()]
deals = []

for result in scrapers:
    deals.append(result)
    print(f"✅ {result['carrier']}: {result['price']}/mo - {result['note']}")

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

# Save data with consistent format
output_data = {
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "deals": deals,
    "best_deal_analysis": best_deal_analysis,
    "all_phone_promotions": all_phone_deals
}

with open("output/deals.json", "w") as f:
    json.dump(output_data, f, indent=2)

print(f"\n✅ Saved to output/deals.json")
print(f"📊 Best deal: {best_deal_analysis[:100]}...")

# Generate HTML report (your existing HTML generation code stays here)
# ... (keep your existing HTML generation from line ~120 onward)
