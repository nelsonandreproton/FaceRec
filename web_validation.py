#!/usr/bin/env python3
# web_validation.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import sqlite3
import os
import base64
from datetime import datetime
import json
from config import config

app = Flask(__name__)

class ValidationApp:
    def __init__(self, db_path=None, images_base_path=None):
        self.db_path = db_path or config.DB_PATH
        self.images_base_path = images_base_path or config.IMAGES_BASE_PATH
    
    def get_pending_detections(self, limit=None):
        """Obter detecções pendentes de validação"""
        limit = limit or config.MAX_DETECTIONS_LIMIT
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.id, d.image_path, d.detected_name, d.confidence_score, 
                   d.timestamp, d.is_verified, p.name as actual_name
            FROM detections d
            LEFT JOIN people p ON d.correct_person_id = p.id
            WHERE d.is_verified = FALSE
            ORDER BY d.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        detections = []
        for row in cursor.fetchall():
            detections.append({
                'id': row[0],
                'image_path': row[1],
                'detected_name': row[2],
                'confidence_score': row[3],
                'timestamp': row[4],
                'is_verified': row[5],
                'actual_name': row[6]
            })
        
        conn.close()
        return detections
    
    def get_all_people(self):
        """Obter lista de todas as pessoas conhecidas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM people ORDER BY name")
        people = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return people
    
    def validate_detection(self, detection_id, is_correct, correct_person_id=None, feedback_text=""):
        """Validar uma detecção"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Atualizar detecção
        cursor.execute("""
            UPDATE detections 
            SET is_verified = TRUE, correct_person_id = ?
            WHERE id = ?
        """, (correct_person_id, detection_id))
        
        # Obter detecção original
        cursor.execute("""
            SELECT detected_name, detected_person_id FROM detections WHERE id = ?
        """, (detection_id,))
        
        detection = cursor.fetchone()
        if detection:
            original_name = detection[0]
            
            # Determinar nome correto
            if correct_person_id:
                cursor.execute("SELECT name FROM people WHERE id = ?", (correct_person_id,))
                correct_name_row = cursor.fetchone()
                correct_name = correct_name_row[0] if correct_name_row else "Desconhecido"
            else:
                correct_name = "Desconhecido"
            
            # Registrar feedback se houve correção
            if not is_correct:
                feedback_type = "correction" if correct_person_id else "unknown"
                cursor.execute("""
                    INSERT INTO feedback (detection_id, original_prediction, correct_prediction, 
                                        feedback_type, processed)
                    VALUES (?, ?, ?, ?, FALSE)
                """, (detection_id, original_name, correct_name, feedback_type))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_detection_stats(self):
        """Obter estatísticas das detecções"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de detecções
        cursor.execute("SELECT COUNT(*) FROM detections")
        total = cursor.fetchone()[0]
        
        # Detecções verificadas
        cursor.execute("SELECT COUNT(*) FROM detections WHERE is_verified = TRUE")
        verified = cursor.fetchone()[0]
        
        # Detecções corretas
        cursor.execute("""
            SELECT COUNT(*) FROM detections 
            WHERE is_verified = TRUE 
            AND (detected_person_id = correct_person_id OR 
                 (detected_person_id IS NULL AND correct_person_id IS NULL))
        """)
        correct = cursor.fetchone()[0]
        
        # Feedback pendente
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE processed = FALSE")
        pending_feedback = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'verified': verified,
            'pending': total - verified,
            'correct': correct,
            'accuracy': (correct / verified * 100) if verified > 0 else 0,
            'pending_feedback': pending_feedback
        }

validation_app = ValidationApp()

@app.route('/')
def index():
    """Página principal com lista de detecções pendentes"""
    detections = validation_app.get_pending_detections()
    people = validation_app.get_all_people()
    stats = validation_app.get_detection_stats()
    
    return render_template('validation.html', 
                         detections=detections, 
                         people=people, 
                         stats=stats)

@app.route('/api/validate', methods=['POST'])
def validate_detection():
    """API para validar uma detecção"""
    data = request.json
    detection_id = data.get('detection_id')
    is_correct = data.get('is_correct')
    correct_person_id = data.get('correct_person_id')
    feedback_text = data.get('feedback', '')
    
    if not detection_id:
        return jsonify({'error': 'ID da detecção é obrigatório'}), 400
    
    try:
        validation_app.validate_detection(detection_id, is_correct, correct_person_id, feedback_text)
        return jsonify({'success': True, 'message': 'Validação registrada com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Servir imagens"""
    return send_from_directory(validation_app.images_base_path, filename)

@app.route('/stats')
def stats():
    """Página de estatísticas"""
    stats = validation_app.get_detection_stats()
    return render_template('stats.html', stats=stats)

@app.route('/api/retrain', methods=['POST'])
def trigger_retrain():
    """API para disparar retreino do modelo"""
    import time
    start_time = time.time()
    
    try:
        from retrain_model import RetainModel
        retrainer = RetainModel()
        success = retrainer.retrain_with_feedback()
        
        end_time = time.time()
        duration = end_time - start_time
        
        if duration < 60:
            training_time = f"{duration:.1f} segundos"
        else:
            training_time = f"{duration / 60:.1f} minutos"
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'Modelo retreinado com sucesso',
                'training_time': training_time,
                'duration_seconds': round(duration, 1)
            })
        else:
            return jsonify({'error': 'Falha no retreino do modelo'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro no retreino: {str(e)}'}), 500

if __name__ == '__main__':
    # Print configuration
    config.print_config()
    
    # Criar pastas se não existirem
    os.makedirs(config.TEMPLATES_PATH, exist_ok=True)
    os.makedirs(config.STATIC_PATH, exist_ok=True)
    
    # Executar aplicação
    print(f"🚀 Starting web validation server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(debug=config.FLASK_DEBUG, host=config.FLASK_HOST, port=config.FLASK_PORT)