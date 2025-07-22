"""
Text processing utilities
"""

import re
import spacy
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Text processing and analysis utilities"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except IOError:
            logger.warning("spaCy English model not found. Some features may be limited.")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', ' ', text)
        
        return text.strip()
    
    def is_likely_heading(self, text: str, font_size: float, avg_font_size: float) -> bool:
        """Determine if text is likely a heading based on various criteria"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Font size criterion
        font_size_ratio = font_size / avg_font_size if avg_font_size > 0 else 1
        is_larger_font = font_size_ratio > 1.1
        
        # Text characteristics
        is_short = len(text) < 100  # Headings are usually shorter
        is_capitalized = text.isupper() or text.istitle()
        ends_with_colon = text.strip().endswith(':')
        
        # Pattern matching for common heading patterns
        heading_patterns = [
            r'^\d+[\.\)]\s+',  # 1. or 1)
            r'^[A-Z]+[\.\s]+',  # CHAPTER or SECTION
            r'^\w+\s+\d+',     # Chapter 1
        ]
        
        matches_pattern = any(re.match(pattern, text.strip()) for pattern in heading_patterns)
        
        # Combine criteria
        score = 0
        if is_larger_font: score += 2
        if is_short: score += 1
        if is_capitalized: score += 1
        if ends_with_colon: score += 1
        if matches_pattern: score += 2
        
        return score >= 3
    
    def classify_heading_level(self, text: str, font_size: float, font_sizes: List[float]) -> str:
        """Classify heading level based on font size and text patterns"""
        if not font_sizes:
            return "H1"
        
        # Sort font sizes to determine hierarchy
        unique_sizes = sorted(list(set(font_sizes)), reverse=True)
        
        if len(unique_sizes) < 2:
            return "H1"
        
        # Determine level based on font size rank
        try:
            size_rank = unique_sizes.index(font_size)
            if size_rank == 0:
                return "H1"
            elif size_rank == 1:
                return "H2"
            else:
                return "H3"
        except ValueError:
            return "H3"
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using NLP"""
        if not self.nlp or not text:
            return []
        
        doc = self.nlp(text)
        
        # Extract meaningful tokens
        keywords = []
        for token in doc:
            if (token.is_alpha and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Count frequency and return top keywords
        from collections import Counter
        keyword_freq = Counter(keywords)
        
        return [word for word, _ in keyword_freq.most_common(max_keywords)]
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not self.nlp or not text1 or not text2:
            return 0.0
        
        try:
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            
            return doc1.similarity(doc2)
        except Exception as e:
            logger.warning(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def detect_language(self, text: str) -> str:
        """Detect text language (basic implementation)"""
        if not text:
            return "unknown"
        
        # Simple heuristic for Japanese detection
        japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text)
        if len(japanese_chars) > len(text) * 0.1:
            return "ja"
        
        # Default to English
        return "en"
    
    def segment_text_into_sections(self, text: str) -> List[Dict]:
        """Segment text into logical sections"""
        if not text:
            return []
        
        # Split by double newlines (paragraph breaks)
        sections = re.split(r'\n\n+', text)
        
        processed_sections = []
        for i, section in enumerate(sections):
            section = section.strip()
            if section and len(section) > 20:  # Ignore very short sections
                processed_sections.append({
                    "index": i,
                    "text": section,
                    "word_count": len(section.split()),
                    "char_count": len(section)
                })
        
        return processed_sections