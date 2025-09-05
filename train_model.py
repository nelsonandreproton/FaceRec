# train_model.py
import face_recognition
import pickle
import os
import sqlite3
import numpy as np
from datetime import datetime

class FaceTrainer:
    def __init__(self, db_path="face_recognition.db"):
        self.db_path = db_path
        self.known_encodings = []
        self.known_names = []
    
    def train_from_images(self, training_folder="training_images"):
        """Treinar modelo com imagens da pasta training_images"""
        if not os.path.exists(training_folder):
            print(f"❌ Pasta {training_folder} não existe!")
            return False
        
        print("🎯 Iniciando treino do modelo...")
        
        # Limpar dados anteriores
        self.known_encodings = []
        self.known_names = []
        
        # Processar cada pessoa
        for person_folder in os.listdir(training_folder):
            person_path = os.path.join(training_folder, person_folder)
            if not os.path.isdir(person_path):
                continue
                
            print(f"📸 Processando fotos de {person_folder}...")
            person_encodings = []
            
            # Processar cada foto da pessoa
            for image_file in os.listdir(person_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    image_path = os.path.join(person_path, image_file)
                    
                    try:
                        # Carregar e processar imagem
                        image = face_recognition.load_image_file(image_path)
                        face_encodings = face_recognition.face_encodings(image)
                        
                        if face_encodings:
                            person_encodings.append(face_encodings[0])
                            print(f"  ✅ {image_file} - Face detectada")
                        else:
                            print(f"  ⚠️ {image_file} - Nenhuma face encontrada")
                            
                    except Exception as e:
                        print(f"  ❌ {image_file} - Erro: {e}")
            
            # Adicionar pessoa ao modelo se tiver encodings
            if person_encodings:
                # Salvar na base de dados
                avg_encoding = np.mean(person_encodings, axis=0)
                self.save_person_to_db(person_folder, avg_encoding)
                
                # Adicionar ao modelo em memória
                self.known_encodings.extend(person_encodings)
                self.known_names.extend([person_folder] * len(person_encodings))
                
                print(f"  ✅ {person_folder}: {len(person_encodings)} encodings adicionados")
            else:
                print(f"  ❌ {person_folder}: Nenhuma face válida encontrada")
        
        # Salvar modelo
        if self.known_encodings:
            self.save_model()
            print(f"🎉 Treino concluído! {len(set(self.known_names))} pessoas, {len(self.known_encodings)} encodings")
            return True
        else:
            print("❌ Nenhuma face foi processada com sucesso!")
            return False
    
    def save_person_to_db(self, name, encoding):
        """Salvar pessoa na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se pessoa já existe
        cursor.execute("SELECT id FROM people WHERE name = ?", (name,))
        if cursor.fetchone():
            # Atualizar encoding existente
            cursor.execute(
                "UPDATE people SET face_encoding = ?, updated_at = ? WHERE name = ?",
                (pickle.dumps(encoding), datetime.now(), name)
            )
        else:
            # Inserir nova pessoa
            cursor.execute(
                "INSERT INTO people (name, face_encoding) VALUES (?, ?)",
                (name, pickle.dumps(encoding))
            )
        
        conn.commit()
        conn.close()
    
    def save_model(self, model_path="models/face_model.pkl"):
        """Salvar modelo treinado"""
        os.makedirs("models", exist_ok=True)
        
        model_data = {
            'encodings': self.known_encodings,
            'names': self.known_names,
            'training_date': datetime.now().isoformat()
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Modelo salvo em {model_path}")
    
    def load_model(self, model_path="models/face_model.pkl"):
        """Carregar modelo treinado"""
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.known_encodings = model_data['encodings']
                self.known_names = model_data['names']
            print(f"📂 Modelo carregado: {len(self.known_encodings)} encodings")
            return True
        return False

if __name__ == "__main__":
    trainer = FaceTrainer()
    trainer.train_from_images()