"""
Test cases for Round 1B: Persona-Based Section Relevance Extraction
"""

import pytest
import json
import os
import tempfile
from datetime import datetime

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.round1b.relevance_extractor import RelevanceExtractor


class TestRelevanceExtractor:
    """Test cases for relevance extraction functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = RelevanceExtractor()
    
    def test_relevance_extractor_initialization(self):
        """Test that extractor initializes correctly"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'pdf_processor')
        assert hasattr(self.extractor, 'text_processor')
    
    def test_keyword_relevance_calculation(self):
        """Test keyword-based relevance calculation"""
        query = "financial analysis revenue growth"
        text = "The company showed strong revenue growth in Q3 with financial metrics improving"
        
        relevance = self.extractor._calculate_keyword_relevance(query, text)
        
        assert 0.0 <= relevance <= 1.0
        assert relevance > 0  # Should find some overlap
    
    def test_keyword_relevance_no_match(self):
        """Test keyword relevance with no matches"""
        query = "machine learning algorithms"
        text = "The weather was sunny and bright today"
        
        relevance = self.extractor._calculate_keyword_relevance(query, text)
        
        assert relevance == 0.0
    
    def test_refined_text_generation(self):
        """Test refined text generation"""
        content = """
        This is a long document about financial analysis.
        The revenue grew by 15% last year.
        Market conditions were favorable.
        Investment strategies proved successful.
        Weather was nice yesterday.
        """
        persona = "Financial Analyst"
        job = "Analyze revenue trends"
        
        refined = self.extractor._create_refined_text(content, persona, job)
        
        assert isinstance(refined, str)
        assert len(refined) > 0
        assert len(refined) <= 350  # Should be limited in length
    
    def test_section_ranking(self):
        """Test section ranking functionality"""
        sections = [
            {
                "document": "test.pdf",
                "page": 1,
                "title": "Financial Overview",
                "content": "Revenue analysis and growth metrics for the quarter"
            },
            {
                "document": "test.pdf", 
                "page": 2,
                "title": "Weather Report",
                "content": "Sunny skies and mild temperatures expected"
            }
        ]
        
        persona = "Financial Analyst"
        job = "Analyze revenue trends"
        
        ranked = self.extractor._rank_sections_by_relevance(sections, persona, job)
        
        assert len(ranked) == 2
        assert all("relevance_score" in section for section in ranked)
        
        # First section should be more relevant (financial content)
        assert ranked[0]["title"] == "Financial Overview"
        assert ranked[0]["relevance_score"] >= ranked[1]["relevance_score"]
    
    def test_save_result_functionality(self):
        """Test result saving functionality"""
        test_result = {
            "metadata": {
                "documents": ["test.pdf"],
                "persona": "Test Persona",
                "job_to_be_done": "Test Task",
                "timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "sub_section_analysis": []
        }
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.extractor.save_result(test_result, temp_path)
            
            # Verify file was created and contains correct data
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["metadata"]["persona"] == "Test Persona"
            assert "documents" in saved_data["metadata"]
            assert "extracted_sections" in saved_data
            assert "sub_section_analysis" in saved_data
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)


def test_output_format_compliance():
    """Test that output matches required JSON format"""
    expected_structure = {
        "metadata": {
            "documents": [],
            "persona": "",
            "job_to_be_done": "",
            "timestamp": ""
        },
        "extracted_sections": [],
        "sub_section_analysis": []
    }
    
    # Create sample output
    sample_output = {
        "metadata": {
            "documents": ["doc1.pdf", "doc2.pdf"],
            "persona": "Investment Analyst",
            "job_to_be_done": "Analyze revenue trends",
            "timestamp": "2025-01-22T12:00:00Z"
        },
        "extracted_sections": [
            {
                "document": "doc1.pdf",
                "page": 4,
                "section_title": "Revenue Growth Trends", 
                "importance_rank": 1
            }
        ],
        "sub_section_analysis": [
            {
                "document": "doc1.pdf",
                "page": 4,
                "refined_text": "Revenue increased by 18%..."
            }
        ]
    }
    
    # Validate structure
    assert set(sample_output.keys()) == set(expected_structure.keys())
    assert set(sample_output["metadata"].keys()) == set(expected_structure["metadata"].keys())
    
    # Validate data types
    assert isinstance(sample_output["metadata"]["documents"], list)
    assert isinstance(sample_output["extracted_sections"], list)
    assert isinstance(sample_output["sub_section_analysis"], list)
    
    # Validate extracted sections format if present
    if sample_output["extracted_sections"]:
        section = sample_output["extracted_sections"][0]
        required_keys = {"document", "page", "section_title", "importance_rank"}
        assert required_keys.issubset(section.keys())
        assert isinstance(section["page"], int)
        assert isinstance(section["importance_rank"], int)


if __name__ == "__main__":
    pytest.main([__file__])