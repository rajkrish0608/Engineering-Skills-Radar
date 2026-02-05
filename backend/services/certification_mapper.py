"""
Certification to Skill Mapper
Maps known certifications to predefined skill sets
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session

from models.database_models import Skill

@dataclass
class CertificationMapping:
    """Represents a certification-to-skills mapping"""
    cert_pattern: str  # Pattern to match certification title
    skill_names: List[str]  # Associated skill names
    confidence: float  # Base confidence for this mapping

class CertificationMapper:
    """
    Maps certifications to skills using:
    1. Pre-defined certification database
    2. Fuzzy matching for variations
    3. Fallback to NLP extraction
    """
    
    # Static certification mappings database
    CERT_MAPPINGS = [
        # Cloud & DevOps
        CertificationMapping(
            cert_pattern="aws certified solutions architect",
            skill_names=["Cloud Computing", "AWS", "System Design"],
            confidence=0.95
        ),
        CertificationMapping(
            cert_pattern="aws certified developer",
            skill_names=["Cloud Computing", "AWS", "Python"],
            confidence=0.95
        ),
        CertificationMapping(
            cert_pattern="google cloud professional",
            skill_names=["Cloud Computing", "GCP"],
            confidence=0.95
        ),
        CertificationMapping(
            cert_pattern="azure fundamentals",
            skill_names=["Cloud Computing", "Azure"],
            confidence=0.90
        ),
        CertificationMapping(
            cert_pattern="kubernetes",
            skill_names=["Containerization", "DevOps", "Cloud Computing"],
            confidence=0.92
        ),
        CertificationMapping(
            cert_pattern="docker",
            skill_names=["Containerization", "DevOps"],
            confidence=0.90
        ),
        
        # Data Science & ML
        CertificationMapping(
            cert_pattern="google data analytics",
            skill_names=["Data Analysis", "Python", "SQL"],
            confidence=0.92
        ),
        CertificationMapping(
            cert_pattern="tensorflow developer",
            skill_names=["Machine Learning", "Deep Learning", "Python"],
            confidence=0.95
        ),
        CertificationMapping(
            cert_pattern="machine learning",
            skill_names=["Machine Learning", "Python"],
            confidence=0.90
        ),
        CertificationMapping(
            cert_pattern="data science",
            skill_names=["Data Analysis", "Machine Learning", "Python"],
            confidence=0.88
        ),
        
        # Programming & Web Dev
        CertificationMapping(
            cert_pattern="python",
            skill_names=["Python", "Programming"],
            confidence=0.85
        ),
        CertificationMapping(
            cert_pattern="java",
            skill_names=["Java", "Object-Oriented Programming"],
            confidence=0.85
        ),
        CertificationMapping(
            cert_pattern="javascript",
            skill_names=["JavaScript", "Web Development"],
            confidence=0.85
        ),
        CertificationMapping(
            cert_pattern="react",
            skill_names=["React", "JavaScript", "Web Development"],
            confidence=0.90
        ),
        CertificationMapping(
            cert_pattern="angular",
            skill_names=["Angular", "JavaScript", "Web Development"],
            confidence=0.90
        ),
        CertificationMapping(
            cert_pattern="full stack",
            skill_names=["Web Development", "JavaScript", "Database Management"],
            confidence=0.88
        ),
        
        # Database & Backend
        CertificationMapping(
            cert_pattern="sql",
            skill_names=["SQL", "Database Management"],
            confidence=0.88
        ),
        CertificationMapping(
            cert_pattern="mongodb",
            skill_names=["Database Management", "NoSQL"],
            confidence=0.88
        ),
        CertificationMapping(
            cert_pattern="postgresql",
            skill_names=["SQL", "Database Management"],
            confidence=0.88
        ),
        
        # Design & CAD
        CertificationMapping(
            cert_pattern="autocad",
            skill_names=["CAD Design", "Technical Drawing"],
            confidence=0.92
        ),
        CertificationMapping(
            cert_pattern="solidworks",
            skill_names=["CAD Design", "3D Modeling"],
            confidence=0.92
        ),
        CertificationMapping(
            cert_pattern="revit",
            skill_names=["BIM", "CAD Design"],
            confidence=0.92
        ),
        
        # Project Management
        CertificationMapping(
            cert_pattern="pmp",
            skill_names=["Project Management"],
            confidence=0.95
        ),
        CertificationMapping(
            cert_pattern="scrum master",
            skill_names=["Agile", "Project Management"],
            confidence=0.92
        ),
        CertificationMapping(
            cert_pattern="agile",
            skill_names=["Agile", "Project Management"],
            confidence=0.88
        ),
    ]
    
    def __init__(self, db: Session):
        """
        Initialize certification mapper
        
        Args:
            db: Database session for skill lookups
        """
        self.db = db
        self._skill_cache = {}
    
    def _get_skill_by_name(self, skill_name: str) -> Optional[Skill]:
        """
        Get skill from database by name (cached)
        
        Args:
            skill_name: Name of skill to find
            
        Returns:
            Skill object or None
        """
        if skill_name not in self._skill_cache:
            skill = self.db.query(Skill).filter(
                Skill.skill_name.ilike(f"%{skill_name}%")
            ).first()
            self._skill_cache[skill_name] = skill
        
        return self._skill_cache[skill_name]
    
    def map_certification(
        self,
        cert_title: str,
        provider: Optional[str] = None,
        min_confidence: float = 0.75
    ) -> List[Dict]:
        """
        Map certification to skills
        
        Args:
            cert_title: Certification title/name
            provider: Certification provider (e.g., "Google", "AWS")
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of skill matches with confidence scores
        """
        if not cert_title:
            return []
        
        cert_lower = cert_title.lower()
        matches = []
        
        # Try exact pattern matching first
        for mapping in self.CERT_MAPPINGS:
            # Use fuzzy matching for flexibility
            similarity = fuzz.partial_ratio(mapping.cert_pattern, cert_lower)
            
            if similarity >= 85:  # 85% similarity threshold
                # Adjust confidence based on match quality
                adjusted_confidence = mapping.confidence * (similarity / 100.0)
                
                # Boost confidence if provider is reputable
                if provider and self._is_reputable_provider(provider):
                    adjusted_confidence = min(1.0, adjusted_confidence * 1.05)
                
                if adjusted_confidence >= min_confidence:
                    # Get actual skill objects
                    for skill_name in mapping.skill_names:
                        skill = self._get_skill_by_name(skill_name)
                        if skill:
                            matches.append({
                                'skill_id': str(skill.id),
                                'skill_name': skill.skill_name,
                                'confidence': adjusted_confidence,
                                'source': 'certification',
                                'evidence_text': f"Certification: {cert_title}",
                                'match_type': 'certification_mapping'
                            })
        
        # Remove duplicates (keep highest confidence)
        unique_matches = {}
        for match in matches:
            skill_id = match['skill_id']
            if skill_id not in unique_matches or match['confidence'] > unique_matches[skill_id]['confidence']:
                unique_matches[skill_id] = match
        
        return list(unique_matches.values())
    
    def _is_reputable_provider(self, provider: str) -> bool:
        """
        Check if certification provider is reputable
        
        Args:
            provider: Provider name
            
        Returns:
            True if reputable
        """
        reputable = [
            'google', 'microsoft', 'amazon', 'aws', 'ibm', 'oracle',
            'meta', 'facebook', 'coursera', 'udacity', 'edx',
            'linkedin', 'salesforce', 'cisco', 'comptia', 'pmi',
            'scrum.org', 'autodesk', 'adobe', 'red hat'
        ]
        
        provider_lower = provider.lower()
        return any(rep in provider_lower for rep in reputable)
