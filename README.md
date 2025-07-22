# Adobe India Hackathon - Document Intelligence Challenge

A complete production-ready solution for extracting structured information from PDF documents, designed for the Adobe India Hackathon Document Intelligence Challenge.

## 🚀 Features

### Round 1A: Structured PDF Outline Extraction
- Extracts document title and heading hierarchy (H1, H2, H3)
- Provides page numbers for each heading
- Processes PDFs up to 50 pages in under 10 seconds
- Works entirely offline with no external API dependencies

### Round 1B: Persona-Based Section Relevance Extraction  
- Analyzes 3-10 related PDFs for persona-specific content
- Ranks sections by relevance to given persona and job-to-be-done
- Provides refined subsection analysis
- Supports multilingual content detection

## 🏗️ Architecture

```
/
├── Dockerfile                 # Production container setup
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
├── src/
│   ├── round1a/             # Round 1A implementation
│   │   └── outline_extractor.py
│   ├── round1b/             # Round 1B implementation  
│   │   └── relevance_extractor.py
│   └── utils/               # Shared utilities
│       ├── pdf_utils.py     # PDF processing
│       └── text_utils.py    # Text analysis
└── tests/                   # Test cases
```

## 🛠️ Technologies Used

- **PDF Processing**: PyMuPDF, pdfplumber
- **NLP**: spaCy, sentence-transformers
- **Text Analysis**: Custom algorithms for heading detection
- **Semantic Similarity**: sentence-transformers (all-MiniLM-L6-v2)
- **Container**: Docker with multi-stage builds

## 📦 Installation & Usage

### Prerequisites
- Docker
- Input PDFs in `./input/` directory

### Quick Start

1. **Build the Docker image:**
```bash
docker build --platform linux/amd64 -t adobe-hackathon:latest .
```

2. **Run Round 1A (Outline Extraction):**
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe-hackathon:latest \
  python main.py --round 1a
```

3. **Run Round 1B (Relevance Extraction):**
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe-hackathon:latest \
  python main.py --round 1b \
  --persona "PhD Researcher in Computational Biology" \
  --job "Summarize literature review for Graph Neural Networks"
```

### Advanced Usage

```bash
# Custom input/output directories
docker run --rm \
  -v /path/to/pdfs:/app/input \
  -v /path/to/results:/app/output \
  --network none \
  adobe-hackathon:latest \
  python main.py --round 1a

# Development mode (without Docker)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py --round 1a --input ./input --output ./output
```

## 📊 Output Formats

### Round 1A Output (filename.json)
```json
{
  "title": "Machine Learning in Healthcare",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background Research", "page": 2},
    {"level": "H3", "text": "Previous Studies", "page": 3}
  ]
}
```

### Round 1B Output (relevance_analysis.json)
```json
{
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
      "refined_text": "Revenue increased 18% in 2023 due to cloud services..."
    }
  ]
}
```

## ⚡ Performance

- **Round 1A**: Processes 50-page PDFs in <10 seconds
- **Round 1B**: Analyzes 3-5 documents in <60 seconds  
- **Model Size**: <200MB (Round 1A), <1GB (Round 1B)
- **CPU Only**: No GPU requirements
- **Offline**: No internet connectivity needed

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/ -v

# Test with sample data
python main.py --round 1a --input ./tests/sample_data --output ./test_output
```

## 🌐 Multilingual Support

The solution includes basic multilingual support:
- Japanese character detection
- Unicode text processing
- Extensible language detection framework

## 🔧 Customization

### Adding New Languages
```python
# In src/utils/text_utils.py
def detect_language(self, text: str) -> str:
    # Add your language detection logic
    if contains_chinese_chars(text):
        return "zh"
    return "en"
```

### Custom Heading Detection
```python
# In src/round1a/outline_extractor.py
def _custom_heading_patterns(self):
    return [
        r'^CHAPTER\s+\d+',  # CHAPTER 1
        r'^\d+\.\d+\s+',    # 1.1 format
        # Add your patterns
    ]
```

## 🚀 Production Deployment

The solution is production-ready with:
- Error handling and logging
- Resource optimization
- Memory-efficient processing
- Containerized deployment
- Modular architecture

## 📝 License

This project is created for the Adobe India Hackathon 2025.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

---

**Built for Adobe India Hackathon 2025** 🏆