import streamlit as st
from eiu import EIU
from countries import countries
from stocks import stock_dic
from reports import report_codes
from latitude import AI
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import altair as alt


class StockMacroScore:

    def __init__(self):
        self.stocks = stock_dic
        self.countries = countries
        self.report_codes = report_codes
        self.eiu = EIU()
        self.ai = AI()

        if 'final_analysis' not in st.session_state:
            st.session_state.final_analysis = ""

        if 'macro_score' not in st.session_state:
            st.session_state.macro_score = 0

        if 'historic_macro_score' not in st.session_state:
            st.session_state.historic_macro_score = []
    
    
    def render(self):
        st.title("MacroScore™ Analysis")

        stocks = st.multiselect("Select stocks", self.stocks, format_func=lambda x: x['stock'])

        stock_data = {}


        if stocks:
            # all_stocks = stocks.replace(" ", "").upper().split(",")
            for stock in stocks:
                stock_info = yf.Ticker(stock['stock']).info
                stock_name = stock_info.get('longName', 'Unknown')
                stock_description = stock_info.get('longBusinessSummary', 'Unknown')
                with st.expander(f"{stock_name} Metadata"):
                    st.write(f"#### {stock_name}")
                    
                    allocation = st.number_input("Allocation (%)", value=stock['allocation'], key=f"{stock}_allocation")
                    industry = st.selectbox("Select an industry", index=stock['industry'], options=["Automotive", "Consumer goods", "Financial services", "Healthcare", "Energy", "Telecommunications"], key=f"{stock}_industry")
                    countries_selected = st.multiselect("Select countries", default=stock['countries'],  options=countries, format_func=lambda x: x['name'], key=f"{stock}_countries")
                    stock_data[stock.get('stock')] = {
                        "stock_name": stock_name,
                        "stock_description": stock_description,
                        "allocation": allocation,
                        "industry": industry,
                        "macro_score": 0,
                        "countries": [],
                        "maps": stock.get('map')
                    }
                    
                    for country in countries_selected:
                        st.write(f"Country: {country['name']}")
                        default_revenue = next((revenue['revenue'] for revenue in stock['revenues'] if revenue['code'] == country['code']), 0)
                        revenue = st.number_input("Revenue (%)", value=default_revenue, key=f"{stock}_{country['code']}_revenue")
                        stock_data[stock.get('stock')]["countries"].append({
                            "country_name": country['name'],
                            "country_code": country['code'],
                            "revenue": revenue
                        })
                        
                

            if st.button("Get MacroScore™"):
                st.divider()
                for stock, data in stock_data.items():
                    st.session_state.historic_macro_score = np.random.randint(0, 101, size=10).tolist()  # 10 random values between 0 and 100
                    with st.expander(f"{stock} Details"):
                        final_score = 0
                        for country in data["countries"]:
                            stock_name = data["stock_name"]
                            stock_description = yf.Ticker(stock).info['longBusinessSummary']
                            
                            with st.spinner("Calculating MacroScore™..."):
                                try:
                                    source_op, op_risk = self.eiu.get_score("operationalRisk", country['country_code'])
                                    source_fin, fin_risk = self.eiu.get_score("financialRisk", country['country_code'])
                                
                                except Exception as e:
                                    st.error(f"Error occurred: There is not enough data for {country['country_name']}")
                                    continue
                                macro_score = (op_risk + fin_risk) / 2
                                cols = st.columns(3)
                                cols[0].metric(label=f"{country['country_name']}", value=op_risk, delta=source_op)
                                cols[1].metric(label=f"{country['country_name']}", value=fin_risk, delta=source_fin)
                                cols[2].metric(label=f"MacroScore™", value=macro_score)
                            final_score += macro_score * country['revenue'] / 100

                        stock_data[stock]["macro_score"] = final_score
                        cols = st.columns(3)
                        cols[1].metric(label=f"{stock} MacroScore™", value=f"{final_score:.2f}")

                st.session_state.macro_score = sum([data["macro_score"] * data["allocation"] / 100 for data in stock_data.values()])
                st.session_state.historic_macro_score.append(st.session_state.macro_score)
                    
                with st.spinner("Generating a MacroScore™ Report"):
                    all_risk_reports = ""
                    all_eiu_views = ""
                    for stock,data in stock_data.items():
                        stock_name = data["stock_name"]
                        revenue_countries = data["countries"]
                        for country in revenue_countries:
                            risk_report = BeautifulSoup(self.eiu.fetch_reports(country_code=country['country_code'], report_codes=report_codes), 'html.parser').get_text()
                            eiu_views = BeautifulSoup(self.eiu.get_eiu_views(country_code=country['country_code'], industry=data["industry"]), 'html.parser').get_text()
                            all_risk_reports += f"*For {country['country_name']}* {risk_report}"
                            all_eiu_views += f"*For {country['country_name']}* {eiu_views}"
                            stock_data[stock]["risk_reports"] = all_risk_reports
                            stock_data[stock]["eiu_views"] = all_eiu_views

                    st.session_state.final_analysis = self.ai.get_portfolio_macro_score_analysis(stock_data)

        
            df = pd.DataFrame({
                'MacroScore': st.session_state.historic_macro_score
            })
            
            st.line_chart(df, width=250, height=250, x_label="Months", y_label="MacroScore™" )
            st.metric(label="Overall MacroScore™", value=f"{st.session_state.macro_score:.2f}")

            
            @st.dialog("MacroScore™ Report", width="large")
            def show_report():
                st.markdown(st.session_state.final_analysis, unsafe_allow_html=True)

            if st.session_state.final_analysis != "":
                if st.button("Show MacroScore™ Report", type="secondary"):
                    show_report()