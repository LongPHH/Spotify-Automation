import requests
import base64

# simple script to get spotify API token


# Dummy values. to be replaced with real client id and secret
client_id = "dfsdfdsfsdf"
client_secret = "sdfsdfsdf"

client_creds = f"{client_id}:{client_secret}"
client_creds_64 = base64.b64encode(client_creds.encode())  # encode it to based 64

token_url = "https://accounts.spotify.com/api/token"
method = "POST"


token_data = {"grant_type": "client_credentials"}
token_headers = {"Authorization": f"Basic {client_creds_64.decode()}"}

r = requests.post(token_url, data=token_data, headers=token_headers)

print(r.json())         # token to be use for spotify API


