"""
Similarity calculation utilities
"""
import numpy as np


def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector (numpy array)
        embedding2: Second embedding vector (numpy array)
        
    Returns:
        Similarity score (0-1, where 1 is identical)
    """
    # Ensure embeddings are numpy arrays
    emb1 = np.array(embedding1)
    emb2 = np.array(embedding2)
    
    # Calculate dot product
    dot_product = np.dot(emb1, emb2)
    
    # Calculate magnitudes
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    # Calculate cosine similarity
    similarity = dot_product / (norm1 * norm2)
    
    # Normalize to 0-1 range (cosine similarity is -1 to 1)
    # For face recognition, we typically get positive values
    similarity = (similarity + 1) / 2
    
    return float(similarity)


def euclidean_distance(embedding1, embedding2):
    """
    Calculate Euclidean distance between two embeddings
    
    Args:
        embedding1: First embedding vector (numpy array)
        embedding2: Second embedding vector (numpy array)
        
    Returns:
        Distance (lower is more similar)
    """
    emb1 = np.array(embedding1)
    emb2 = np.array(embedding2)
    
    distance = np.linalg.norm(emb1 - emb2)
    
    return float(distance)


def normalize_embedding(embedding):
    """
    Normalize embedding to unit length
    
    Args:
        embedding: Embedding vector (numpy array)
        
    Returns:
        Normalized embedding
    """
    emb = np.array(embedding)
    norm = np.linalg.norm(emb)
    
    if norm == 0:
        return emb
        
    return emb / norm
