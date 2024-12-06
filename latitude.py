import requests
import streamlit as st

class AI:
    def __init__(self):
        self.api_url = "https://gateway.latitude.so/api/v2/projects/11095/versions/live/documents/run"
        self.api_key = st.secrets['LATITUDE']
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_summary(self, text):
        data = {
            "path": "eiuSummarizer",
            "stream": False,
            "parameters": {
                "news": text
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        return response.json().get("response").get("text")
    

    def get_macro_score_analysis(self, risk_reports, eiu_views, stock, stock_description):
        data = {
            "path": "eiuMacroScoreAnalysis",
            "stream": False,
            "parameters": {
                "news": risk_reports,
                "stock": stock,
                "description": stock_description,
                "industryNews": eiu_views,
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        return response.json().get("response").get("text")
    
    def get_portfolio_macro_score_analysis(self, portfolio_json):
        data = {
            "path": "eiuMacroWithJson",
            "stream": False,
            "parameters": {
                "portfolio": portfolio_json
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=data)
        return response.json().get("response").get("text")