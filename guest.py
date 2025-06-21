import redis
import json
import random
import uuid
from common import EventInvitation, GuestResponse, ResponseType
import os
from dotenv import load_dotenv

load_dotenv()

class EventGuest:
    def __init__(self, guest_id: str):
        self.guest_id = guest_id
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe("guest_invitations")
    
    def start(self):
        print(f"Guest {self.guest_id} started. Listening for invitations...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    invitation = EventInvitation.parse_raw(message['data'])
                    self._handle_invitation(invitation)
                except Exception as e:
                    print(f"Error processing invitation: {e}")
    
    def _handle_invitation(self, invitation: EventInvitation):
        print(f"\nReceived invitation for event: {invitation.event_name}")
        print(f"Date: {invitation.event_date}")
        print(f"Location: {invitation.location}")
        print(f"Description: {invitation.description}")
        response = self._make_decision(invitation)
        self._send_response(invitation.event_id, response)
    
    def _make_decision(self, invitation: EventInvitation) -> ResponseType:
        decision = random.choice(list(ResponseType))
        print(f"Decision made: {decision}")
        return decision
    
    def _send_response(self, event_id: str, response: ResponseType):
        guest_response = GuestResponse(
            event_id=event_id,
            guest_id=self.guest_id,
            response=response,
            message=f"Guest {self.guest_id} has responded with {response}"
        )
        
        self.redis_client.publish(
            "guest_responses",
            guest_response.json()
        )
        print(f"Sent response: {response}")

if __name__ == "__main__":
    guests = [
        EventGuest(f"guest_{i}") for i in range(1, 4)
    ]
    
    # Start all guests
    for guest in guests:
        guest.start() 