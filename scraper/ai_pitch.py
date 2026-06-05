import os
from groq import Groq

def generate_ai_pitch(deals_data):
    """Generate best deal analysis in exactly 3 lines"""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Best deal: Compare carriers for lowest price. Check Metro or Boost at $25/mo for unlimited."
    
    try:
        client = Groq(api_key=api_key)
        
        deals_summary = "\n".join([
            f"- {d['carrier']}: {d['price']}/mo for {d['deal']}"
            for d in deals_data
        ])
        
        prompt = f"""Wireless deals: {deals_summary}

Identify the absolute best deal. Return EXACTLY 3 lines (sentences) with:

Line 1: Which carrier has the best deal and their price
Line 2: The #1 main reason why it's the best (price, data, or features)
Line 3: A one-sentence recommendation

Be specific. No markdown. No extra text. Just 3 lines."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Best deal: {deals_data[0]['carrier']} at {deals_data[0]['price']}/mo\nReason: Lowest price\nRecommendation: Switch today and save"

def generate_competitive_pitch(deal, all_deals):
    """Generate 3 bullet points for sales team to win vs competitors"""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return ["Competitive pricing", "No contracts", "Same network quality"]
    
    try:
        client = Groq(api_key=api_key)
        
        competitors = [d for d in all_deals if d['carrier'] != deal['carrier']]
        competitor_summary = "\n".join([f"- {c['carrier']}: {c['price']}/mo" for c in competitors])
        
        prompt = f"""Carrier: {deal['carrier']} at {deal['price']}/mo
Competitors: {competitor_summary}

Create exactly 3 bullet points (short phrases) that a salesperson would use to win business FOR {deal['carrier']} AGAINST competitors.

Focus on: price advantage, network quality, phone deals, or no contracts.

Return as JSON array: ["point 1", "point 2", "point 3"]"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=150
        )
        
        import json
        # Try to parse JSON, fallback to text split
        try:
            bullets = json.loads(response.choices[0].message.content)
            return bullets[:3]
        except:
            text = response.choices[0].message.content
            bullets = [b.strip('-• ') for b in text.split('\n') if b.strip()][:3]
            return bullets if len(bullets) == 3 else ["Lowest price in market", "No hidden fees", "Keep your current phone"]
        
    except Exception as e:
        return ["Competitive pricing", "No contracts", "Same network quality"]

def generate_sales_pitch(deal, all_deals):
    """Legacy function - kept for compatibility"""
    return generate_competitive_pitch(deal, all_deals)
