import pandas as pd 
import requests
import datetime


class swordfishAPI(): 
    def __init__(self, master=None, **kw):
        self.master = master  # master is optional, default is None
        super().__init__(**kw)

        credentials = {
            "sf_username": "API_User",
            "sf_password": "API_User@"
        }

        # The URL endpoint for the API login
        url = "https://mylaw.swordfish.co.za/api/login/"

        # Perform a POST request to the API
        response = requests.post(url, data=credentials)

        if response.status_code == 200:
            # Assuming 'response' is a JSON object and it has a 'data' field with the PHPSESSID
            data = response.json()
            phpsessid = data.get('data')

            # Use 'requests' Session object if you want to persist cookies across requests
            self.session = requests.Session()
            self.cookie_obj = requests.cookies.create_cookie(domain='.swordfish.co.za', name='PHPSESSID', value=phpsessid)
            self.session.cookies.set_cookie(self.cookie_obj)

    def _debtorExists(self, ID):
        data = {
            "id_num": ID
        }
        debtorExists = self.session.get("https://mylaw.swordfish.co.za/api/debtors/", params=data)

        debtorData = debtorExists.json()

        if debtorData.get("code") == "200":

            data = debtorData.get("data")[0]

            print(data)

            debtorID = data['debtor_id']

            accounts = data.get("accounts")

            print("debtorExists", True, debtorID, accounts)

            return True, debtorID, accounts

        else:
            print("debtorExists", debtorExists.json())
            return False, 0 ,0

    def _importDebtor(self,row):
        debtor = {
                "id_num": row.get("IDnumber"),
                "first_name": row.get("first_name"),
                "surname": row.get("surname"),
                "title": row.get("title"),
                "initials": row.get("initials"),
                "gender": row.get("gender"),
                "cell_phone_1": row.get("cell_phone_1"),
                "cell_phone_2": row.get("cell_phone_2"),
                "cell_phone_3": row.get("cell_phone_3"),
                "cell_phone_4": row.get("cell_phone_4"),
                "email_address_1": row.get("email_address_1"),
                "email_address_2": row.get("email_address_2"),
                "email_address_3": row.get("email_address_3"),
                "street_address_1": row.get("street_address_1"),
                "street_address_2": row.get("street_address_2"),
                "street_address_3": row.get("street_address_3"),
                "street_address_4": row.get("street_address_4"),
                "street_code": row.get("street_code"),
                "occupation": row.get("st_Debtooccupationr_Occupation"),
                "marital_status": row.get("marital_status")
                }
        

        debtorResponse = self.session.post("https://mylaw.swordfish.co.za/api/debtors/", data=debtor)

        if debtorResponse.status_code == "201":
            debtorData = debtorResponse.json()

            data = debtorData.get("data")
            print ("debtor",data)

            return data.get("debtor_id")

        else:

            print (debtorResponse.json())
            return False
        
    def _importAccount(self,row,debtorID):
        Account = {
                "debtor_id": debtorID,
                "client_id": row.get("client_id"),
                "handover_amount": row.get("handover_amount"),
                "interest_rate": "18",
                # Assuming DebtorInfo.get("Created_Time") returns a string with a 'T' present
                "interest_date": datetime.date.today(),
                # "legal_portion": "0",
                # "capital_portion": row.get("capital_portion"),
                # "interest_portion": row.get("interest_portion"),
                "type": row.get("type"),
                "client_reference": row.get("client_reference"),
                "date_of_default": row.get("date_of_default"),  # Corrected the spelling from "Deafult" to "Default"
                "last_payment_amount": row.get("last_payment_amount"),
                "sub_status": "2"
            }

        accountResponse = self.session.post("https://mylaw.swordfish.co.za/api/accounts/", data=Account)

        print(accountResponse.json())

        if accountResponse.status_code == "201":
            debtorData = accountResponse.json()

            data = debtorData.get("data")

            accountID = data.get("account_id")


            return data, accountID

        else:
            print(accountResponse.json())
            return {}, ""
        
    def writeoffAccount(self, accounts):
        accountsWR = []
        print
        for account in accounts:
            account_id = account["account_id"]
            client_debtor_id = account["client_debtor_id"]
  
            if client_debtor_id.startswith("EEE"):

                data = {
                            "account_id": account_id,
                            "function": "writeoff",
                            "status": 2,  # Status code for 'Written-Off Other'
                            "use_last_payment_date": 0,
                            "date": datetime.datetime.now(),  # Fill in if necessary
                            "reason": "Setteled with client"
                        }
                
                wr = self.session.put("https://mylaw.swordfish.co.za/api/accounts/", data=data)
                print(wr.json())
                if wr.status_code == "200":
                    accountsWR.append(client_debtor_id)
                    print(wr.json())


            print(client_debtor_id)

    def _importExpenses(self,accountID):
        Expens = {
                            "account_id": accountID,
                            "description": "Collection Cost",
                            "cost": 1023,
                            "date": datetime.date.today(),
                            "feeexpense": 0,
                            "comments": "Collection Cost"
                        }
        ExpensResponse = self.session.post("https://mylaw.swordfish.co.za/api/expenses/", data=Expens)

        print("Expense", ExpensResponse.json())
    
    def importAccounts(self, df):
        for index, row in df.iterrows():

            # Check if debtor exists
            bDebtor,  debtorID, accounts = self._debtorExists(row["IDnumber"])
            
            if bDebtor: 
                # if debtor exists then writeoff account
                bAccount = self.writeoffAccount(accounts)
            else:
                #  if debtor does not exist then create debotr
                debtorID = self._importDebtor(row)


            Account, accountID = self._importAccount(row, debtorID)
            
      

            Expens = self._importExpenses(accountID)

df = pd.read_excel("MylawSA\\Files\\20231115 Loans Handover Client Import.xlsx",sheet_name = 0)
api = swordfishAPI()

api.importAccounts(df)
