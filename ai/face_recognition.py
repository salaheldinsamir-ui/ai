"""
Face Recognition Module
Generates face embeddings and performs recognition
"""
import cv2
import numpy as np
from deepface import DeepFace
import os


class FaceRecognizer:
    """Generates face embeddings and compares faces"""
    
    def __init__(self, model_name="Facenet", backend="opencv"):
        """
        Initialize face recognizer
        
        Args:
            model_name: Model to use ("Facenet", "VGG-Face", "OpenFace", "Facenet512", "ArcFace")
            backend: Detection backend for DeepFace
        """
        self.model_name = model_name
        self.backend = backend
        
    def generate_embedding(self, face_img):
        """
        Generate face embedding from face image
        
        Args:
            face_img: Face image (BGR or RGB)
            
        Returns:
            Numpy array of face embedding or None if failed
        """
        try:
            # DeepFace.represent returns a list of embeddings
            embedding_objs = DeepFace.represent(
                img_path=face_img,
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend=self.backend
            )
            
            if embedding_objs and len(embedding_objs) > 0:
                # Extract the embedding vector
                embedding = np.array(embedding_objs[0]["embedding"])
                return embedding
            else:
                return None
                
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
            
    def compare_embeddings(self, embedding1, embedding2, threshold=0.6):
        """
        Compare two face embeddings using cosine similarity
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            threshold: Similarity threshold (0-1)
            
        Returns:
            Tuple: (is_match, similarity_score)
        """
        from utils.similarity import cosine_similarity
        
        # Calculate cosine similarity
        similarity = cosine_similarity(embedding1, embedding2)
        
        # Determine if it's a match
        is_match = similarity >= threshold
        
        return is_match, similarity
        
    def recognize_face(self, face_img, database_embeddings, threshold=0.6):
        """
        Recognize a face against a database of embeddings
        
        Args:
            face_img: Face image to recognize
            database_embeddings: List of tuples (student_id, name, aruco_id, embedding)
            threshold: Similarity threshold
            
        Returns:
            Tuple: (student_id, name, aruco_id, similarity) or (None, None, None, 0)
        """
        # Generate embedding for input face
        query_embedding = self.generate_embedding(face_img)
        
        if query_embedding is None:
            return None, None, None, 0.0
            
        # Compare with all database embeddings
        best_match = None
        best_similarity = 0.0
        
        for student_id, name, aruco_id, db_embedding in database_embeddings:
            is_match, similarity = self.compare_embeddings(
                query_embedding, db_embedding, threshold
            )
            
            if is_match and similarity > best_similarity:
                best_similarity = similarity
                best_match = (student_id, name, aruco_id, similarity)
                
        if best_match:
            return best_match
        else:
            return None, None, None, 0.0
            
    def preprocess_face(self, face_img, target_size=(160, 160)):
        """
        Preprocess face image for embedding generation
        
        Args:
            face_img: Input face image
            target_size: Target size for model input
            
        Returns:
            Preprocessed face image
        """
        # Resize to model input size
        face_resized = cv2.resize(face_img, target_size)
        
        # Normalize pixel values
        face_normalized = face_resized.astype('float32') / 255.0
        
        return face_normalized
