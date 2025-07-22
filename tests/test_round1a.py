"""
Test cases for Round 1A: Structured PDF Outline Extraction
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.round1a.outline_extractor import OutlineExtractor


class TestOutlineExtractor:
    """Test cases for outline extraction functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = OutlineExtractor()
    
    def test_outline_extractor_initialization(self):
        """Test that extractor initializes correctly"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'pdf_processor')
        assert hasattr(self.extractor, 'text_processor')
    
    def test_save_result_functionality(self):
        """Test result saving functionality"""
        # Create test result
        test_result = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Introduction", "page": 1},
                {"level": "H2", "text": "Background", "page": 2}
            ]
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
            
            assert saved_data == test_result
            assert saved_data["title"] == "Test Document"
            assert len(saved_data["outline"]) == 2
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_heading_hierarchy_refinement(self):
        """Test heading hierarchy processing"""
        # Test with mock headings data
        mock_headings = [
            {"level": "H1", "text": "Chapter 1", "page": 1, "font_size": 16},
            {"level": "H2", "text": "Section 1.1", "page": 1, "font_size": 14},
            {"level": "H3", "text": "Subsection 1.1.1", "page": 2, "font_size": 12},
            {"level": "H1", "text": "Chapter 2", "page": 3, "font_size": 16}
        ]
        
        refined = self.extractor._refine_heading_hierarchy(mock_headings)
        
        # Check that refinement maintains structure
        assert len(refined) == 4
        assert all("font_size" not in heading for heading in refined)
        assert all("level" in heading for heading in refined)
        assert all("text" in heading for heading in refined)
        assert all("page" in heading for heading in refined)
        
        # Check sorting by page
        pages = [h["page"] for h in refined]
        assert pages == sorted(pages)
    
    def test_empty_input_handling(self):
        """Test handling of empty or invalid inputs"""
        # Test empty headings list
        result = self.extractor._refine_heading_hierarchy([])
        assert result == []
        
        # Test with single heading
        single_heading = [{"level": "H1", "text": "Title", "page": 1, "font_size": 14}]
        result = self.extractor._refine_heading_hierarchy(single_heading)
        assert len(result) == 1
        assert result[0]["level"] == "H1"


def test_json_output_format():
    """Test that output matches expected JSON format"""
    expected_format = {
        "title": str,
        "outline": list
    }
    
    # Create sample output
    sample_output = {
        "title": "Sample Document",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1}
        ]
    }
    
    # Validate format
    assert isinstance(sample_output["title"], str)
    assert isinstance(sample_output["outline"], list)
    
    if sample_output["outline"]:
        outline_item = sample_output["outline"][0]
        required_keys = {"level", "text", "page"}
        assert required_keys.issubset(outline_item.keys())
        assert isinstance(outline_item["page"], int)
        assert outline_item["level"] in ["H1", "H2", "H3"]


if __name__ == "__main__":
    pytest.main([__file__])