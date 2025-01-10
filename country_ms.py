import streamlit as st
from eiu import EIU
from countries import countries

class CountryMacroScore:
    def __init__(self):
        self.countries = countries
        self.eiu = EIU()

    def render(self):
        st.title("Country MacroScore™ Analysis")
        countries_selected = st.multiselect("Select a country", options=self.countries, format_func=lambda x: x['name'])
        total_portfolio = st.number_input("Total Portfolio Value", value=1000000, step=1000000)

        country_data = []

        if countries_selected:
            for country in countries_selected:
                with st.expander(f"{country['name']} Metadata"):
                    allocation = st.number_input("Allocation", value=0, key=f"{country['code']}_allocation")
                    country_data.append({
                        "countryName": country['name'],
                        "countryCode": country['code'],
                        "portfolioAllocation": allocation,
                    })

        if st.button("Get MacroScore™"):
            for country in country_data:
                _, country["financialRisk"] = self.eiu.get_score("financialRisk", country.get('countryCode'))
                _, country["operationalRisk"] = self.eiu.get_score("operationalRisk", country.get('countryCode'))


                with st.expander(f"{country['countryName']} MacroScore™"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Financial Risk", country["financialRisk"])
                    with col2:
                        st.metric("Operational Risk", country["operationalRisk"])
                    with col3:
                        macro_score = (country["financialRisk"]*0.4 + country["operationalRisk"]*0.6) * country["portfolioAllocation"] / total_portfolio
                        st.metric("MacroScore™", macro_score)

