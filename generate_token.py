from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    SCOPES
)

# FORCE Google to prompt for consent and return a refresh token
creds = flow.run_local_server(
    port=0, 
    authorization_prompt_message="Please visit this URL to authorize this application: {url}",
    prompt="consent"  # <-- CRITICAL: This forces Google to provide a new refresh_token
)

print("\n=== COPY THESE ===")
print("GMAIL_CLIENT_ID=",creds.client_id)
print("GMAIL_CLIENT_SECRET=",creds.client_secret)
print("GMAIL_REFRESH_TOKEN=",creds.refresh_token) # This will no longer be None!