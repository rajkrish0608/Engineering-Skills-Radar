"""
Text Preprocessing Service
Cleans and normalizes text from various sources (projects, resumes, courses)
"""
import re
import string
from typing import List, Set
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

class TextPreprocessor:
    """Service for cleaning and preprocessing text before skill extraction"""
    
    def __init__(self):
        """Initialize spaCy model for text processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("WARNING: spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Technical stopwords to preserve
        self.tech_terms = {
            'c', 'r', 'ai', 'ml', 'ui', 'ux', 'api', 'sql', 'aws', 'gcp',
            'ios', 'css', 'html', 'xml', 'json', 'rest'
        }
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep important programming symbols
        # Keep: +, #, ., -, /
        text = re.sub(r'[^a-z0-9\s\+\#\.\-\/]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Cleaned text
            
        Returns:
            List of tokens
        """
        if not self.nlp:
            # Fallback to simple split
            return text.split()
        
        doc = self.nlp(text)
        return [token.text for token in doc]
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove common English stopwords while preserving technical terms
        
        Args:
            tokens: List of word tokens
            
        Returns:
            Filtered token list
        """
        filtered = []
        for token in tokens:
            # Keep if it's a technical term or not a stopword
            if token.lower() in self.tech_terms or token.lower() not in STOP_WORDS:
                filtered.append(token)
        
        return filtered
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract potential technical terms and phrases
        
        Args:
            text: Cleaned text
            
        Returns:
            List of technical term candidates
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        technical_terms = []
        
        # Extract noun chunks (potential tech terms)
        for chunk in doc.noun_chunks:
            technical_terms.append(chunk.text)
        
        # Extract named entities that might be technologies
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                technical_terms.append(ent.text)
        
        # Extract capitalized words (often tech names like Python, React, etc.)
        for token in doc:
            if token.text[0].isupper() and len(token.text) > 1:
                technical_terms.append(token.text.lower())
        
        return list(set(technical_terms))
    
    def extract_from_bullet_points(self, text: str) -> List[str]:
        """
        Extract text from bullet points in resume/project descriptions
        
        Args:
            text: Text containing bullet points
            
        Returns:
            List of bullet point texts
        """
        # Common bullet point patterns
        bullet_patterns = [
            r'[•●○◦▪▫■□]',  # Unicode bullets
            r'[-\*\+]',      # ASCII bullets
            r'\d+\.',        # Numbered lists
        ]
        
        bullets = []
        for pattern in bullet_patterns:
            matches = re.split(pattern, text)
            for match in matches[1:]:  # Skip first split (before any bullet)
                cleaned = match.strip()
                if cleaned:
                    bullets.append(cleaned)
        
        return bullets if bullets else [text]
    
    def preprocess(self, text: str, extract_bullets: bool = False) -> dict:
        """
        Full preprocessing pipeline
        
        Args:
            text: Raw input text
            extract_bullets: Whether to extract bullet points
            
        Returns:
            Dictionary with preprocessed components
        """
        # Clean text
        cleaned = self.clean_text(text)
        
        # Extract bullets if requested
        if extract_bullets:
            bullet_texts = self.extract_from_bullet_points(cleaned)
        else:
            bullet_texts = [cleaned]
        
        # Tokenize
        tokens = []
        for bullet in bullet_texts:
            tokens.extend(self.tokenize(bullet))
        
        # Remove stopwords
        filtered_tokens = self.remove_stopwords(tokens)
        
        # Extract technical terms
        tech_terms = self.extract_technical_terms(cleaned)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'technical_terms': tech_terms,
            'bullet_points': bullet_texts if extract_bullets else None
        }

# Singleton instance
_preprocessor = None

def get_preprocessor() -> TextPreprocessor:
    """Get or create singleton preprocessor instance"""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = TextPreprocessor()
    return _preprocessor
