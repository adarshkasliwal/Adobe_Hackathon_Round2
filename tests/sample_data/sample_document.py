"""
Generate sample PDF for testing purposes
"""

from reportlab.lib.pagesizes import letter
from reportlab.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os


def create_sample_pdf():
    """Create a sample PDF with clear heading hierarchy for testing"""
    
    output_path = os.path.join(os.path.dirname(__file__), "sample_test_document.pdf")
    
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles for headings
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # Center
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'], 
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=8
    )
    
    # Document content
    story.append(Paragraph("Sample Document for Testing", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Introduction section
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph("This is a sample document created for testing the Adobe Hackathon Document Intelligence solution. It contains various heading levels and content to validate the extraction algorithms.", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("1.1 Background", h2_style))
    story.append(Paragraph("The document intelligence challenge requires accurate extraction of structured information from PDF documents. This includes identifying titles, headings, and content hierarchy.", styles['Normal']))
    
    story.append(Paragraph("1.1.1 Objectives", h3_style))
    story.append(Paragraph("The primary objectives include: (1) Extract document title accurately, (2) Identify heading hierarchy with correct levels, (3) Provide page numbers for each section.", styles['Normal']))
    
    # Methodology section 
    story.append(PageBreak())
    story.append(Paragraph("2. Methodology", h1_style))
    story.append(Paragraph("This section describes the approach used for document processing and information extraction. The methodology combines multiple techniques for robust performance.", styles['Normal']))
    
    story.append(Paragraph("2.1 PDF Processing", h2_style))
    story.append(Paragraph("We utilize PyMuPDF and pdfplumber libraries for comprehensive PDF text extraction. These libraries provide both structural and textual information necessary for accurate analysis.", styles['Normal']))
    
    story.append(Paragraph("2.1.1 Text Extraction", h3_style))
    story.append(Paragraph("Text extraction involves parsing PDF structure while preserving formatting information such as font sizes, styles, and positioning data.", styles['Normal']))
    
    story.append(Paragraph("2.1.2 Font Analysis", h3_style))
    story.append(Paragraph("Font analysis helps identify heading hierarchy by examining relative font sizes, bold formatting, and other stylistic indicators.", styles['Normal']))
    
    story.append(Paragraph("2.2 Natural Language Processing", h2_style))
    story.append(Paragraph("NLP techniques are employed for semantic understanding and relevance analysis. This includes keyword extraction, similarity calculation, and context analysis.", styles['Normal']))
    
    # Results section
    story.append(PageBreak())
    story.append(Paragraph("3. Results and Analysis", h1_style))
    story.append(Paragraph("The experimental results demonstrate the effectiveness of our approach across various document types and structures.", styles['Normal']))
    
    story.append(Paragraph("3.1 Performance Metrics", h2_style))
    story.append(Paragraph("Performance evaluation includes processing time, accuracy measurements, and resource utilization analysis. All metrics meet the specified hackathon requirements.", styles['Normal']))
    
    story.append(Paragraph("3.2 Accuracy Assessment", h2_style))
    story.append(Paragraph("Accuracy assessment involves comparing extracted headings with manually annotated ground truth data. The system achieves high precision and recall rates.", styles['Normal']))
    
    # Conclusion
    story.append(Paragraph("4. Conclusion", h1_style))
    story.append(Paragraph("This document serves as a comprehensive test case for validating document intelligence algorithms. The structured format with clear heading hierarchy enables thorough testing of extraction capabilities.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"Sample PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_sample_pdf()