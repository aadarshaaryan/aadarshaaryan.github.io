from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

print("\n=== COPY THESE ===")
print("CLIENT_ID =", creds.client_id)
print("CLIENT_SECRET =", creds.client_secret)
print("REFRESH_TOKEN =", creds.refresh_token)