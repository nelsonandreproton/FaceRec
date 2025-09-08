#!/usr/bin/env python3
# retrain_model.py
import sqlite3
import pickle
import face_recognition
import numpy as np
import os
from datetime import datetime
from train_model import FaceTrainer
from config import config

class RetainModel:
    def __init__(self, db_path=None, model_path=None):
        self.db_path = db_path or config.DB_PATH
        self.model_path = model_path or config.MODEL_PATH
        self.trainer = FaceTrainer(self.db_path)
    
    def get_feedback_data(self):
        """Obter dados de feedback não processados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.id, f.detection_id, f.original_prediction, f.correct_prediction, 
                   f.feedback_type, d.image_path
            FROM feedback f
            JOIN detections d ON f.detection_id = d.id
            WHERE f.processed = FALSE
        """)
        
        feedback_data = []
        for row in cursor.fetchall():
            feedback_data.append({
                'feedback_id': row[0],
                'detection_id': row[1],
                'original_prediction': row[2],
                'correct_prediction': row[3],
                'feedback_type': row[4],
                'image_path': row[5]
            })
        
        conn.close()
        return feedback_data
    
    def process_corrections(self, feedback_data):
        """Processar correções e extrair novos encodings"""
        corrections = []
        
        for feedback in feedback_data:
            image_path = feedback['image_path']
            correct_name = feedback['correct_prediction']
            
            # Construir caminho completo se necessário
            if not os.path.isabs(image_path):
                full_image_path = os.path.join(config.IMAGES_BASE_PATH, image_path)
            else:
                full_image_path = image_path
            
            if not os.path.exists(full_image_path) or correct_name == "Desconhecido":
                print(f"⚠️ Saltando: {full_image_path} (existe: {os.path.exists(full_image_path)}, nome: {correct_name})")
                continue
            
            try:
                # Carregar imagem e extrair encoding
                image = face_recognition.load_image_file(full_image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    corrections.append({
                        'name': correct_name,
                        'encoding': face_encodings[0],
                        'feedback_id': feedback['feedback_id']
                    })
                    print(f"✅ Encoding extraído para {correct_name}")
                else:
                    print(f"⚠️ Nenhuma face encontrada em {full_image_path}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar {full_image_path}: {e}")
        
        return corrections
    
    def update_person_encodings(self, corrections):
        """Atualizar encodings das pessoas com novas correções"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agrupar correções por pessoa
        person_corrections = {}
        for correction in corrections:
            name = correction['name']
            if name not in person_corrections:
                person_corrections[name] = []
            person_corrections[name].append(correction)
        
        for person_name, person_corrections_list in person_corrections.items():
            try:
                # Obter encoding atual da pessoa
                cursor.execute("SELECT face_encoding FROM people WHERE name = ?", (person_name,))
                result = cursor.fetchone()
                
                if result:
                    # Pessoa existe - combinar encodings
                    current_encoding = pickle.loads(result[0])
                    new_encodings = [correction['encoding'] for correction in person_corrections_list]
                    all_encodings = [current_encoding] + new_encodings
                    
                    # Calcular encoding médio
                    avg_encoding = np.mean(all_encodings, axis=0)
                    
                    # Atualizar na base de dados
                    cursor.execute("""
                        UPDATE people 
                        SET face_encoding = ?, updated_at = ?
                        WHERE name = ?
                    """, (pickle.dumps(avg_encoding), datetime.now(), person_name))
                    
                    print(f"🔄 Encoding atualizado para {person_name} ({len(new_encodings)} novas amostras)")
                    
                else:
                    # Pessoa nova - criar entrada
                    if len(person_corrections_list) == 1:
                        encoding = person_corrections_list[0]['encoding']
                    else:
                        encodings = [correction['encoding'] for correction in person_corrections_list]
                        encoding = np.mean(encodings, axis=0)
                    
                    cursor.execute("""
                        INSERT INTO people (name, face_encoding)
                        VALUES (?, ?)
                    """, (person_name, pickle.dumps(encoding)))
                    
                    print(f"➕ Nova pessoa adicionada: {person_name}")
                    
            except Exception as e:
                print(f"❌ Erro ao atualizar {person_name}: {e}")
        
        conn.commit()
        conn.close()
    
    def rebuild_model(self):
        """Reconstruir modelo com todos os dados atualizados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter todas as pessoas e seus encodings
            cursor.execute("SELECT name, face_encoding FROM people")
            
            all_encodings = []
            all_names = []
            
            for row in cursor.fetchall():
                name = row[0]
                encoding = pickle.loads(row[1])
                
                # Para cada pessoa, adicionar encoding múltiplas vezes para balanceamento
                # (simula ter múltiplas fotos de treino)
                for _ in range(3):  # Replicar 3 vezes
                    all_encodings.append(encoding)
                    all_names.append(name)
            
            conn.close()
            
            if all_encodings:
                # Salvar modelo atualizado
                model_data = {
                    'encodings': all_encodings,
                    'names': all_names,
                    'training_date': datetime.now().isoformat(),
                    'retrain_count': getattr(self, 'retrain_count', 0) + 1
                }
                
                # Criar backup do modelo anterior
                if os.path.exists(self.model_path):
                    backup_path = f"{self.model_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    os.rename(self.model_path, backup_path)
                    print(f"💾 Backup criado: {backup_path}")
                
                # Salvar novo modelo
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                with open(self.model_path, 'wb') as f:
                    pickle.dump(model_data, f)
                
                print(f"🎉 Modelo retreinado com {len(set(all_names))} pessoas e {len(all_encodings)} encodings")
                return True
            else:
                print("❌ Nenhum dado disponível para treino")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao reconstruir modelo: {e}")
            return False
    
    def mark_feedback_processed(self, feedback_ids):
        """Marcar feedback como processado"""
        if not feedback_ids:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(feedback_ids))
        cursor.execute(f"""
            UPDATE feedback 
            SET processed = TRUE 
            WHERE id IN ({placeholders})
        """, feedback_ids)
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(feedback_ids)} feedbacks marcados como processados")
    
    def retrain_with_feedback(self):
        """Executar processo completo de retreino com feedback"""
        print("🔄 Iniciando retreino com feedback...")
        
        # 1. Obter dados de feedback
        feedback_data = self.get_feedback_data()
        
        if not feedback_data:
            print("ℹ️ Nenhum feedback pendente para processamento")
            return True
        
        print(f"📊 {len(feedback_data)} feedbacks encontrados")
        
        # 2. Processar correções
        corrections = self.process_corrections(feedback_data)
        
        if not corrections:
            print("⚠️ Nenhuma correção válida encontrada")
            return False
        
        print(f"✅ {len(corrections)} correções processadas")
        
        # 3. Atualizar encodings das pessoas
        self.update_person_encodings(corrections)
        
        # 4. Reconstruir modelo
        success = self.rebuild_model()
        
        if success:
            # 5. Marcar feedback como processado
            feedback_ids = [correction['feedback_id'] for correction in corrections]
            self.mark_feedback_processed(feedback_ids)
            
            print("🎯 Retreino concluído com sucesso!")
            return True
        else:
            print("❌ Falha no retreino")
            return False
    
    def get_retrain_stats(self):
        """Obter estatísticas do retreino"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback total
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        # Feedback processado
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE processed = TRUE")
        processed_feedback = cursor.fetchone()[0]
        
        # Feedback pendente
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE processed = FALSE")
        pending_feedback = cursor.fetchone()[0]
        
        # Últimas correções
        cursor.execute("""
            SELECT f.correct_prediction, f.created_at
            FROM feedback f
            WHERE f.processed = TRUE
            ORDER BY f.created_at DESC
            LIMIT 10
        """)
        
        recent_corrections = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'processed_feedback': processed_feedback,
            'pending_feedback': pending_feedback,
            'recent_corrections': recent_corrections
        }

if __name__ == "__main__":
    print("🎯 Sistema de Retreino com Feedback")
    print("==================================")
    
    retrainer = RetainModel()
    
    # Mostrar estatísticas
    stats = retrainer.get_retrain_stats()
    print(f"📊 Feedback total: {stats['total_feedback']}")
    print(f"✅ Processado: {stats['processed_feedback']}")
    print(f"⏳ Pendente: {stats['pending_feedback']}")
    
    if stats['pending_feedback'] > 0:
        print(f"\n🔄 Iniciando retreino com {stats['pending_feedback']} feedbacks pendentes...")
        success = retrainer.retrain_with_feedback()
        
        if success:
            print("🎉 Retreino concluído com sucesso!")
        else:
            print("❌ Falha no retreino")
    else:
        print("\nℹ️ Nenhum feedback pendente para processamento")