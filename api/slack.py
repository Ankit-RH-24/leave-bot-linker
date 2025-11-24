import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse the incoming data
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_response(400)
            self.end_headers()
            return
        
        # Handle Slack URL verification challenge
        if 'challenge' in data:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'challenge': data['challenge']}).encode())
            return
        
        # Handle event_callback wrapper (Slack sends events wrapped in this)
        if 'event' in data:
            # Respond immediately to Slack (within 3 seconds)
            self.send_response(200)
            self.end_headers()
            
            event = data['event']
            event_type = event.get('type')
            
            # Ignore bot messages to prevent loops
            if event.get('bot_id'):
                return
            
            # Ignore message subtypes (edited, deleted, etc.)
            if event.get('subtype'):
                return
            
            # Process the message
            if event_type == 'message' or event_type == 'app_mention':
                message_text = event.get('text', '').lower()
                user_id = event.get('user')
                channel = event.get('channel')
                
                # Skip if no user or channel
                if not user_id or not channel:
                    return
                
                # Identify request type
                request_type = self.identify_request_type(message_text)
                
                if request_type:
                    # Send response back to Slack
                    response_message = self.generate_response(request_type, user_id)
                    self.send_slack_message(channel, response_message)
        else:
            # Respond to other events (like event_callback wrapper)
            self.send_response(200)
            self.end_headers()
    
    def identify_request_type(self, message):
        """
        Identify if the message is about leave or WFH
        Returns: 'leave', 'wfh', or None
        """
        # Keywords for leave
        leave_keywords = [
            'leave', 'off', 'vacation', 'holiday', 'absent', 
            'sick', 'medical', 'emergency', 'pto', 'time off',
            'not coming', 'won\'t be in', 'taking off'
        ]
        
        # Keywords for WFH
        wfh_keywords = [
            'wfh', 'work from home', 'working from home', 
            'remote', 'home office', 'working remotely'
        ]
        
        # Check for WFH first (more specific)
        for keyword in wfh_keywords:
            if keyword in message:
                return 'wfh'
        
        # Check for leave
        for keyword in leave_keywords:
            if keyword in message:
                return 'leave'
        
        return None
    
    def generate_response(self, request_type, user_id):
        """
        Generate appropriate response based on request type
        """
        # Replace this with your actual form link
        form_link = os.environ.get('FORM_LINK', 'https://your-form-link.com')
        
        if request_type == 'leave':
            message = f"Hi <@{user_id}>! 👋\n\n"
            message += "I see you're requesting a leave. Please fill out the form below:\n"
            message += f"📝 *Leave Request Form:* {form_link}\n\n"
            message += "Make sure to fill in all the required details. Have a great day! 🌴"
        
        elif request_type == 'wfh':
            message = f"Hi <@{user_id}>! 👋\n\n"
            message += "I see you're planning to work from home. Please fill out the form below:\n"
            message += f"🏠 *WFH Request Form:* {form_link}\n\n"
            message += "Make sure to fill in all the required details. Happy remote working! 💻"
        
        else:
            message = f"Hi <@{user_id}>! 👋\n\n"
            message += "I'm here to help with leave and WFH requests!\n"
            message += f"Please fill out the form: {form_link}"
        
        return message
    
    def send_slack_message(self, channel, message):
        """
        Send message back to Slack using Web API
        """
        import requests
        
        slack_token = os.environ.get('SLACK_BOT_TOKEN')
        
        if not slack_token:
            print("Error: SLACK_BOT_TOKEN not found")
            return
        
        url = 'https://slack.com/api/chat.postMessage'
        headers = {
            'Authorization': f'Bearer {slack_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'channel': channel,
            'text': message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if not result.get('ok'):
                print(f"Slack API error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error sending message to Slack: {e}")
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Slack Leave Bot is running!')

