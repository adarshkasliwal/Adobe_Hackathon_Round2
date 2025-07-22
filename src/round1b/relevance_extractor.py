"""
Round 1B: Persona-Based Section Relevance Extraction
Extracts relevant sections based on persona and job-to-be-done
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path
import logging
import numpy as np

# Try to import sentence transformers, fallback to basic similarity
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning("sentence-transformers not available, using basic similarity")

from src.utils.pdf_utils import PDFProcessor
from src.utils.text_utils import TextProcessor

logger = logging.getLogger(__name__)


class RelevanceExtractor:
    """Extract relevant sections based on persona and job requirements"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        
        # Initialize sentence transformer if available
        self.sentence_model = None
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Use a lightweight model that fits within size constraints
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {str(e)}")
    
    def extract_relevant_sections(self, pdf_files: List[str], persona: str, job_to_be_done: str) -> Dict:
        """Extract most relevant sections for given persona and job"""
        logger.info(f"Processing {len(pdf_files)} PDFs for persona: {persona}")
        
        # Process all documents
        all_sections = []
        document_sections = {}
        
        for pdf_file in pdf_files:
            filename = Path(pdf_file).name
            logger.info(f"Processing document: {filename}")
            
            sections = self._extract_document_sections(pdf_file)
            document_sections[filename] = sections
            all_sections.extend(sections)
        
        # Rank sections by relevance
        relevant_sections = self._rank_sections_by_relevance(
            all_sections, persona, job_to_be_done
        )
        
        # Generate refined subsection analysis
        subsection_analysis = self._generate_subsection_analysis(
            relevant_sections[:10], persona, job_to_be_done
        )
        
        # Build result
        result = {
            "metadata": {
                "documents": [Path(f).name for f in pdf_files],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "page": section["page"],
                    "section_title": section["title"],
                    "importance_rank": i + 1
                }
                for i, section in enumerate(relevant_sections[:20])  # Top 20
            ],
            "sub_section_analysis": subsection_analysis
        }
        
        logger.info(f"Extracted {len(result['extracted_sections'])} relevant sections")
        return result
    
    def _extract_document_sections(self, pdf_path: str) -> List[Dict]:
        """Extract sections from a single document"""
        if not self.pdf_processor.load_pdf(pdf_path):
            logger.error(f"Cannot load PDF: {pdf_path}")
            return []
        
        try:
            sections = []
            filename = Path(pdf_path).name
            page_count = self.pdf_processor.get_page_count()
            
            for page_num in range(page_count):
                # Extract text with formatting
                formatted_text = self.pdf_processor.extract_text_with_formatting(page_num)
                plain_text = self.pdf_processor.extract_plain_text(page_num)
                
                # Find potential section titles (headings)
                headings = self._find_headings_in_page(formatted_text)
                
                # If no headings found, treat entire page as a section
                if not headings:
                    if plain_text.strip():
                        sections.append({
                            "document": filename,
                            "page": page_num + 1,
                            "title": f"Page {page_num + 1}",
                            "content": plain_text,
                            "heading_level": "content"
                        })
                else:
                    # Create sections for each heading
                    for heading in headings:
                        # Extract content around heading
                        content = self._extract_section_content(
                            plain_text, heading["text"], page_num
                        )
                        
                        sections.append({
                            "document": filename,
                            "page": page_num + 1,
                            "title": heading["text"],
                            "content": content,
                            "heading_level": heading.get("level", "H3")
                        })
            
            return sections
            
        finally:
            self.pdf_processor.close()
    
    def _find_headings_in_page(self, formatted_text: List[Dict]) -> List[Dict]:
        """Find headings in formatted text"""
        if not formatted_text:
            return []
        
        font_sizes = [item["font_size"] for item in formatted_text]
        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
        
        headings = []
        for item in formatted_text:
            if self.text_processor.is_likely_heading(
                item["text"], item["font_size"], avg_font_size
            ):
                headings.append({
                    "text": self.text_processor.clean_text(item["text"]),
                    "font_size": item["font_size"],
                    "level": "H2"  # Default level
                })
        
        return headings
    
    def _extract_section_content(self, page_text: str, heading: str, page_num: int) -> str:
        """Extract content belonging to a section"""
        # Simple approach: take surrounding text
        lines = page_text.split('\n')
        
        # Find heading line
        heading_line_idx = -1
        for i, line in enumerate(lines):
            if heading.lower() in line.lower():
                heading_line_idx = i
                break
        
        if heading_line_idx == -1:
            # Heading not found, return limited content
            return ' '.join(lines[:10])  # First 10 lines
        
        # Extract content after heading (next ~5-10 lines)
        start_idx = heading_line_idx + 1
        end_idx = min(start_idx + 10, len(lines))
        
        content_lines = lines[start_idx:end_idx]
        return ' '.join(content_lines).strip()
    
    def _rank_sections_by_relevance(self, sections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """Rank sections by relevance to persona and job"""
        if not sections:
            return []
        
        # Create query from persona and job
        query = f"{persona} {job_to_be_done}"
        
        scored_sections = []
        
        for section in sections:
            content = section.get("content", "")
            title = section.get("title", "")
            combined_text = f"{title} {content}"
            
            # Calculate relevance score
            if self.sentence_model:
                relevance_score = self._calculate_semantic_relevance(
                    query, combined_text
                )
            else:
                relevance_score = self._calculate_keyword_relevance(
                    query, combined_text
                )
            
            section_copy = section.copy()
            section_copy["relevance_score"] = relevance_score
            scored_sections.append(section_copy)
        
        # Sort by relevance score (descending)
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_sections
    
    def _calculate_semantic_relevance(self, query: str, text: str) -> float:
        """Calculate semantic relevance using sentence transformers"""
        try:
            # Encode texts
            query_embedding = self.sentence_model.encode([query])
            text_embedding = self.sentence_model.encode([text])
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding[0], text_embedding[0]) / (
                np.linalg.norm(query_embedding[0]) * np.linalg.norm(text_embedding[0])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.warning(f"Error in semantic relevance calculation: {str(e)}")
            return self._calculate_keyword_relevance(query, text)
    
    def _calculate_keyword_relevance(self, query: str, text: str) -> float:
        """Calculate relevance using keyword matching (fallback)"""
        if not query or not text:
            return 0.0
        
        # Extract keywords
        query_keywords = set(self.text_processor.extract_keywords(query.lower()))
        text_keywords = set(self.text_processor.extract_keywords(text.lower()))
        
        if not query_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_keywords.intersection(text_keywords))
        union = len(query_keywords.union(text_keywords))
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_subsection_analysis(self, top_sections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """Generate refined analysis for top sections"""
        analysis = []
        
        for section in top_sections[:10]:  # Analyze top 10 sections
            content = section.get("content", "")
            
            # Create refined text (summary/key points)
            refined_text = self._create_refined_text(
                content, persona, job_to_be_done
            )
            
            analysis.append({
                "document": section["document"],
                "page": section["page"],
                "refined_text": refined_text
            })
        
        return analysis
    
    def _create_refined_text(self, content: str, persona: str, job_to_be_done: str) -> str:
        """Create refined/summarized text for the section"""
        if not content:
            return ""
        
        # Simple approach: extract most relevant sentences
        sentences = content.split('.')
        
        # Limit to 2-3 most relevant sentences
        relevant_sentences = []
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Reasonable sentence length
                # Simple relevance check
                if any(keyword.lower() in sentence.lower() 
                       for keyword in [persona, job_to_be_done]):
                    relevant_sentences.append(sentence)
        
        if not relevant_sentences:
            # Fallback: first few sentences
            relevant_sentences = [s.strip() for s in sentences[:2] if len(s.strip()) > 20]
        
        # Combine and limit length
        refined = '. '.join(relevant_sentences[:3])
        
        # Ensure reasonable length
        if len(refined) > 300:
            refined = refined[:300] + "..."
        
        return refined
    
    def save_result(self, result: Dict, output_path: str):
        """Save extraction result to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved relevance analysis to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            raise