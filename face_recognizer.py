# face_recognizer.py
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

import face_recognition
import cv2
import pickle
import sqlite3
import numpy as np
from datetime import datetime
import os
from config import config

class FaceRecognizer:
    def __init__(self, db_path=None, model_path=None):
        self.db_path = db_path or config.DB_PATH
        self.model_path = model_path or config.MODEL_PATH
        self.known_encodings = []
        self.known_names = []
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        
        # Carregar modelo se existir
        self.load_model()
    
    def load_model(self):
        """Carregar modelo treinado"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.known_encodings = model_data['encodings']
                    self.known_names = model_data['names']
                print(f"✅ Modelo carregado: {len(self.known_encodings)} encodings")
                return True
            except Exception as e:
                print(f"❌ Erro ao carregar modelo: {e}")
        
        print("⚠️ Modelo não encontrado. Execute o treino primeiro.")
        return False
    
    def recognize_face_in_image(self, image_path):
        """Reconhecer face numa imagem"""
        if not self.known_encodings:
            return None, 0.0, "Modelo não carregado"
        
        try:
            # Carregar imagem
            image = face_recognition.load_image_file(image_path)
            
            # Detectar faces
            face_locations = face_recognition.face_locations(image, model="hog")
            if not face_locations:
                return None, 0.0, "Nenhuma face detectada"
            
            # Obter encodings das faces detectadas
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                return None, 0.0, "Não foi possível extrair features da face"
            
            # Usar primeira face detectada
            face_encoding = face_encodings[0]
            face_location = face_locations[0]
            
            # Comparar com faces conhecidas
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            min_distance = np.min(face_distances)
            confidence = 1 - min_distance
            
            if confidence > self.confidence_threshold:
                best_match_index = np.argmin(face_distances)
                name = self.known_names[best_match_index]
                return name, confidence, f"Face reconhecida: {name}"
            else:
                return "Desconhecido", confidence, f"Face detectada mas não reconhecida (confiança: {confidence:.2f})"
        
        except Exception as e:
            return None, 0.0, f"Erro no processamento: {str(e)}"
    
    def save_detection(self, image_path, detected_name, confidence, status_message):
        """Salvar detecção na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Encontrar ID da pessoa se conhecida
        person_id = None
        if detected_name and detected_name != "Desconhecido":
            cursor.execute("SELECT id FROM people WHERE name = ?", (detected_name,))
            result = cursor.fetchone()
            if result:
                person_id = result[0]
        
        # Inserir detecção
        cursor.execute("""
            INSERT INTO detections (image_path, detected_person_id, detected_name, confidence_score)
            VALUES (?, ?, ?, ?)
        """, (image_path, person_id, detected_name, confidence))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"💾 Detecção salva (ID: {detection_id})")
        return detection_id

if __name__ == "__main__":
    # Teste básico
    recognizer = FaceRecognizer()
    
    test_image = "test_images/test.jpg"  # Colocar uma foto aqui para testar
    if os.path.exists(test_image):
        name, confidence, message = recognizer.recognize_face_in_image(test_image)
        print(f"Resultado: {name} (confiança: {confidence:.2f})")
        print(f"Mensagem: {message}")
        
        if name:
            recognizer.save_detection(test_image, name, confidence, message)
    else:
        print(f"Coloque uma foto em {test_image} para testar")