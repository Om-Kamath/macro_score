import streamlit as st
from eiu import EIU
from countries import countries
from reports import report_codes
from latitude import AI
import yfinance as yf
import streamviz

window = st.sidebar.selectbox("Select a category", ["Country-wise Analysis", "MacroScore™"])
eiu = EIU()

if window == "Country-wise Analysis":
    st.title("Country-wise Analysis")
    country = st.selectbox("Select a country", countries, format_func=lambda x: x['name'])


    if st.button("Get Score"):
        with st.spinner("Calculating macro score..."):
            cols = st.columns(3)
            country_ms = 0
            for i, score_series in enumerate(["operationalRisk", "financialRisk"]):
                source, value = eiu.get_score(score_series, country['code'])
                country_ms += int(value)
                cols[i].metric(label=source, value=value)
            cols[2].metric(label="Country-wise MacroScore™", value=country_ms / 2)
        
        with st.spinner("Summarizing"):
            # st.markdown(eiu.fetch_reports(country_code=country["code"], report_codes=report_codes), unsafe_allow_html=True)
            st.markdown(AI().get_summary(eiu.fetch_reports(country_code=country["code"], report_codes=report_codes)), unsafe_allow_html=True)

elif window == "MacroScore™":
    st.title("MacroScore™ Analysis")
    
    stock = st.text_input("Enter a stock symbol")
    countries = st.multiselect("Select countries", countries, format_func=lambda x: x['name'])
    industry = st.selectbox("Select an industry", ["Automotive", "Consumer goods", "Financial services", "Healthcare", "Energy", "Telecommunications"])
    revenue_countries = []
    st.write("#### Add revenue distribution")
    for country in countries:
        st.write(f"Country: {country['name']}")
        revenue = st.number_input("Revenue (%)", value=0, key=country['code'])
        revenue_countries.append({
            "country_name": country['name'],
            "country_code": country['code'],
            "revenue": revenue
        })

    if st.button("Get MacroScore™ Report"):
        stock_name = yf.Ticker(stock).info['longName']
        stock_description = yf.Ticker(stock).info['longBusinessSummary']
        final_score = 0
        with st.spinner("Calculating MacroScore™..."):
            for country in revenue_countries:
                try:
                    source_op, op_risk = eiu.get_score("operationalRisk", country['country_code'])
                    source_fin, fin_risk = eiu.get_score("financialRisk", country['country_code'])
                except Exception as e:
                    st.error(f"Error occurred: There is not enough data for {country['country_name']}")
                    continue
                macro_score = (op_risk + fin_risk) / 2
                cols = st.columns(3)
                cols[0].metric(label=f"{country['country_name']}", value=op_risk, delta=source_op)
                cols[1].metric(label=f"{country['country_name']}", value=fin_risk, delta=source_fin)
                cols[2].metric(label=f"MacroScore™", value=macro_score)
                final_score += macro_score * country['revenue']/100

            cols = st.columns(3)
            cols[1].metric(label=f"{stock} MacroScore™", value=f"{final_score:.2f}")
        
        with st.spinner("Generating a MacroScore™ Report"):
            all_risk_reports = ""
            all_eiu_views = ""
            for country in revenue_countries:
                all_risk_reports+=f"For {country["country_name"]}\n {eiu.fetch_reports(country_code=country["country_code"], report_codes=report_codes)}"
                all_eiu_views+=f"For {country["country_name"]}\n {eiu.get_eiu_views(country_code=country["country_code"], industry=industry)}"
            
            with st.expander("Risk Reports"):
                st.markdown(all_risk_reports, unsafe_allow_html=True)
            with st.expander("EIU Views"):
                st.markdown(all_eiu_views, unsafe_allow_html=True)

            st.markdown(AI().get_macro_score_analysis(all_risk_reports, all_eiu_views, stock_name, stock_description), unsafe_allow_html=True)

