import os
import pickle
import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleCalendarAPI:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticate()

    def authenticate(self):
      
        creds = None
        
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                flow.redirect_uri = 'http://localhost:8080/oauth2callback'
                creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_upcoming_events(self, max_results=10):
      
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    def format_event(self, event):
       
        start = event['start'].get('dateTime', event['start'].get('date'))
        return f'{start} - {event["summary"]}'

    def print_upcoming_events(self, max_results=10):
       
        events = self.get_upcoming_events(max_results)
        
        if not events:
            print('No upcoming events found.')
            return
        
        for event in events:
            print(self.format_event(event))

# Example usage
if __name__ == '__main__':
    # Create an instance of the calendar API
    calendar = GoogleCalendarAPI()
    
    # Print upcoming events
    calendar.print_upcoming_events() 