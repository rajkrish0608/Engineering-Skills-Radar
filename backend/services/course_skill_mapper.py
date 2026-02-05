"""
Course to Skill Mapper
Maps course codes and names to related skills
"""
from typing import List, Dict, Optional
import re
from sqlalchemy.orm import Session

from models.database_models import Skill, Course

class CourseSkillMapper:
    """
    Maps courses to skills using:
    1. Course code patterns (e.g., CS101 → Programming)
    2. Course name keyword matching
    3. Syllabus parsing (if available)
    """
    
    # Course code prefix to skill category mappings
    CODE_PREFIX_MAPPINGS = {
        # Computer Science
        'cs': ['Programming', 'Algorithms', 'Software Development'],
        'cse': ['Programming', 'Algorithms', 'Software Development'],
        'it': ['Programming', 'System Design', 'Networking'],
        
        # Mechanical Engineering
        'me': ['CAD Design', 'Simulation', 'Manufacturing'],
        'mech': ['CAD Design', 'Simulation', 'Manufacturing'],
        
        # Electrical/Electronics
        'ee': ['Circuit Design', 'Embedded Systems', 'Control Systems'],
        'ece': ['Circuit Design', 'Embedded Systems', 'Signal Processing'],
        'eee': ['Circuit Design', 'Power Systems', 'Control Systems'],
        
        # Civil Engineering
        'ce': ['Structural Analysis', 'CAD Design', 'BIM'],
        'civil': ['Structural Analysis', 'Construction', 'Surveying'],
        
        # Data/Math
        'math': ['Mathematics', 'Problem Solving'],
        'stat': ['Statistics', 'Data Analysis'],
        'data': ['Data Analysis', 'Database Management', 'Machine Learning'],
    }
    
    # Course name keyword to skills
    KEYWORD_MAPPINGS = {
        # Programming
        'programming': ['Programming', 'Problem Solving'],
        'python': ['Python', 'Programming'],
        'java': ['Java', 'Object-Oriented Programming'],
        'c++': ['C++', 'Programming'],
        'javascript': ['JavaScript', 'Web Development'],
        'web development': ['Web Development', 'JavaScript', 'HTML/CSS'],
        'mobile': ['Mobile Development'],
        'android': ['Android', 'Java', 'Mobile Development'],
        'ios': ['iOS', 'Swift', 'Mobile Development'],
        
        # Data & AI
        'machine learning': ['Machine Learning', 'Python', 'Data Analysis'],
        'data science': ['Data Analysis', 'Machine Learning', 'Python'],
        'artificial intelligence': ['Machine Learning', 'Python', 'Algorithms'],
        'data structures': ['Data Structures', 'Algorithms', 'Programming'],
        'algorithms': ['Algorithms', 'Problem Solving'],
        'database': ['Database Management', 'SQL'],
        'sql': ['SQL', 'Database Management'],
        
        # Systems
        'operating system': ['Operating Systems', 'System Design'],
        'computer networks': ['Networking', 'System Design'],
        'distributed systems': ['System Design', 'Cloud Computing'],
        'cloud computing': ['Cloud Computing', 'System Design'],
        
        # Design & CAD
        'cad': ['CAD Design', 'Technical Drawing'],
        'autocad': ['CAD Design', 'Technical Drawing'],
        'solidworks': ['CAD Design', '3D Modeling'],
        'bim': ['BIM', 'CAD Design'],
        'architectural': ['CAD Design', 'BIM'],
        
        # Mechanical
        'thermodynamics': ['Thermodynamics', 'Heat Transfer'],
        'fluid mechanics': ['Fluid Mechanics', 'CFD'],
        'manufacturing': ['Manufacturing', 'Production Planning'],
        'robotics': ['Robotics', 'Control Systems', 'Programming'],
        
        # Electrical
        'circuits': ['Circuit Design', 'Electronics'],
        'electronics': ['Circuit Design', 'Electronics'],
        'embedded': ['Embedded Systems', 'Microcontrollers', 'C'],
        'microcontroller': ['Embedded Systems', 'Microcontrollers'],
        'signal processing': ['Signal Processing', 'DSP'],
        'control systems': ['Control Systems', 'Automation'],
        
        # Civil
        'structural': ['Structural Analysis', 'Design'],
        'geotechnical': ['Geotechnical Engineering', 'Soil Mechanics'],
        'transportation': ['Transportation Engineering'],
        'construction': ['Construction Management', 'Project Management'],
    }
    
    def __init__(self, db: Session):
        """
        Initialize course mapper
        
        Args:
            db: Database session
        """
        self.db = db
        self._skill_cache = {}
    
    def _get_skill_by_name(self, skill_name: str) -> Optional[Skill]:
        """Get skill from database by name (cached)"""
        if skill_name not in self._skill_cache:
            skill = self.db.query(Skill).filter(
                Skill.skill_name.ilike(f"%{skill_name}%")
            ).first()
            self._skill_cache[skill_name] = skill
        
        return self._skill_cache[skill_name]
    
    def map_course(
        self,
        course_code: Optional[str] = None,
        course_name: Optional[str] = None,
        syllabus: Optional[str] = None
    ) -> List[Dict]:
        """
        Map course to skills
        
        Args:
            course_code: Course code (e.g., "CS101", "ME301")
            course_name: Course name
            syllabus: Course syllabus text
            
        Returns:
            List of skill matches with confidence
        """
        matches = []
        
        # Strategy 1: Course code pattern matching
        if course_code:
            code_matches = self._match_by_code(course_code)
            matches.extend(code_matches)
        
        # Strategy 2: Course name keyword matching
        if course_name:
            name_matches = self._match_by_name(course_name)
            matches.extend(name_matches)
        
        # Strategy 3: Syllabus parsing (if available)
        if syllabus:
            syllabus_matches = self._match_by_syllabus(syllabus)
            matches.extend(syllabus_matches)
        
        # Remove duplicates (keep highest confidence)
        unique_matches = {}
        for match in matches:
            skill_id = match['skill_id']
            if skill_id not in unique_matches or match['confidence'] > unique_matches[skill_id]['confidence']:
                unique_matches[skill_id] = match
        
        return list(unique_matches.values())
    
    def _match_by_code(self, course_code: str) -> List[Dict]:
        """Match skills by course code prefix"""
        matches = []
        code_lower = course_code.lower()
        
        # Extract prefix (letters before numbers)
        prefix_match = re.match(r'([a-z]+)', code_lower)
        if not prefix_match:
            return matches
        
        prefix = prefix_match.group(1)
        
        if prefix in self.CODE_PREFIX_MAPPINGS:
            skill_names = self.CODE_PREFIX_MAPPINGS[prefix]
            for skill_name in skill_names:
                skill = self._get_skill_by_name(skill_name)
                if skill:
                    matches.append({
                        'skill_id': str(skill.id),
                        'skill_name': skill.skill_name,
                        'confidence': 0.70,  # Moderate confidence from code
                        'source': 'course',
                        'evidence_text': f"Course Code: {course_code}",
                        'match_type': 'course_code_pattern'
                    })
        
        return matches
    
    def _match_by_name(self, course_name: str) -> List[Dict]:
        """Match skills by course name keywords"""
        matches = []
        name_lower = course_name.lower()
        
        for keyword, skill_names in self.KEYWORD_MAPPINGS.items():
            if keyword in name_lower:
                for skill_name in skill_names:
                    skill = self._get_skill_by_name(skill_name)
                    if skill:
                        matches.append({
                            'skill_id': str(skill.id),
                            'skill_name': skill.skill_name,
                            'confidence': 0.80,  # Higher confidence from name
                            'source': 'course',
                            'evidence_text': f"Course: {course_name}",
                            'match_type': 'course_name_keyword'
                        })
        
        return matches
    
    def _match_by_syllabus(self, syllabus: str) -> List[Dict]:
        """Match skills by syllabus content (basic keyword extraction)"""
        matches = []
        syllabus_lower = syllabus.lower()
        
        # Use same keyword mappings as course name
        for keyword, skill_names in self.KEYWORD_MAPPINGS.items():
            if keyword in syllabus_lower:
                for skill_name in skill_names:
                    skill = self._get_skill_by_name(skill_name)
                    if skill:
                        # Extract evidence snippet
                        evidence = self._extract_evidence(syllabus, keyword)
                        
                        matches.append({
                            'skill_id': str(skill.id),
                            'skill_name': skill.skill_name,
                            'confidence': 0.75,
                            'source': 'course',
                            'evidence_text': evidence,
                            'match_type': 'syllabus_keyword'
                        })
        
        return matches
    
    def _extract_evidence(self, text: str, keyword: str, context_chars: int = 80) -> str:
        """Extract text snippet containing keyword"""
        pos = text.lower().find(keyword)
        if pos == -1:
            return text[:context_chars] + "..."
        
        start = max(0, pos - context_chars // 2)
        end = min(len(text), pos + len(keyword) + context_chars // 2)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
