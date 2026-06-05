import os
from groq import Groq

def generate_ai_pitch(deals_data):
    """Generate sales pitch using Groq AI"""
    
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "🔧 AI ready - Add GROQ_API_KEY environment variable"
    
    try:
        client = Groq(api_key=api_key)
        
        # Prepare deals summary for AI
        deals_summary = "\n".join([
            f"- {d['carrier']}: {d['deal']} at ${d['price'] if isinstance(d['price'], (int,float)) else 'check site'}"
            for d in deals_data
        ])
        
        prompt = f"""You are a wireless sales expert. Current competitor deals:
{deals_summary}

Your advantages over them:
- No contracts (they also have no contracts, but you save more)
- Same network quality (they use T-Mobile/AT&T/Verizon towers)
- Save 30-50% vs major carriers like Verizon/AT&T/T-Mobile postpaid

Write a compelling 3-sentence sales pitch that:
1. Highlights the best deal among competitors
2. Explains why prepaid is better than postpaid
3. Ends with an urgent call-to-action

Make it enthusiastic but professional."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"⚠️ AI temporarily unavailable: {str(e)[:100]}"