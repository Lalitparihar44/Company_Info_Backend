import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import nest_asyncio

# Agent/Tool setup
from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools

# Set API keys
os.environ["AGNO_API_KEY"] = "ag-5REAI2rIKVL_wQKmujCZQ2sBEMTUIROYU5jGedxtzx8"
os.environ["GROQ_API_KEY"] = "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"

# Initialize agent
stock_agent = Agent(
    model=Groq(id="llama3-8b-8192"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            historical_prices=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=dedent("""\
        You are a seasoned credit rating analyst with deep expertise in market analysis! 📊

        Follow these steps for comprehensive financial analysis:
        1. Market Overview
           - Latest stock price
           - 52-week high and low
        2. Financial Deep Dive
           - Key metrics (P/E, Market Cap, EPS, Cash Flow)
        3. Market Context
           - Industry trends and positioning
           - Competitive analysis
           - Market sentiment indicators

        Your reporting style:
        - Begin with an executive summary
        - Clearly mention the company's **full name** and its **stock ticker (if available)**
        - Use tables for data presentation
        - Include clear section headers
        - Highlight key insights with bullet points
        - Compare metrics to industry averages
        - Include technical term explanations
        - End with a forward-looking analysis

        Risk Disclosure:
        - Always highlight potential risk factors
        - Note market uncertainties
        - Mention relevant regulatory concerns
    """),
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
)

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Just for quick test if the backend is running
@app.route('/', methods=['GET'])
def index():
    return 'Flask backend is running! Use POST /get_company_info with JSON: { "company": "Tesla" }', 200

@app.route('/get_company_info', methods=['POST', 'OPTIONS'])
def get_company_info():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        data = request.get_json()
        company = data.get('company', '').strip()

        if not company:
            return jsonify({'error': 'No company name provided'}), 400

        result = stock_agent.run(company)
        return jsonify({'report': result.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the server locally
if __name__ == '__main__':
    nest_asyncio.apply()  # for async compatibility
    app.run(host='0.0.0.0', port=5000)
