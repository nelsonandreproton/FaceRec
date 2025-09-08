# create_database.py
import sqlite3
import os
from datetime import datetime

def create_database():
    """Criar base de dados SQLite"""
    db_path = "face_recognition.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabela de pessoas conhecidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            face_encoding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de detecções
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            detected_person_id INTEGER,
            detected_name TEXT,
            confidence_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'file',
            is_verified BOOLEAN DEFAULT FALSE,
            correct_person_id INTEGER,
            feedback TEXT,
            FOREIGN KEY (detected_person_id) REFERENCES people(id),
            FOREIGN KEY (correct_person_id) REFERENCES people(id)
        )
    """)
    
    # Tabela de feedback para retreino
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER,
            original_prediction TEXT,
            correct_prediction TEXT,
            feedback_type TEXT,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (detection_id) REFERENCES detections(id)
        )
    """)
    
    # Adicionar coluna source se não existir (para bases de dados existentes)
    try:
        cursor.execute("ALTER TABLE detections ADD COLUMN source TEXT DEFAULT 'file'")
        print("✅ Coluna 'source' adicionada à tabela detections")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Coluna 'source' já existe na tabela detections")
        else:
            print(f"⚠️ Aviso ao adicionar coluna 'source': {e}")
    
    conn.commit()
    conn.close()
    print("✅ Base de dados criada com sucesso!")

if __name__ == "__main__":
    create_database()