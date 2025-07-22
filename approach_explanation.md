# Approach Explanation: Adobe India Hackathon Document Intelligence Challenge

## Overview

This solution tackles two distinct challenges in document intelligence: structured outline extraction and persona-based relevance analysis. The approach emphasizes offline processing, computational efficiency, and production-grade reliability.

## Round 1A: Structured PDF Outline Extraction

### Core Strategy

Our outline extraction employs a **multi-layered font analysis approach** combined with **contextual text pattern recognition**. Rather than relying on external APIs or large models, we leverage the inherent structure of PDF documents.

#### Technical Implementation

**Font-Based Hierarchy Detection**: We analyze font sizes, styles, and formatting flags to establish heading hierarchy. The algorithm:
1. Extracts all text with formatting metadata using PyMuPDF
2. Calculates statistical measures (mean, variance) of font sizes
3. Identifies outlier font sizes that likely represent headings
4. Maps font sizes to H1/H2/H3 levels using relative ranking

**Pattern Recognition**: Beyond font analysis, we employ regex patterns to catch common heading formats:
- Numbered sections (1., 1.1, Chapter 1)
- Capitalized headers (INTRODUCTION, METHODOLOGY)  
- Structural indicators (colons, bullet points)

**Title Detection**: Document titles are identified through multiple heuristics:
- Largest font size on first page
- Positioning (top-center alignment)
- Length constraints (reasonable title length)
- Formatting emphasis (bold, distinct font)

### Performance Optimizations

- **Streaming Processing**: Pages processed individually to minimize memory usage
- **Early Termination**: Stops processing when sufficient headings are found
- **Font Caching**: Reuses font analysis across pages for consistency
- **Text Preprocessing**: Efficient cleaning reduces downstream processing

## Round 1B: Persona-Based Section Relevance Extraction

### Semantic Relevance Framework

This challenge requires understanding context and relevance rather than just structure. Our approach combines **semantic similarity** with **keyword-based ranking**.

#### Core Components

**Document Segmentation**: Each PDF is broken into logical sections:
- Heading-based sections when clear structure exists
- Page-based sections for unstructured documents  
- Paragraph-level granularity for detailed analysis

**Relevance Scoring**: Multi-faceted scoring mechanism:
1. **Semantic Similarity**: Using sentence-transformers (all-MiniLM-L6-v2) to encode persona/job queries and document sections
2. **Keyword Matching**: TF-IDF style matching for explicit term relevance
3. **Context Weighting**: Sections near relevant content receive boost scores
4. **Length Normalization**: Prevents bias toward longer or shorter sections

**Persona Understanding**: The system builds a composite query by combining:
- Persona-specific domain knowledge (Research Analyst → financial terms)
- Job-specific action words (analyze → quantitative focus)
- Contextual term expansion using semantic relationships

### Advanced Features

**Multi-Document Correlation**: Sections are ranked not just individually but in relation to content across all provided documents. This enables identification of themes that span multiple sources.

**Refined Text Generation**: For the top-ranked sections, we generate concise summaries that:
- Extract key sentences most relevant to the persona/job
- Maintain original context while improving readability
- Limit length to essential information (200-300 characters)

## Technical Architecture

### Modular Design

The solution follows **separation of concerns** with distinct modules:
- `pdf_utils.py`: Handles all PDF parsing and text extraction
- `text_utils.py`: Manages NLP operations and text analysis
- Round-specific extractors: Implement business logic for each challenge

### Resource Management

**Memory Efficiency**: 
- Process documents one at a time
- Release resources immediately after use
- Stream large texts rather than loading entirely

**CPU Optimization**:
- Vectorized operations where possible  
- Efficient string processing with compiled regex
- Minimal model loading (single transformer model for Round 1B)

**Model Selection**: Chose all-MiniLM-L6-v2 for optimal balance of:
- Size constraint compliance (<1GB total)
- Semantic understanding capability
- CPU inference speed
- Multilingual support foundation

## Offline Capability

### No External Dependencies

The solution operates entirely offline through:
- Local model inference (sentence transformers)
- Pre-downloaded language models (spaCy)
- Built-in PDF processing libraries
- Self-contained similarity calculations

### Robustness

**Error Handling**: Comprehensive exception management ensures partial failures don't crash processing:
- PDF parsing errors fall back to alternative extraction methods
- Missing models gracefully degrade to keyword-based approaches
- File system errors are logged and processing continues

**Fallback Mechanisms**: Multiple backup strategies:
- PyMuPDF fails → pdfplumber extraction
- Semantic similarity unavailable → keyword matching
- Heading detection fails → page-based sections

## Innovation Aspects

### Adaptive Hierarchy Detection

Rather than fixed rules, our heading detection adapts to each document's font distribution. This handles diverse document styles without manual tuning.

### Context-Aware Relevance

Round 1B doesn't just match keywords but understands semantic relationships between personas, jobs, and document content. A "Research Analyst" query will match sections about "data analysis" or "quantitative methods" even without exact term matches.

### Production Readiness

The solution includes comprehensive logging, performance monitoring, and graceful degradation - essential for real-world deployment scenarios.

## Results & Validation

This approach successfully balances accuracy with performance constraints, providing reliable extraction within the specified time limits while maintaining high relevance scores for persona-based analysis. The modular architecture enables easy extension for additional document types or analysis requirements.