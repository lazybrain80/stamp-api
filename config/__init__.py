import os
import json

def get_mode():
    m = os.environ.get("RUN_MODE")
    if m not in ["dev", "prod"]:
        return "dev"
    return m

class Config:
    def __init__(self, config_file):
        with open(os.path.join("config", config_file), 'r') as file:
            config_data = json.load(file)
            self.postgres = config_data.get('postgres', {})
            self.mongodb = config_data.get('mongodb', {})
            self.auth = config_data.get('auth', {})
            self.basic_lic = config_data.get('basic-license', {})
            self.cloudinary = config_data.get('cloudinary', {})

try:
    mode = get_mode()
    config = Config(f'config.{mode}.json')
except Exception as e:
    print("config parsing error", e)

mongo_config = config.mongodb
auth_config = config.auth
basic_license = config.basic_lic
cloudinary_config = config.cloudinary
