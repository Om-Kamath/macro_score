import streamlit as st
from stock_ms import StockMacroScore
from country_ms import CountryMacroScore


st.session_state.pages = {
    "Country MacroScore™ Analysis": CountryMacroScore(),
    "Stock MacroScore™ Analysis": StockMacroScore()
}

class App:
    def __init__(self):
        self.page = st.sidebar.selectbox("Select a page", list(st.session_state.pages.keys()))
        self.page = st.session_state.pages[self.page]

    def run(self):
        self.page.render()

app = App()
app.run()