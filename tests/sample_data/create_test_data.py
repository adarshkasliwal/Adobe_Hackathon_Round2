"""
Create sample test data for both rounds
"""

import json
import os
from pathlib import Path


def create_sample_input_data():
    """Create sample expected outputs for testing"""
    
    # Create directories
    base_dir = Path(__file__).parent
    expected_dir = base_dir / "expected_output"
    expected_dir.mkdir(exist_ok=True)
    
    # Round 1A expected output
    round1a_expected = {
        "title": "Sample Document for Testing",
        "outline": [
            {"level": "H1", "text": "1. Introduction", "page": 1},
            {"level": "H2", "text": "1.1 Background", "page": 1},
            {"level": "H3", "text": "1.1.1 Objectives", "page": 1},
            {"level": "H1", "text": "2. Methodology", "page": 2},
            {"level": "H2", "text": "2.1 PDF Processing", "page": 2},
            {"level": "H3", "text": "2.1.1 Text Extraction", "page": 2},
            {"level": "H3", "text": "2.1.2 Font Analysis", "page": 2},
            {"level": "H2", "text": "2.2 Natural Language Processing", "page": 2},
            {"level": "H1", "text": "3. Results and Analysis", "page": 3},
            {"level": "H2", "text": "3.1 Performance Metrics", "page": 3},
            {"level": "H2", "text": "3.2 Accuracy Assessment", "page": 3},
            {"level": "H1", "text": "4. Conclusion", "page": 3}
        ]
    }
    
    # Save Round 1A expected output
    with open(expected_dir / "sample_test_document.json", "w") as f:
        json.dump(round1a_expected, f, indent=2)
    
    # Round 1B expected output
    round1b_expected = {
        "metadata": {
            "documents": ["sample_test_document.pdf"],
            "persona": "Research Analyst",
            "job_to_be_done": "Extract methodology insights",
            "timestamp": "2025-01-22T12:00:00Z"
        },
        "extracted_sections": [
            {
                "document": "sample_test_document.pdf",
                "page": 2,
                "section_title": "2. Methodology",
                "importance_rank": 1
            },
            {
                "document": "sample_test_document.pdf", 
                "page": 2,
                "section_title": "2.1 PDF Processing",
                "importance_rank": 2
            },
            {
                "document": "sample_test_document.pdf",
                "page": 2,
                "section_title": "2.2 Natural Language Processing",
                "importance_rank": 3
            }
        ],
        "sub_section_analysis": [
            {
                "document": "sample_test_document.pdf",
                "page": 2,
                "refined_text": "This section describes the approach used for document processing and information extraction. The methodology combines multiple techniques for robust performance."
            },
            {
                "document": "sample_test_document.pdf",
                "page": 2, 
                "refined_text": "We utilize PyMuPDF and pdfplumber libraries for comprehensive PDF text extraction. These libraries provide both structural and textual information."
            }
        ]
    }
    
    # Save Round 1B expected output
    with open(expected_dir / "relevance_analysis_expected.json", "w") as f:
        json.dump(round1b_expected, f, indent=2)
    
    print("Sample test data created successfully!")
    print(f"Expected outputs saved to: {expected_dir}")


if __name__ == "__main__":
    create_sample_input_data()