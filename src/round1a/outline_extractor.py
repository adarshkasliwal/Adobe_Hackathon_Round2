"""
Round 1A: Structured PDF Outline Extraction
Extracts title and heading hierarchy from PDF documents
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

from src.utils.pdf_utils import PDFProcessor
from src.utils.text_utils import TextProcessor

logger = logging.getLogger(__name__)


class OutlineExtractor:
    """Extract structured outline from PDF documents"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract title and heading hierarchy from PDF"""
        logger.info(f"Extracting outline from: {pdf_path}")
        
        # Load PDF
        if not self.pdf_processor.load_pdf(pdf_path):
            raise ValueError(f"Cannot load PDF: {pdf_path}")
        
        try:
            # Extract title
            title = self.pdf_processor.detect_document_title()
            if not title:
                title = Path(pdf_path).stem
            
            # Extract headings
            outline = self._extract_headings()
            
            result = {
                "title": title,
                "outline": outline
            }
            
            logger.info(f"Extracted {len(outline)} headings from {pdf_path}")
            return result
            
        finally:
            self.pdf_processor.close()
    
    def _extract_headings(self) -> List[Dict]:
        """Extract headings with hierarchy from all pages"""
        all_headings = []
        all_font_sizes = []
        
        # First pass: collect all text with formatting info
        page_count = self.pdf_processor.get_page_count()
        
        for page_num in range(page_count):
            formatted_text = self.pdf_processor.extract_text_with_formatting(page_num)
            
            for item in formatted_text:
                all_font_sizes.append(item["font_size"])
        
        # Calculate average font size
        avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12
        
        # Second pass: identify headings
        heading_font_sizes = []
        
        for page_num in range(page_count):
            formatted_text = self.pdf_processor.extract_text_with_formatting(page_num)
            
            for item in formatted_text:
                text = item["text"]
                font_size = item["font_size"]
                
                # Check if this looks like a heading
                if self.text_processor.is_likely_heading(text, font_size, avg_font_size):
                    heading_font_sizes.append(font_size)
                    
                    # Classify heading level
                    level = self.text_processor.classify_heading_level(
                        text, font_size, heading_font_sizes
                    )
                    
                    all_headings.append({
                        "level": level,
                        "text": self.text_processor.clean_text(text),
                        "page": page_num + 1,
                        "font_size": font_size
                    })
        
        # Post-process headings to ensure proper hierarchy
        return self._refine_heading_hierarchy(all_headings)
    
    def _refine_heading_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """Refine heading hierarchy based on font sizes and content"""
        if not headings:
            return []
        
        # Sort by font size (largest first) to establish hierarchy
        unique_font_sizes = sorted(list(set(h["font_size"] for h in headings)), reverse=True)
        
        # Create font size to level mapping
        font_to_level = {}
        for i, font_size in enumerate(unique_font_sizes[:3]):  # Only H1, H2, H3
            if i == 0:
                font_to_level[font_size] = "H1"
            elif i == 1:
                font_to_level[font_size] = "H2"
            else:
                font_to_level[font_size] = "H3"
        
        # Apply refined levels
        refined_headings = []
        for heading in headings:
            heading["level"] = font_to_level.get(heading["font_size"], "H3")
            # Remove font_size from final output
            refined_headings.append({
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"]
            })
        
        # Sort by page number
        refined_headings.sort(key=lambda x: x["page"])
        
        # Limit to reasonable number of headings
        return refined_headings[:50]  # Max 50 headings
    
    def save_result(self, result: Dict, output_path: str):
        """Save extraction result to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved outline to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            raise