# main_processor.py
#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from face_recognizer import FaceRecognizer
from ha_integration import HomeAssistantIntegration

# Configurações
HA_URL = "http://192.168.1.88:8123"  # !! ALTERAR para IP do HA
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzODUzY2EzZjc3ZTE0YTdhYWQ2ZjllODhlNGUzNGFhZiIsImlhdCI6MTc1Njg1Mjc4MiwiZXhwIjoyMDcyMjEyNzgyfQ.7QI-xc1dbHdO-ZnrTX_Jb7j9m23g1CICEU8IwEx3RTY"
TEST_IMAGE_PATH = "test_images/nelson_test.jpg"
NEST_HUB_ENTITY = "media_player.hub"  # !! VERIFICAR nome correto

class FaceRecognitionSystem:
    def __init__(self):
        self.recognizer = FaceRecognizer()
        self.ha = HomeAssistantIntegration(HA_URL, HA_TOKEN)
        
        # Verificar se modelo está carregado
        if not self.recognizer.known_encodings:
            print("❌ Modelo não carregado! Execute o treino primeiro.")
            sys.exit(1)
    
    def process_image(self, image_path):
        """Processar uma imagem completa"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return
        
        print(f"🔍 Processando: {image_path}")
        
        # 1. Reconhecimento facial
        name, confidence, message = self.recognizer.recognize_face_in_image(image_path)
        
        print(f"Resultado: {name} (confiança: {confidence:.2f})")
        print(f"Status: {message}")
        
        # 2. Salvar detecção
        detection_id = self.recognizer.save_detection(image_path, name, confidence, message)
        
        # 3. Gerar saudação
        greeting = self.ha.get_greeting_message(name)
        
        # 4. Falar no Nest Hub
        success = self.ha.speak_on_nest_hub(greeting, NEST_HUB_ENTITY)
        
        # 5. Notificação HA
        if success:
            self.ha.send_notification(
                "Face Recognition", 
                f"Detectado: {name} (confiança: {confidence:.2f})"
            )
        
        print(f"🎤 Saudação: '{greeting}'")
        print(f"📱 Nest Hub TTS: {'✅ OK' if success else '❌ Falhou'}")
        
        return {
            'name': name,
            'confidence': confidence,
            'message': message,
            'greeting': greeting,
            'tts_success': success,
            'detection_id': detection_id
        }
    
    def process_test_image(self):
        """Processar imagem de teste"""
        return self.process_image(TEST_IMAGE_PATH)

if __name__ == "__main__":
    print("🎯 Sistema de Reconhecimento Facial")
    print("==================================")
    
    system = FaceRecognitionSystem()
    
    if len(sys.argv) > 1:
        # Processar imagem específica
        image_path = sys.argv[1]
        system.process_image(image_path)
    else:
        # Processar imagem de teste
        system.process_test_image()