import pandas as pd 
import requests


df = pd.read_csv("")

# Your credentials
credentials = {
    "sf_username": "API_User",
    "sf_password": "API_User@"
}

# The URL endpoint for the API login
url = "https://mylaw.swordfish.co.za/api/login/"

# Perform a POST request to the API
response = requests.post(url, data=credentials)

# Check if the request was successful
if response.status_code == 200:
    # Assuming 'response' is a JSON object and it has a 'data' field with the PHPSESSID
    data = response.json()
    phpsessid = data.get('data')

    # Use 'requests' Session object if you want to persist cookies across requests
    session = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.swordfish.co.za', name='PHPSESSID', value=phpsessid)
    session.cookies.set_cookie(cookie_obj)

    # Now you can use 'session' to make subsequent requests that will use the cookie
    # session.get('some_protected_url')

    for index, row in df.iterrows():
        

else:
    print("Failed to log in:", response.text)
