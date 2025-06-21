import redis
import json
import uuid
from datetime import datetime, timedelta
from common import EventInvitation, EventSummary
import os
from dotenv import load_dotenv

load_dotenv()

class EventHost:
    def __init__(self, host_id: str):
        self.host_id = host_id
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(f"event_summary_{host_id}")
        
    def create_invitation(self, event_name: str, description: str, location: str, days_from_now: int = 7) -> str:
        event_id = str(uuid.uuid4())
        event_date = datetime.now() + timedelta(days=days_from_now)
        
        invitation = EventInvitation(
            event_id=event_id,
            host_id=self.host_id,
            event_name=event_name,
            event_date=event_date,
            description=description,
            location=location
        )
        
        self.redis_client.publish(
            "event_invitations",
            invitation.json()
        )
        print(f"Published invitation for event: {event_name}")
        return event_id
    
    def listen_for_summary(self):
        print(f"Host {self.host_id} listening for event summaries...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    summary_data = json.loads(message['data'])
                    summary = EventSummary(**summary_data)
                    self._handle_summary(summary)
                except Exception as e:
                    print(f"Error processing summary: {e}")
    
    def _handle_summary(self, summary: EventSummary):
        print("\n=== Event Summary ===")
        print(f"Event: {summary.event_name}")
        print(f"Date: {summary.event_date}")
        print("\nResponse Summary:")
        print(f"Total Invited: {summary.get_summary()['total_invited']}")
        print(f"Yes: {summary.get_summary()['yes_count']}")
        print(f"No: {summary.get_summary()['no_count']}")
        print(f"Maybe: {summary.get_summary()['maybe_count']}")
        print("\nDetailed Responses:")
        for response in summary.responses:
            print(f"Guest {response.guest_id}: {response.response}")
            if response.message:
                print(f"Message: {response.message}")
        print("===================\n")

def get_event_details():
    print("\n=== Create New Event ===")
    event_name = input("Enter event name: ")
    description = input("Enter event description: ")
    location = input("Enter event location: ")
    
    while True:
        try:
            days = int(input("Enter number of days from now for the event (default 7): ") or "7")
            if days < 0:
                print("Please enter a positive number of days")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    return event_name, description, location, days

if __name__ == "__main__":
    host = EventHost("host_1")
    
    while True:
        print("\nEvent Planning System")
        print("1. Create new event")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            event_name, description, location, days = get_event_details()
            event_id = host.create_invitation(
                event_name=event_name,
                description=description,
                location=location,
                days_from_now=days
            )
            print(f"\nEvent created successfully! Event ID: {event_id}")
            print("Waiting for guest responses...")
            host.listen_for_summary()
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.") 