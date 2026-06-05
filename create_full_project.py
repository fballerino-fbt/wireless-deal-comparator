$script = @'
import os
import json

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
project_path = os.path.join(desktop, "wireless-deal-comparator")
os.makedirs(project_path, exist_ok=True)
os.chdir(project_path)

folders = ['scraper/carriers', 'ai', 'output/current', 'output/logs', 'output/rollback', 'dashboard', '.github/workflows', 'archives']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

print(f"[OK] Project created at: {project_path}")

config = {
    "carriers": [
        {"name": "Metro by T-Mobile", "urls": ["https://www.metrobyt-mobile.com/cell-phone-plans"], "type": "dynamic"},
        {"name": "Cricket Wireless", "urls": ["https://www.cricketwireless.com/cell-phone-plans"], "type": "dynamic"},
        {"name": "Boost Mobile", "urls": ["https://www.boostmobile.com/plans"], "type": "dynamic"},
        {"name": "Total Wireless", "urls": ["https://www.totalwireless.com/plans"], "type": "dynamic"}
    ],
    "target_phones": ["iPhone", "Samsung Galaxy", "Google Pixel", "free phone"],
    "sales_angle": {
        "contract_freedom": "No annual contracts - cancel anytime",
        "quality": "Same network towers as top carriers at half the price",
        "price": "Save 30-50% vs postpaid plans"
    },
    "ai": {"provider": "groq", "model": "llama3-70b-8192"},
    "archive_days": 30,
    "auth": {"shared_password": "compare2025"}
}

with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

requirements = """requests==2.31.0
beautifulsoup4==4.12.2
playwright==1.40.0
groq==0.4.2
tenacity==8.2.3
fake-useragent==1.4.0
python-dotenv==1.0.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

base_scraper = '''import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
import time
import hashlib

class BaseScraper:
    def __init__(self, carrier_name, urls, scraper_type="dynamic"):
        self.carrier_name = carrier_name
        self.urls = urls if isinstance(urls, list) else [urls]
        self.scraper_type = scraper_type
        self.ua = UserAgent()
        self.session = requests.Session()
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_html_dynamic(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
            return html
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch_html_static(self, url):
        headers = {'User-Agent': self.ua.random}
        response = self.session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    
    def get_all_html(self):
        all_html = []
        for url in self.urls:
            if self.scraper_type == "dynamic":
                html = self.fetch_html_dynamic(url)
            else:
                html = self.fetch_html_static(url)
            all_html.append(html)
        return all_html
    
    def extract_price(self, text):
        import re
        match = re.search(r'\$(\\d+(?:\\.\\d{2})?)', text)
        return float(match.group(1)) if match else None
    
    def detect_change(self, old_hash, html):
        new_hash = hashlib.md5(html.encode()).hexdigest()
        if old_hash and old_hash != new_hash:
            with open('output/logs/change_alerts.txt', 'a') as f:
                f.write(f"{self.carrier_name}: HTML changed at {time.ctime()}\\n")
        return new_hash
'''

with open('scraper/base_scraper.py', 'w') as f:
    f.write(base_scraper)

metro_scraper = '''from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

class MetroScraper(BaseScraper):
    def __init__(self):
        super().__init__("Metro by T-Mobile", ["https://www.metrobyt-mobile.com/cell-phone-plans"], "dynamic")
    
    def parse_deals(self, html_list):
        all_deals = []
        for html in html_list:
            soup = BeautifulSoup(html, 'html.parser')
            plan_cards = soup.select('.plan-card, .rate-plan-card, [class*="plan"]')
            for card in plan_cards[:5]:
                name_elem = card.select_one('.plan-name, h3, h4')
                price_elem = card.select_one('.price, .plan-price, [class*="price"]')
                if name_elem and price_elem:
                    all_deals.append({
                        'carrier': self.carrier_name,
                        'plan_name': name_elem.text.strip()[:100],
                        'price': self.extract_price(price_elem.text),
                        'contract': 'No contract',
                        'phone_deals': self.extract_phone_deals(soup)
                    })
        return all_deals
    
    def extract_phone_deals(self, soup):
        text = soup.get_text().lower()
        deals = []
        if 'free phone' in text or 'free samsung' in text:
            deals.append('Free phone with port-in')
        if 'iphone' in text:
            deals.append('iPhone deals available')
        return deals
'''

with open('scraper/carriers/metro.py', 'w') as f:
    f.write(metro_scraper)

cricket_scraper = '''from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

class CricketScraper(BaseScraper):
    def __init__(self):
        super().__init__("Cricket Wireless", ["https://www.cricketwireless.com/cell-phone-plans"], "dynamic")
    
    def parse_deals(self, html_list):
        all_deals = []
        for html in html_list:
            soup = BeautifulSoup(html, 'html.parser')
            plan_cards = soup.select('.plan-tile, .plan-card, [class*="plan"]')
            for card in plan_cards[:5]:
                name_elem = card.select_one('.plan-name, h4')
                price_elem = card.select_one('.price, .plan-price')
                if name_elem and price_elem:
                    all_deals.append({
                        'carrier': self.carrier_name,
                        'plan_name': name_elem.text.strip()[:100],
                        'price': self.extract_price(price_elem.text),
                        'contract': 'No contract (30-day terms)',
                        'phone_deals': self.extract_phone_deals(soup)
                    })
        return all_deals
    
    def extract_phone_deals(self, soup):
        text = soup.get_text().lower()
        deals = []
        if 'free' in text and 'iphone' in text:
            deals.append('iPhone deals available')
        return deals
'''

with open('scraper/carriers/cricket.py', 'w') as f:
    f.write(cricket_scraper)

boost_scraper = '''from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

class BoostScraper(BaseScraper):
    def __init__(self):
        super().__init__("Boost Mobile", ["https://www.boostmobile.com/plans"], "dynamic")
    
    def parse_deals(self, html_list):
        all_deals = []
        for html in html_list:
            soup = BeautifulSoup(html, 'html.parser')
            plan_cards = soup.select('.plan-card, [class*="plan"]')
            for card in plan_cards[:5]:
                name_elem = card.select_one('h3, h4, .plan-name')
                price_elem = card.select_one('.price, .plan-price')
                if name_elem and price_elem:
                    all_deals.append({
                        'carrier': self.carrier_name,
                        'plan_name': name_elem.text.strip()[:100],
                        'price': self.extract_price(price_elem.text),
                        'contract': 'No contract',
                        'phone_deals': ['Check site for current phone promotions']
                    })
        return all_deals
'''

with open('scraper/carriers/boost.py', 'w') as f:
    f.write(boost_scraper)

total_scraper = '''from scraper.base_scraper import BaseScraper
from bs4 import BeautifulSoup

class TotalScraper(BaseScraper):
    def __init__(self):
        super().__init__("Total Wireless", ["https://www.totalwireless.com/plans"], "dynamic")
    
    def parse_deals(self, html_list):
        all_deals = []
        for html in html_list:
            soup = BeautifulSoup(html, 'html.parser')
            plan_cards = soup.select('.plan-card, [class*="plan"]')
            for card in plan_cards[:5]:
                name_elem = card.select_one('h3, h4')
                price_elem = card.select_one('.price')
                if name_elem and price_elem:
                    all_deals.append({
                        'carrier': self.carrier_name,
                        'plan_name': name_elem.text.strip()[:100],
                        'price': self.extract_price(price_elem.text),
                        'contract': 'No contract',
                        'phone_deals': ['Promotions available on select phones']
                    })
        return all_deals
'''

with open('scraper/carriers/total.py', 'w') as f:
    f.write(total_scraper)

ai_pitch = '''import os
import json
from groq import Groq

class AIPitchGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
    
    def generate_comparison_pitch(self, competitor_deals, sales_angle):
        deals_summary = []
        for deal in competitor_deals[:10]:
            deals_summary.append(f"{deal['carrier']}: {deal['plan_name']} at ${deal.get('price', 'N/A')}/mo")
        
        prompt = f\"\"\"
        You are a wireless sales expert. Competitor deals: {json.dumps(deals_summary)}
        Your advantages: Contract freedom, network quality, 30-50% savings.
        
        Generate a JSON response:
        {{\"pitch\": \"2-3 sentence sales pitch beating competitors\", 
          \"comparison_summary\": \"Table showing why we beat each competitor\",
          \"recommendation\": \"Best plan for customers\"}}
        \"\"\"
        
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
'''

with open('ai/pitch_generator.py', 'w') as f:
    f.write(ai_pitch)

runner = '''import os, json, shutil
from datetime import datetime
from scraper.carriers.metro import MetroScraper
from scraper.carriers.cricket import CricketScraper
from scraper.carriers.boost import BoostScraper
from scraper.carriers.total import TotalScraper
from ai.pitch_generator import AIPitchGenerator

def archive_previous():
    today = datetime.now().strftime("%Y-%m-%d")
    archive_dir = f"archives/{today}"
    if os.path.exists("output/current/deals.json"):
        os.makedirs(archive_dir, exist_ok=True)
        shutil.copy("output/current/deals.json", f"{archive_dir}/deals.json")
        print(f"Archived to {archive_dir}")
    if os.path.exists("output/current/deals.json"):
        os.makedirs("output/rollback", exist_ok=True)
        shutil.copy("output/current/deals.json", "output/rollback/latest_good.json")

def run_all():
    os.makedirs("output/current", exist_ok=True)
    archive_previous()
    
    scrapers = [MetroScraper(), CricketScraper(), BoostScraper(), TotalScraper()]
    all_deals = []
    success_count = 0
    
    for scraper in scrapers:
        try:
            html_list = scraper.get_all_html()
            deals = scraper.parse_deals(html_list)
            all_deals.extend(deals)
            success_count += 1
            print(f"OK {scraper.carrier_name}: {len(deals)} deals")
        except Exception as e:
            print(f"FAIL {scraper.carrier_name}: {e}")
    
    if success_count == 0 and os.path.exists("output/rollback/latest_good.json"):
        print("All failed! Rolling back...")
        with open("output/rollback/latest_good.json") as f:
            data = json.load(f)
            with open("output/current/deals.json", "w") as out:
                json.dump(data, out)
            return data
    
    ai = AIPitchGenerator()
    with open('config.json') as f:
        config = json.load(f)
    ai_pitch = ai.generate_comparison_pitch(all_deals, config.get('sales_angle', {}))
    
    output = {
        "date": datetime.now().isoformat(),
        "deals": all_deals,
        "ai_pitch": ai_pitch,
        "successful_scrapers": success_count
    }
    
    with open("output/current/deals.json", "w") as f:
        json.dump(output, f, indent=2)
    
    html = '<!DOCTYPE html>\\n<html>\\n<head><title>Wireless Deals</title><style>\\nbody { font-family: Arial; background: #0a0a0a; color: white; padding: 20px; }\\n.deal { background: #1a1a1a; margin: 10px; padding: 15px; border-radius: 10px; }\\n.price { color: #00ff88; font-size: 24px; }\\n</style></head>\\n<body>\\n<h1>Best Wireless Deals - ' + datetime.now().strftime("%Y-%m-%d") + '</h1>\\n'
    
    for d in all_deals:
        price_val = d.get('price', 'N/A')
        html += f'<div class="deal"><h3>{d["carrier"]}</h3><div class="price">${price_val}/mo</div><p>{d["plan_name"]}</p><p>{d["contract"]}</p></div>\\n'
    
    html += f'<div class="deal"><h2>Our Pitch</h2><p>{ai_pitch.get("pitch", "Save with no contracts!")}</p></div></body></html>'
    
    with open("output/current/comparison.html", "w") as f:
        f.write(html)
    
    print(f"Done! {success_count}/4 carriers successful")
    return output

if __name__ == "__main__":
    run_all()
'''

with open('scraper/run_scraper.py', 'w') as f:
    f.write(runner)

workflow = '''name: Weekly Deal Scraper
on:
  schedule:
    - cron: '0 9 * * 1'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: playwright install chromium
      - run: python scraper/run_scraper.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      - uses: actions/upload-pages-artifact@v2
        with:
          path: output/current/
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output/current
'''

with open('.github/workflows/weekly_scrape.yml', 'w') as f:
    f.write(workflow)

readme = '''# Wireless Deal Comparator

## Setup
1. Get Groq API key from console.groq.com
2. Add to GitHub Secrets as GROQ_API_KEY
3. Enable GitHub Actions

## Run Locally
pip install -r requirements.txt
playwright install chromium
set GROQ_API_KEY=your_key_here
python scraper/run_scraper.py

## View Results
- output/current/comparison.html - Static page
- output/current/deals.json - Raw data
'''

with open('README.md', 'w') as f:
    f.write(readme)

print("")
print("="*50)
print("ALL FILES CREATED SUCCESSFULLY!")
print(f"Location: {project_path}")
print("="*50)
print("")
print("NEXT STEPS:")
print(f"cd {project_path}")
print("pip install -r requirements.txt")
print("playwright install chromium")
print("set GROQ_API_KEY=your_groq_key_here")
print("python scraper/run_scraper.py")
'@

$script | Out-File -FilePath "$env:USERPROFILE\Desktop\create_full_project.py" -Encoding ASCII