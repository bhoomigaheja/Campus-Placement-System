import json
import urllib.request
from django.core.mail.backends.base import BaseEmailBackend

class GoogleScriptBackend(BaseEmailBackend):
    def __init__(self, script_url=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        from django.conf import settings
        self.script_url = script_url or getattr(settings, 'GOOGLE_SCRIPT_URL', None)

    def send_messages(self, email_messages):
        if not email_messages or not self.script_url:
            return 0
        
        sent_count = 0
        for message in email_messages:
            try:
                for recipient in message.to:
                    data = {
                        'to': recipient,
                        'subject': message.subject,
                        'htmlBody': getattr(message, 'alternatives', [(message.body,)])[0][0] if hasattr(message, 'alternatives') and message.alternatives else message.body
                    }
                    
                    req = urllib.request.Request(
                        self.script_url, 
                        data=json.dumps(data).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    urllib.request.urlopen(req, timeout=10)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return sent_count
