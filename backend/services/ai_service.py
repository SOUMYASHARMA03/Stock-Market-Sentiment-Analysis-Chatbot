import os
import requests
import random
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

def get_query_type(query):
    q = query.lower().strip().replace("?", "").replace("!", "")
    # Acknowledgments / Negatives
    if q in ["ok", "okay", "thanks", "thank you", "got it", "fine", "cool", "perfect", "no", "nope", "nothing", "exit", "awesome", "great"]:
        return "acknowledgment"
    # General greetings
    greetings = {"hi", "hii", "hiii", "hello", "hey", "heyy", "heyya", "helloo", "who are you", "who are u", "what is your name", "whats up"}
    words = set(q.split())
    if q in greetings or not words.isdisjoint(greetings):
        return "greeting"
    # Deep/Advanced questions
    DEEP_KEYWORDS = [
        "why", "how come", "deep dive", "in depth", "in-depth", "detailed", "elaborate", 
        "compare", "difference between", "impact of", "future of", "predict", "forecast", 
        "deeply", "explain in detail", "analyze deeply", "elaborate on", "evaluate", "assess",
        "critique", "review", "outlook", "expectation", "projection", "trend", "trajectory",
        "what happens if", "scenario", "consequence", "valuation", "fundamental analysis",
        "technical analysis", "risk", "return", "roi", "earnings report", "balance sheet",
        "income statement", "cash flow", "debt", "equity", "dividend", "should i buy",
        "should i invest", "should i sell", "portfolio", "asset allocation", "diversification",
        "hedge", "arbitrage", "macroeconomic", "interest rates", "inflation", "recession",
        "bull market", "bear market", "market crash", "bubble", "sentiment", "short squeeze",
        "options strategy", "liquidity", "volatility", "break down", "walk me through",
        "step by step", "comprehensive", "thoroughly", "underlying cause", "core reason",
        "driving force", "behind the scenes", "pros and cons", "advantages", "disadvantages",
        "strengths", "weaknesses", "long term", "short term", "strategy", "investment thesis",
        "catalyst", "headwinds", "tailwinds", "market share", "competitive advantage", "moat",
        "growth potential", "intrinsic value", "price target", "analyst rating", "downgrade",
        "upgrade", "merger", "acquisition", "spinoff", "buyback", "insider trading",
        "institutional ownership", "sec filing", "10-k", "10-q", "earnings call", "guidance",
        "profit margin", "revenue growth", "eps", "p/e ratio", "peg ratio", "price to book",
        "debt to equity", "free cash flow", "ebitda", "capital expenditure", "supply chain",
        "regulation", "geopolitical", "tariffs", "trade war", "federal reserve", "fed rate",
        "quantitative easing", "tightening", "yield curve", "bond market", "crypto", "bitcoin",
        "ethereum", "blockchain", "smart contract", "defi", "nft", "web3", "metaverse",
        "artificial intelligence", "machine learning", "cloud computing", "saas", "ev",
        "electric vehicle", "semiconductor", "chip shortage", "green energy", "esg",
        "sustainability", "climate change", "demographics", "consumer spending", "retail sales",
        "unemployment", "gdp", "cpi", "ppi", "housing market", "mortgage rates", "commodity",
        "oil", "gold", "silver", "copper", "supply and demand", "bottleneck", "innovation",
        "disruption", "startups", "venture capital", "ipo", "spac", "direct listing",
        "what is the reason", "how will this affect", "what are the implications", "strategic",
        "long-term vision", "business model", "monetization", "user growth", "churn rate",
        "customer acquisition cost", "lifetime value", "network effects", "economies of scale",
        "barriers to entry", "first mover advantage", "patent", "intellectual property",
        "lawsuit", "antitrust", "monopoly", "oligopoly", "cartel", "price fixing", "dumping",
        "chart", "graph", "plot", "historical", "history"
    ]
    if any(phrase in q for phrase in DEEP_KEYWORDS):
        return "deep"
    # Analysis / Summary triggers (Priority)
    if any(word in q for word in ["summarize", "analysis", "summary", "news", "opinion", "article"]):
        return "analysis"
    # Simple questions
    if any(phrase in q for phrase in ["what is", "define", "meaning", "how much", "what are", "tell me about", "explain", "what does", "how to"]):
        return "simple"
    
    # Default to simple to avoid forcing strict news formatting on general questions
    return "simple"

def chatbot(query, context=""):
    """
    Main chatbot function with intelligent formatting and safety filters.
    """
    query_type = get_query_type(query)
    
    if query_type == "acknowledgment":
        responses = [
            "Got it! Let me know if you need anything else—like a stock summary or a term explained. 📈",
            "Happy to help! Feel free to ask if you have more questions about the market. 🚀",
            "Understood. I'm here if you need more analysis or financial insights! 📊",
            "Perfect. Let me know what we should analyze next! 📉",
            "Glad I could help. Have a great day of trading! 🌟"
        ]
        return random.choice(responses)

    if query_type == "greeting":
        return "Hello! I am StockBot, your dedicated financial analyst.\n\nI can help you analyze stock charts, explain complex financial terms, or summarize the latest market news. What would you like to explore today?"

    # Define system prompt for analysis and safety
    system_prompt = (
        "You are StockBot, a professional AI Stock Analyst. "
        "Your expertise is strictly limited to the stock market, finance, and company analysis. "
        "\n\n**Safety Rule**: If the user asks about anything NOT related to stocks/finance, politely decline."
        "\n\n**Chart Rule**: If asked to explain a chart/graph, use the 'Chart/Graph History' data provided in the context to explain the price trend. Do NOT say there is no chart."
        "\n\n**Formatting Rules**:"
    )

    if query_type == "simple":
        system_prompt += (
            "\n- The user asked a simple definition or fact. "
            "\n- Answer directly and concisely in 2-3 sentences. "
            "\n- Do not use the full analysis template."
        )
    elif query_type == "deep":
        system_prompt += (
            "\n- The user asked an analytical question. "
            "\n- Provide a short, clear, and highly precise answer. "
            "\n- Do NOT write overly long essays. Get straight to the point. "
            "\n- Use bullet points and bold text for key terms to make it easy to read."
        )
    else:
        system_prompt += (
            "\n- The user wants an analysis or summary. "
            "\n- ALWAYS use this exact structured format with newlines:\n\n"
            "**Short Summary**:\n[1-2 sentences]\n\n"
            "**👉 Top News Headlines**:\n"
            "- [Headline 1]\n\n"
            "- [Headline 2]\n\n"
            "**👉 Key Insights**:\n"
            "- [Insight 1]\n\n"
            "- [Insight 2]\n\n"
            "Keep it very short and professional. Use **bold** for subheaders. "
            "DO NOT include any analogies or 'Simple Example' sections anymore."
        )
    
    full_prompt = f"Context:\n{context}\n\nUser Query: {query}"
    
    # Try using Groq API via requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    
    last_error = ""
    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.3,
        }
        
        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if hasattr(e, 'response') and e.response is not None:
                last_error += f" - Response: {e.response.text}"
            if "429" in last_error or "503" in last_error or "404" in last_error or "400" in last_error:
                continue
            break
        except Exception as e:
            last_error = str(e)
            break
            
    return f"⚠️ AI Error: {last_error if last_error else 'Could not generate response.'}"