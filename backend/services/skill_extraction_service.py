"""
Skill Extraction Service
Core NLP-based skill extraction engine using multiple matching strategies
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session

from models.database_models import Skill
from services.text_preprocessor import get_preprocessor

@dataclass
class SkillMatch:
    """Represents a matched skill with confidence score"""
    skill_id: str
    skill_name: str
    confidence: float  # 0-1
    source: str  # 'project', 'resume', 'certification', 'course'
    evidence_text: str  # The text snippet that matched
    match_type: str  # 'exact', 'fuzzy', 'semantic'

class SkillExtractionService:
    """
    Multi-strategy skill extraction using:
    1. Exact keyword matching
    2. Fuzzy string matching
    3. Semantic similarity (sentence-transformers)
    """
    
    def __init__(self, db: Session):
        """
        Initialize extraction service
        
        Args:
            db: Database session for skill queries
        """
        self.db = db
        self.preprocessor = get_preprocessor()
        
        # Load sentence transformer model for semantic similarity
        try:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"WARNING: Could not load semantic model: {e}")
            self.semantic_model = None
        
        # Cache skills from database
        self._skill_cache = None
        self._skill_embeddings = None
        
    def _load_skills(self) -> List[Skill]:
        """Load all skills from database and cache"""
        if self._skill_cache is None:
            self._skill_cache = self.db.query(Skill).all()
        return self._skill_cache
    
    def _get_skill_embeddings(self) -> Tuple[List[str], np.ndarray]:
        """
        Get or create sentence embeddings for all skills
        
        Returns:
            Tuple of (skill_names, embeddings_matrix)
        """
        if self._skill_embeddings is None and self.semantic_model:
            skills = self._load_skills()
            skill_texts = [f"{skill.skill_name} {skill.description or ''}" for skill in skills]
            self._skill_embeddings = (
                [skill.skill_name for skill in skills],
                self.semantic_model.encode(skill_texts)
            )
        return self._skill_embeddings
    
    def _exact_match(self, text: str, skill_name: str) -> float:
        """
        Check for exact keyword match
        
        Args:
            text: Input text (preprocessed)
            skill_name: Skill name to match
            
        Returns:
            Confidence score (1.0 if match, 0.0 otherwise)
        """
        # Normalize both
        text_lower = text.lower()
        skill_lower = skill_name.lower()
        
        # Check if skill name appears as whole word
        import re
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            return 1.0
        
        return 0.0
    
    def _fuzzy_match(self, text: str, skill_name: str) -> float:
        """
        Fuzzy string matching for skill variations
        
        Args:
            text: Input text
            skill_name: Skill name
            
        Returns:
            Confidence score (0-1)
        """
        # Use fuzzywuzzy partial ratio
        score = fuzz.partial_ratio(skill_name.lower(), text.lower())
        
        # Normalize to 0-1
        normalized = score / 100.0
        
        # Only return if above threshold (90%)
        if normalized >= 0.9:
            return normalized
        
        return 0.0
    
    def _semantic_match(self, text: str, skill_name: str) -> float:
        """
        Semantic similarity matching using sentence transformers
        
        Args:
            text: Input text
            skill_name: Skill name
            
        Returns:
            Cosine similarity score (0-1)
        """
        if not self.semantic_model:
            return 0.0
        
        # Encode both texts
        text_embedding = self.semantic_model.encode([text])
        skill_embedding = self.semantic_model.encode([skill_name])
        
        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(text_embedding, skill_embedding)[0][0]
        
        # Only return if above threshold
        if similarity >= 0.7:
            return float(similarity)
        
        return 0.0
    
    def _calculate_confidence(
        self,
        exact_score: float,
        fuzzy_score: float,
        semantic_score: float,
        source: str
    ) -> Tuple[float, str]:
        """
        Calculate final confidence score from multiple match strategies
        
        Args:
            exact_score: Exact match score
            fuzzy_score: Fuzzy match score
            semantic_score: Semantic match score
            source: Data source
            
        Returns:
            Tuple of (final_confidence, match_type)
        """
        # Prioritize exact match
        if exact_score > 0:
            confidence = 1.0
            match_type = 'exact'
        elif fuzzy_score > semantic_score:
            confidence = fuzzy_score * 0.95  # Slightly discount fuzzy
            match_type = 'fuzzy'
        elif semantic_score > 0:
            confidence = semantic_score * 0.85  # Discount semantic more
            match_type = 'semantic'
        else:
            return 0.0, 'none'
        
        # Apply source credibility multiplier
        source_weights = {
            'internship': 0.95,
            'project': 0.90,
            'certification': 1.0,
            'course': 0.75,
            'resume': 0.85
        }
        
        weight = source_weights.get(source, 0.8)
        final_confidence = confidence * weight
        
        return final_confidence, match_type
    
    def extract_skills(
        self,
        text: str,
        source: str,
        min_confidence: float = 0.6
    ) -> List[SkillMatch]:
        """
        Extract skills from text using multiple strategies
        
        Args:
            text: Input text (project description, resume, etc.)
            source: Data source ('project', 'resume', 'certification', 'course')
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of SkillMatch objects
        """
        if not text:
            return []
        
        # Preprocess text
        processed = self.preprocessor.preprocess(text, extract_bullets=True)
        cleaned_text = processed['cleaned']
        
        # Load all skills
        skills = self._load_skills()
        matches = []
        
        for skill in skills:
            # Try all matching strategies
            exact_score = self._exact_match(cleaned_text, skill.skill_name)
            fuzzy_score = self._fuzzy_match(cleaned_text, skill.skill_name)
            semantic_score = self._semantic_match(cleaned_text, skill.skill_name)
            
            # Calculate final confidence
            confidence, match_type = self._calculate_confidence(
                exact_score, fuzzy_score, semantic_score, source
            )
            
            # Add if above threshold
            if confidence >= min_confidence:
                # Extract evidence snippet
                evidence = self._extract_evidence(cleaned_text, skill.skill_name)
                
                matches.append(SkillMatch(
                    skill_id=str(skill.id),
                    skill_name=skill.skill_name,
                    confidence=confidence,
                    source=source,
                    evidence_text=evidence,
                    match_type=match_type
                ))
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        return matches
    
    def _extract_evidence(self, text: str, skill_name: str, context_chars: int = 100) -> str:
        """
        Extract a snippet of text containing the skill mention
        
        Args:
            text: Full text
            skill_name: Skill to find
            context_chars: Characters of context to include
            
        Returns:
            Evidence snippet
        """
        text_lower = text.lower()
        skill_lower = skill_name.lower()
        
        # Find skill position
        pos = text_lower.find(skill_lower)
        if pos == -1:
            # Return first N chars if not found
            return text[:context_chars] + "..."
        
        # Extract context window
        start = max(0, pos - context_chars // 2)
        end = min(len(text), pos + len(skill_name) + context_chars // 2)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def extract_from_project(self, project_description: str) -> List[SkillMatch]:
        """Extract skills from project description"""
        return self.extract_skills(project_description, source='project')
    
    def extract_from_resume(self, resume_text: str) -> List[SkillMatch]:
        """Extract skills from resume/CV text"""
        return self.extract_skills(resume_text, source='resume')
    
    def extract_from_course(self, course_name: str, syllabus: Optional[str] = None) -> List[SkillMatch]:
        """Extract skills from course information"""
        text = course_name
        if syllabus:
            text += " " + syllabus
        return self.extract_skills(text, source='course')
