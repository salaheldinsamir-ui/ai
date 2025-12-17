"""
Database Manager for the Attendance System
Handles all SQLite database operations
"""
import sqlite3
import os
from datetime import datetime
import pickle
import numpy as np


class DatabaseManager:
    """Manages SQLite database operations for students and attendance"""
    
    def __init__(self, db_path):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                aruco_id INTEGER UNIQUE NOT NULL,
                face_embedding BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(student_id, date)
            )
        """)
        
        conn.commit()
        conn.close()
        
    def add_student(self, name, aruco_id, face_embedding):
        """
        Add a new student to the database (enrollment only)
        
        Args:
            name: Student name
            aruco_id: Unique ArUco marker ID
            face_embedding: Numpy array of face embedding
            
        Returns:
            Student ID if successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize face embedding
            embedding_blob = pickle.dumps(face_embedding)
            
            cursor.execute("""
                INSERT INTO students (name, aruco_id, face_embedding)
                VALUES (?, ?, ?)
            """, (name, aruco_id, embedding_blob))
            
            student_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return student_id
            
        except sqlite3.IntegrityError:
            print(f"Error: ArUco ID {aruco_id} already exists")
            return None
        except Exception as e:
            print(f"Error adding student: {e}")
            return None
            
    def get_all_students(self):
        """
        Retrieve all students from database
        
        Returns:
            List of tuples: (id, name, aruco_id, face_embedding)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, aruco_id, face_embedding FROM students")
        rows = cursor.fetchall()
        conn.close()
        
        # Deserialize face embeddings
        students = []
        for row in rows:
            student_id, name, aruco_id, embedding_blob = row
            face_embedding = pickle.loads(embedding_blob)
            students.append((student_id, name, aruco_id, face_embedding))
            
        return students
        
    def get_student_by_id(self, student_id):
        """
        Retrieve a student by ID
        
        Args:
            student_id: Student ID
            
        Returns:
            Tuple: (id, name, aruco_id, face_embedding) or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, aruco_id, face_embedding 
            FROM students 
            WHERE id = ?
        """, (student_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            student_id, name, aruco_id, embedding_blob = row
            face_embedding = pickle.loads(embedding_blob)
            return (student_id, name, aruco_id, face_embedding)
        return None
        
    def get_student_by_aruco(self, aruco_id):
        """
        Retrieve a student by ArUco ID
        
        Args:
            aruco_id: ArUco marker ID
            
        Returns:
            Tuple: (id, name, aruco_id, face_embedding) or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, aruco_id, face_embedding 
            FROM students 
            WHERE aruco_id = ?
        """, (aruco_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            student_id, name, aruco_id, embedding_blob = row
            face_embedding = pickle.loads(embedding_blob)
            return (student_id, name, aruco_id, face_embedding)
        return None
        
    def mark_attendance(self, student_id, status="Present"):
        """
        Mark attendance for a student
        
        Args:
            student_id: Student ID
            status: Attendance status (default: "Present")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            cursor.execute("""
                INSERT INTO attendance (student_id, date, time, status)
                VALUES (?, ?, ?, ?)
            """, (student_id, date_str, time_str, status))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            # Attendance already marked for today
            return False
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
            
    def check_attendance_today(self, student_id):
        """
        Check if attendance is already marked for today
        
        Args:
            student_id: Student ID
            
        Returns:
            True if already marked, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT id FROM attendance 
            WHERE student_id = ? AND date = ?
        """, (student_id, today))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
        
    def get_attendance_by_date(self, date_str):
        """
        Get all attendance records for a specific date
        
        Args:
            date_str: Date string in format "YYYY-MM-DD"
            
        Returns:
            List of tuples: (student_name, time, status)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.name, a.time, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date = ?
            ORDER BY a.time
        """, (date_str,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
        
    def get_student_count(self):
        """
        Get total number of enrolled students
        
        Returns:
            Number of students
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
