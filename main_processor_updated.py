#!/usr/bin/env python3
# main_processor_updated.py
import os
import sys
import time
import shutil
from datetime import datetime
from face_recognizer import FaceRecognizer
from ha_integration import HomeAssistantIntegration

# Tentar importar configurações
try:
    from config import *
except ImportError:
    # Configurações padrão se config.py não existir
    HA_URL = "http://192.168.1.88:8123"
    HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzODUzY2EzZjc3ZTE0YTdhYWQ2ZjllODhlNGUzNGFhZiIsImlhdCI6MTc1Njg1Mjc4MiwiZXhwIjoyMDcyMjEyNzgyfQ.7QI-xc1dbHdO-ZnrTX_Jb7j9m23g1CICEU8IwEx3RTY"
    TEST_IMAGE_PATH = "test_images/nelson_test.jpg"
    NEST_HUB_ENTITY = "media_player.hub"
    IMAGES_BASE_PATH = "test_images"

class FaceRecognitionSystem:
    def __init__(self, auto_save_images=True):
        self.recognizer = FaceRecognizer()
        self.ha = HomeAssistantIntegration(HA_URL, HA_TOKEN)
        self.auto_save_images = auto_save_images
        
        # Verificar se modelo está carregado
        if not self.recognizer.known_encodings:
            print("❌ Modelo não carregado! Execute o treino primeiro.")
            print("   python train_model.py")
            sys.exit(1)
        
        # Criar pasta de imagens se não existir
        os.makedirs(IMAGES_BASE_PATH, exist_ok=True)
    
    def save_image_for_validation(self, image_path):
        """Copiar imagem para pasta de validação com nome único"""
        if not os.path.exists(image_path):
            return image_path
        
        # Gerar nome único baseado em timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        
        new_filename = f"{timestamp}_{name}{ext}"
        new_path = os.path.join(IMAGES_BASE_PATH, new_filename)
        
        try:
            # Copiar imagem para pasta de validação
            shutil.copy2(image_path, new_path)
            print(f"📁 Imagem copiada para: {new_path}")
            return new_filename  # Retornar apenas o nome do arquivo
        except Exception as e:
            print(f"⚠️ Erro ao copiar imagem: {e}")
            return os.path.basename(image_path)
    
    def process_image(self, image_path, save_detection=True):
        """Processar uma imagem completa"""
        if not os.path.exists(image_path):
            print(f"❌ Imagem não encontrada: {image_path}")
            return None
        
        print(f"🔍 Processando: {image_path}")
        
        # 1. Reconhecimento facial
        name, confidence, message = self.recognizer.recognize_face_in_image(image_path)
        
        print(f"Resultado: {name} (confiança: {confidence:.2f})")
        print(f"Status: {message}")
        
        # 2. Preparar caminho da imagem para validação
        if self.auto_save_images and save_detection:
            saved_image_path = self.save_image_for_validation(image_path)
        else:
            saved_image_path = os.path.basename(image_path)
        
        # 3. Salvar detecção na base de dados
        detection_id = None
        if save_detection:
            detection_id = self.recognizer.save_detection(
                saved_image_path, name, confidence, message
            )
        
        # 4. Gerar saudação
        greeting = self.ha.get_greeting_message(name)
        
        # 5. Falar no Nest Hub (se configurado)
        tts_success = False
        if HA_TOKEN and HA_TOKEN != "seu_token_aqui":
            tts_success = self.ha.speak_on_nest_hub(greeting, NEST_HUB_ENTITY)
            
            # 6. Notificação HA
            if tts_success:
                self.ha.send_notification(
                    "Face Recognition", 
                    f"Detectado: {name} (confiança: {confidence:.2f})"
                )
        else:
            print("⚠️ Token HA não configurado - TTS desabilitado")
        
        print(f"🎤 Saudação: '{greeting}'")
        print(f"📱 Nest Hub TTS: {'✅ OK' if tts_success else '❌ Falhou'}")
        
        if save_detection:
            print(f"💾 Detecção salva (ID: {detection_id}) - Validar em: http://localhost:5000")
        
        return {
            'name': name,
            'confidence': confidence,
            'message': message,
            'greeting': greeting,
            'tts_success': tts_success,
            'detection_id': detection_id,
            'saved_image_path': saved_image_path
        }
    
    def process_test_image(self):
        """Processar imagem de teste"""
        if os.path.exists(TEST_IMAGE_PATH):
            return self.process_image(TEST_IMAGE_PATH)
        else:
            print(f"❌ Imagem de teste não encontrada: {TEST_IMAGE_PATH}")
            print("   Coloque uma foto neste caminho para testar")
            return None
    
    def process_directory(self, directory_path):
        """Processar todas as imagens de um diretório"""
        if not os.path.exists(directory_path):
            print(f"❌ Diretório não encontrado: {directory_path}")
            return []
        
        results = []
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        
        print(f"📁 Processando diretório: {directory_path}")
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(image_extensions):
                image_path = os.path.join(directory_path, filename)
                print(f"\n➡️ Processando: {filename}")
                
                result = self.process_image(image_path)
                if result:
                    results.append(result)
                
                # Pausa pequena entre processamentos
                time.sleep(0.5)
        
        print(f"\n🎯 Processamento concluído: {len(results)} imagens processadas")
        return results
    
    def interactive_mode(self):
        """Modo interativo para testar diferentes imagens"""
        print("\n🎮 MODO INTERATIVO")
        print("=================")
        print("Comandos:")
        print("  test - processar imagem de teste")
        print("  <caminho> - processar imagem específica")
        print("  dir <pasta> - processar diretório")
        print("  stats - mostrar estatísticas")
        print("  quit - sair")
        
        while True:
            try:
                command = input("\n📷 Digite comando: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                    
                elif command.lower() == 'test':
                    self.process_test_image()
                    
                elif command.lower() == 'stats':
                    self.show_stats()
                    
                elif command.startswith('dir '):
                    directory = command[4:].strip()
                    self.process_directory(directory)
                    
                elif command:
                    # Tratar como caminho de imagem
                    self.process_image(command)
                    
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def show_stats(self):
        """Mostrar estatísticas do sistema"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.recognizer.db_path)
            cursor = conn.cursor()
            
            # Estatísticas básicas
            cursor.execute("SELECT COUNT(*) FROM detections")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM detections WHERE is_verified = TRUE")
            verified = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM people")
            people_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE processed = FALSE")
            pending_feedback = cursor.fetchone()[0]
            
            # Últimas detecções
            cursor.execute("""
                SELECT detected_name, confidence_score, timestamp 
                FROM detections 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            recent = cursor.fetchall()
            
            conn.close()
            
            print("\n📊 ESTATÍSTICAS DO SISTEMA")
            print("=" * 30)
            print(f"👥 Pessoas conhecidas: {people_count}")
            print(f"🔍 Total de detecções: {total}")
            print(f"✅ Verificadas: {verified}")
            print(f"⏳ Pendentes: {total - verified}")
            print(f"🔄 Feedback pendente: {pending_feedback}")
            
            if recent:
                print("\n📷 Últimas detecções:")
                for detection in recent:
                    name = detection[0] or "Desconhecido"
                    conf = detection[1] or 0
                    timestamp = detection[2]
                    print(f"  • {name} ({conf:.2f}) - {timestamp}")
            
            print(f"\n🌐 Interface web: http://localhost:5000")
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")

def main():
    print("🎯 Sistema de Reconhecimento Facial")
    print("==================================")
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        system = FaceRecognitionSystem()
        
        if arg == "--interactive" or arg == "-i":
            # Modo interativo
            system.interactive_mode()
            
        elif arg == "--directory" or arg == "-d":
            # Processar diretório
            if len(sys.argv) > 2:
                directory = sys.argv[2]
                system.process_directory(directory)
            else:
                print("❌ Especifique o diretório: python main_processor.py -d pasta/")
                
        elif arg == "--stats" or arg == "-s":
            # Mostrar estatísticas
            system = FaceRecognitionSystem()
            system.show_stats()
            
        elif arg == "--help" or arg == "-h":
            # Ajuda
            print("\nUso:")
            print("  python main_processor.py                    # Imagem de teste")
            print("  python main_processor.py <imagem>          # Imagem específica")
            print("  python main_processor.py -d <diretório>    # Processar diretório")
            print("  python main_processor.py -i               # Modo interativo")
            print("  python main_processor.py -s               # Estatísticas")
            print("  python main_processor.py -h               # Esta ajuda")
            print("\nInterface web:")
            print("  python web_validation.py                   # Abrir interface")
            
        else:
            # Processar imagem específica
            system.process_image(arg)
    
    else:
        # Processar imagem de teste padrão
        system = FaceRecognitionSystem()
        system.process_test_image()

if __name__ == "__main__":
    main()