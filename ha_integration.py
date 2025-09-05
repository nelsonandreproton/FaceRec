# ha_integration.py
import requests
import json
from datetime import datetime

class HomeAssistantIntegration:
    def __init__(self, ha_url, ha_token=None):
        self.ha_url = ha_url.rstrip('/')
        self.ha_token = ha_token
        self.headers = {
            'Authorization': f'Bearer {ha_token}' if ha_token else None,
            'Content-Type': 'application/json',
        }
    
    def speak_on_nest_hub(self, message, entity_id="media_player.hub"):
        """Falar mensagem no Nest Hub via TTS"""
        url = f"{self.ha_url}/api/services/tts/speak"
        
        data = {
            "entity_id": "tts.google_translate_en_com",
            "media_player_entity_id": entity_id,
            "message": message,
            "language": "pt",
            "cache": True
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"🔊 Mensagem enviada para Nest Hub: '{message}'")
                return True
            else:
                print(f"❌ Erro TTS: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro ao contactar HA: {e}")
            return False
    
    def send_notification(self, title, message):
        """Enviar notificação para HA"""
        url = f"{self.ha_url}/api/services/notify/persistent_notification"
        
        data = {
            "title": title,
            "message": message
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code == 200
        except:
            return False
    
    def get_greeting_message(self, person_name):
        """Gerar mensagem de saudação"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Bom dia"
        elif 12 <= hour < 18:
            greeting = "Boa tarde"
        else:
            greeting = "Boa noite"
        
        if person_name and person_name != "Desconhecido":
            return f"{greeting}, {person_name}!"
        else:
            return f"{greeting}! Não te reconheço."