import pandas as pd 
import requests


df = pd.read_excel("MylawSA\\Files\\20231115 Loans Handover Client Import.xlsx",sheet_name = 0)

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
    print(data)

    # Use 'requests' Session object if you want to persist cookies across requests
    session = requests.Session()
    cookie_obj = requests.cookies.create_cookie(domain='.swordfish.co.za', name='PHPSESSID', value=phpsessid)
    session.cookies.set_cookie(cookie_obj)

    # Now you can use 'session' to make subsequent requests that will use the cookie
    # session.get('some_protected_url')

    for index, row in df.iterrows():
        print(row)
        debtor = {
                "id_num": row.get("id_num"),
                "first_name": row.get("first_name"),
                "surname": row.get("Surname"),
                "title": row.get("Title"),
                "initials": row.get("st_Debtor_Initials"),
                "gender": row.get("st_Debtor_Gender"),
                "cell_phone_1": row.get("Mobile_Number"),
                "cell_phone_2": row.get("Secondary_Mobile_Number"),
                "cell_phone_3": row.get("Tertiary_Mobile_Number"),
                "cell_phone_4": row.get("st_Debtor_Quaternary_Mobile_Number"),
                "email_address_1": row.get("st_Debtor_Email"),
                "email_address_2": row.get("st_Debtor_Email_2"),
                "email_address_3": row.get("st_Debtor_Email_3"),
                "street_address_1": row.get("Current_Street_Name_and_House_Number"),
                "street_address_2": row.get("Living_Estate_or_Apartment_Complex"),
                "street_address_3": row.get("st_Debtor_Area"),
                "street_address_4": row.get("Current_City"),
                "street_code": row.get("st_Debtor_Postal_Code"),
                "occupation": row.get("st_Debtor_Occupation"),
                "marital_status": row.get("st_Debtor_Marital_Status")
                }
        

        debtorResponse = session.post("https://mylaw.swordfish.co.za/api/debtors/", data=debtor)
        
       
        if debtorResponse.status_code == "201":
            


            debtorData = debtorResponse.json()


            debtor = debtorData.get("data")

            print(debtorResponse.get("code"), "debtor imported",debtor.get("debtor_id") )
            # Create an Account dictionary with the necessary mappings
            Account = {
                "debtor_id": debtor.get("debtor_id"),
                "client_id": row.get("Handover_Amount"),
                "handover_amount": row.get("Handover_Amount"),
                "interest_rate": "18",
                # Assuming DebtorInfo.get("Created_Time") returns a string with a 'T' present
                "interest_date": row.get("Created_Time"),
                "legal_portion": "0",
                "capital_portion": row.get("Capital_Portion"),
                "interest_portion": row.get("Interest_Portion"),
                "type": row.get("Creditor_Type"),
                "client_reference": row.get("client_reference"),
                "date_of_default": row.get("Date_of_Default"),  # Corrected the spelling from "Deafult" to "Default"
                "last_payment_amount": row.get("Monthly_Amount"),
                "sub_status": "2"
            }

            accountResponse = session.post("https://mylaw.swordfish.co.za/api/accounts/", data=Account)
            
            

            if accountResponse.status_code == "Created":

                accountData = accountResponse.json()

                account = accountData.get("data")
                print(accountResponse.get("code"), "account imported", account.get("account_id"))
                Expens = {
                            "account_id": account.get("account_id"),
                            "description": "Collection Cost",
                            "cost": 1023,
                            "date": row.get("Created_Time"),
                            "feeexpense": 0,
                            "comments": "Collection Cost"
                        }
                ExpensResponse = session.post("https://mylaw.swordfish.co.za/api/accounts/", data=Expens)

        else: 
            print(debtorResponse)
            print(debtorResponse.json())


else:
    print("Failed to log in:", response.text)
