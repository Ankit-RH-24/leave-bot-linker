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
        data = json.loads(post_data.decode('utf-8'))
        
        # Handle Slack URL verification challenge
        if 'challenge' in data:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'challenge': data['challenge']}).encode())
            return
        
        # Handle Slack events
        if 'event' in data:
            event = data['event']
            
            # Ignore bot messages to prevent loops
            if event.get('bot_id'):
                self.send_response(200)
                self.end_headers()
                return
            
            # Process the message
            if event['type'] == 'message' or event['type'] == 'app_mention':
                message_text = event.get('text', '').lower()
                user_id = event.get('user')
                channel = event.get('channel')
                
                # Identify request type
                request_type = self.identify_request_type(message_text)
                
                if request_type:
                    # Send response back to Slack
                    response_message = self.generate_response(request_type, user_id)
                    self.send_slack_message(channel, response_message)
        
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
        except Exception as e:
            print(f"Error sending message to Slack: {e}")
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Slack Leave Bot is running!')

