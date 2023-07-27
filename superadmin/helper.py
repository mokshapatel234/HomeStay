import os
import requests

server_key = os.getenv('SERVER_KEY')

def send_push_notification(receivers,message,title):
    try:
        for receiver in receivers:
            payload = {
                "to":receiver,
                "notification": {
                "title": title,
                "body": message,
                "content_available" : True,
                "sound":"default"
                },
                "priority" : "high"
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"key={server_key}"
            }

            try: 
                response = requests.post('https://fcm.googleapis.com/fcm/send',json=payload,headers=headers,)
            except Exception as e:
                pass
    except Exception as e:
        pass
