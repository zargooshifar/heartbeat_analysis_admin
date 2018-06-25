import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("heartbeatanalysis-keys.json")
app = firebase_admin.initialize_app(cred)
print(app.name)
