import redis
import json
import time
from typing import Dict, List
from common import EventInvitation, GuestResponse, EventSummary, ResponseType
import os
from dotenv import load_dotenv

load_dotenv()

class EventCoordinator:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe("event_invitations")
        self.pubsub.subscribe("guest_responses")
        self.event_responses: Dict[str, List[GuestResponse]] = {}
        self.event_details: Dict[str, EventInvitation] = {}
        
    def start(self):
        print("Coordinator started. Listening for invitations and responses...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    if message['channel'] == 'event_invitations':
                        self._handle_invitation(message['data'])
                    elif message['channel'] == 'guest_responses':
                        self._handle_response(message['data'])
                except Exception as e:
                    print(f"Error processing message: {e}")
    
    def _handle_invitation(self, data: str):
        invitation = EventInvitation.parse_raw(data)
        self.event_details[invitation.event_id] = invitation
        self.event_responses[invitation.event_id] = []
        self.redis_client.publish(
            "guest_invitations",
            data
        )
        print(f"Forwarded invitation for event: {invitation.event_name}")
    
    def _handle_response(self, data: str):
        response = GuestResponse.parse_raw(data)
        event_id = response.event_id
        
        if event_id not in self.event_responses:
            print(f"Received response for unknown event: {event_id}")
            return
        
        self.event_responses[event_id].append(response)
        print(f"Received response from guest {response.guest_id} for event {event_id}")
        time.sleep(3)
        self._send_summary(event_id)
    
    def _send_summary(self, event_id: str):
        if event_id not in self.event_details:
            return
        
        invitation = self.event_details[event_id]
        responses = self.event_responses[event_id]
        
        summary = EventSummary(
            event_id=event_id,
            host_id=invitation.host_id,
            event_name=invitation.event_name,
            event_date=invitation.event_date,
            responses=responses
        )
        
        # Send summary to host
        self.redis_client.publish(
            f"event_summary_{invitation.host_id}",
            summary.json()
        )
        print(f"Sent summary for event {invitation.event_name} to host {invitation.host_id}")

if __name__ == "__main__":
    coordinator = EventCoordinator()
    coordinator.start() 