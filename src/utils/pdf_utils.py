"""
PDF processing utilities
"""

import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Enhanced PDF processor with multiple extraction methods"""
    
    def __init__(self):
        self.doc = None
    
    def load_pdf(self, pdf_path: str) -> bool:
        """Load PDF document"""
        try:
            self.doc = fitz.open(pdf_path)
            return True
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path}: {str(e)}")
            return False
    
    def get_page_count(self) -> int:
        """Get total number of pages"""
        if self.doc:
            return len(self.doc)
        return 0
    
    def extract_text_with_formatting(self, page_num: int) -> List[Dict]:
        """Extract text with font information for heading detection"""
        if not self.doc or page_num >= len(self.doc):
            return []
        
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        formatted_text = []
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        formatted_text.append({
                            "text": text,
                            "font_size": span["size"],
                            "font_flags": span["flags"],
                            "font_name": span["font"],
                            "bbox": span["bbox"],
                            "page": page_num + 1
                        })
        
        return formatted_text
    
    def extract_plain_text(self, page_num: int) -> str:
        """Extract plain text from page"""
        if not self.doc or page_num >= len(self.doc):
            return ""
        
        page = self.doc[page_num]
        return page.get_text()
    
    def extract_all_text(self) -> str:
        """Extract all text from document"""
        if not self.doc:
            return ""
        
        full_text = ""
        for page_num in range(len(self.doc)):
            full_text += self.extract_plain_text(page_num) + "\n"
        
        return full_text
    
    def detect_document_title(self) -> Optional[str]:
        """Detect document title using multiple heuristics"""
        if not self.doc:
            return None
        
        # Try first page for title
        first_page_text = self.extract_text_with_formatting(0)
        
        if not first_page_text:
            return None
        
        # Find largest font size on first page
        max_font_size = max(item["font_size"] for item in first_page_text)
        
        # Find text with largest font size (likely title)
        title_candidates = []
        for item in first_page_text:
            if item["font_size"] == max_font_size:
                title_candidates.append(item["text"])
        
        # Return first title candidate or combine multiple
        if title_candidates:
            return " ".join(title_candidates[:2])  # Take first 2 parts max
        
        # Fallback: use first non-empty line
        for item in first_page_text:
            if len(item["text"]) > 10:  # Reasonable title length
                return item["text"]
        
        return "Untitled Document"
    
    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()
            self.doc = None


class PDFTextExtractor:
    """Alternative PDF text extractor using pdfplumber"""
    
    @staticmethod
    def extract_with_pdfplumber(pdf_path: str) -> Dict:
        """Extract text using pdfplumber for better structure detection"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append({
                            "page_number": i + 1,
                            "text": page_text,
                            "chars": page.chars,  # Character-level details
                            "lines": page.extract_text_lines() if hasattr(page, 'extract_text_lines') else []
                        })
                
                return {
                    "pages": pages_text,
                    "total_pages": len(pdf.pages)
                }
                
        except Exception as e:
            logger.error(f"Error extracting with pdfplumber: {str(e)}")
            return {"pages": [], "total_pages": 0}