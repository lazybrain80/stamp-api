from google.oauth2 import id_token
from google.auth.transport import requests
from config import auth_config

google_client_id = auth_config['google']['CLIENT_ID']

def verify_google_token(token: str):
    try:
        return id_token.verify_oauth2_token(token, requests.Request(), google_client_id)
    except Exception as e:
        print(e)
        return None