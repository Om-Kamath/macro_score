import streamlit as st
import requests
import endpoints
from datetime import datetime, timedelta
from series import series


class EIU:
    def __init__(self):
        self.username = 'oriol@justbuildit.com'
        self.password = st.secrets['EIU_PASS']
        self.x_api_key = st.secrets['EIU_API_KEY']
        self.token = None
        self.token_expiry = None

    def is_token_valid(self):
        # Check if the token is valid and not expired
        return self.token is not None and self.token_expiry is not None and datetime.now() < self.token_expiry

    def get_token(self):
        if self.is_token_valid():
            return self.token

        print("Generating Token")
        url = endpoints.BASE_URL + endpoints.MAIN_ENDPOINTS["login"]
        headers = {
            'x-api-key': self.x_api_key
        }
        data = {
            'emailAddress': self.username,
            'password': self.password
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()
        self.token = token_data.get("token")
        self.token_expiry = datetime.now() + timedelta(seconds=token_data.get("expiresIn"))  # Assuming the token is valid for 1 hour
        return self.token
    
    def get_score(self, score_series, country_code):
        if not self.is_token_valid():
            self.get_token()

        url = endpoints.BASE_URL + endpoints.SCORE_ENDPOINTS["score"]
        headers = {
            'x-api-key': self.x_api_key,
            'Authorization': f'Bearer {self.token}'
        }
        now = datetime.now()
        data = {
            "minDate": (now - timedelta(days=30)).isoformat(timespec='seconds') + 'Z',
            "frequencyType": "Monthly",
            "maxDate": now.isoformat(timespec='seconds') + 'Z',
            "seriesCodes": [
                series[score_series]["score"]
            ],
            "geographyCodes": [
                country_code
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['dataPointRecords'][0].get('source'), float(response.json()['dataPointRecords'][0]['points'][0].get('value'))
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:  # Unauthorized
                self.token = self.get_token()
                print("Token expired, getting new token", self.token)
                return self.get_score(score_series, country_code)
            else:
                print(f"HTTP error occurred: {http_err}")
                response.raise_for_status()
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise

    def get_report(self, report_code, country_code):
        if not self.is_token_valid():
            self.get_token()

        try:
            url = endpoints.BASE_URL + endpoints.REPORT_ENDPOINTS["report"]
            headers = {
                'x-api-key': self.x_api_key,
                'Authorization': f'Bearer {self.token}'
            }
            params = {
                "reportCode": report_code,
                "geographyCode": country_code
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
           
            return response.json()['results'][0]['apiUrl']
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                self.token = self.get_token()
                return self.get_report(report_code, country_code)
            else:
                response.raise_for_status()
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise
        
    def fetch_reports(self, country_code, report_codes):
        if not self.is_token_valid():
            self.get_token()

        merged_report = ""
        for code in report_codes:
            response = None  # Initialize the response variable
            try:
                url = self.get_report(code, country_code)
                headers = {
                    'x-api-key': self.x_api_key,
                    'Authorization': f'Bearer {self.token}'
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                merged_report += response.json()['articleAsNinjs']['body_html']
            except requests.exceptions.HTTPError as http_err:
                if response and response.status_code == 401:
                    self.token = self.get_token()
                    print("Token expired, getting new token", self.token)
                    # Retry the current report code after refreshing the token
                    return self.fetch_reports(country_code, report_codes)
                else:
                    print(f"HTTP error occurred: {http_err}")
                    if response:
                        response.raise_for_status()
            except Exception as err:
                print(f"Other error occurred: {err}")
                raise

        return merged_report
    
    def get_eiu_views(self, country_code, industry):
        if not self.is_token_valid():
            self.get_token()

        url = endpoints.BASE_URL + endpoints.REPORT_ENDPOINTS["views"] + f"/{country_code}"
        headers = {
            'x-api-key': self.x_api_key,
            'Authorization': f'Bearer {self.token}'
        }
        params = {
            "industry": "true"
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            eiu_views = response.json()['eiuViews']
            filtered_views = [view['eiuViewHtml'] for view in eiu_views if view['metadataName'] in ["Essential", industry]]
            filtered_views_string = ''.join(filtered_views)
            return filtered_views_string
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                self.token = self.get_token()
                return self.get_eiu_views(country_code, industry)
            else:
                response.raise_for_status()
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise