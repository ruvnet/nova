import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv("e2b-agent/.env")

# Try to import Slack SDK, but don't fail if not available
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    WebClient = None
    SlackApiError = Exception

class CommsAgent(BaseAgent):
    """Agent for handling communications via Slack and email"""
    def __init__(self, name: str = "CommsAgent"):
        super().__init__(name=name)
        
    def run(self, method: str, message: str = "") -> str:
        """Execute communication operation"""
        try:
            if not method:
                raise ValueError("Communication method is required")
                
            if method == "slack":
                if not SLACK_AVAILABLE:
                    raise RuntimeError("Slack SDK not installed. Run: pip install slack-sdk")
                return self._send_slack_message(message)
            elif method == "email":
                return self._send_email(message)
            else:
                raise ValueError(f"Unknown communication method: {method}")
                
        except Exception as e:
            self.log(f"Error executing operation: {str(e)}")
            return ""
            
    def _send_slack_message(self, message: str) -> str:
        """Send message via Slack"""
        if not message:
            raise ValueError("Message is required for Slack")
            
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        if not slack_token:
            raise RuntimeError("SLACK_BOT_TOKEN not set")
            
        try:
            client = WebClient(token=slack_token)
            response = client.chat_postMessage(
                channel="#general",  # Default channel
                text=message
            )
            return f"Message sent to Slack (ts: {response['ts']})"
            
        except SlackApiError as e:
            raise RuntimeError(f"Slack error: {e.response['error']}")
            
    def _send_email(self, message: str) -> str:
        """Send message via email"""
        if not message:
            raise ValueError("Message is required for email")
            
        smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        smtp_user = os.getenv("EMAIL_SMTP_USER")
        smtp_pass = os.getenv("EMAIL_SMTP_PASS")
        recipient = os.getenv("EMAIL_RECIPIENT")
        
        if not all([smtp_server, smtp_user, smtp_pass, recipient]):
            raise RuntimeError("Email configuration missing")
            
        try:
            msg = MIMEText(message)
            msg["Subject"] = "Message from CommsAgent"
            msg["From"] = smtp_user
            msg["To"] = recipient
            
            with smtplib.SMTP(smtp_server, 587) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [recipient], msg.as_string())
                
            return "Email sent successfully"
            
        except Exception as e:
            raise RuntimeError(f"Email error: {str(e)}")

def handle_communication(method: str, message: str = "") -> bool:
    """Handle communication request"""
    try:
        agent = CommsAgent()
        result = agent.run(method=method, message=message)
        if result:
            agent.log(result)
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] Communication failed: {str(e)}")
        return False