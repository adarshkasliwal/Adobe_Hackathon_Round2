#!/usr/bin/env python3
"""
Adobe India Hackathon - Document Intelligence Challenge
Main entry point for both Round 1A and Round 1B
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.round1a.outline_extractor import OutlineExtractor
from src.round1b.relevance_extractor import RelevanceExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_round1a(input_dir: str, output_dir: str):
    """Execute Round 1A: Structured PDF Outline Extraction"""
    logger.info("Starting Round 1A: Structured PDF Outline Extraction")
    
    extractor = OutlineExtractor()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process all PDF files in input directory
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            result = extractor.extract_outline(str(pdf_file))
            
            # Save result as JSON
            output_file = output_path / f"{pdf_file.stem}.json"
            extractor.save_result(result, str(output_file))
            
            logger.info(f"Completed: {pdf_file.name} -> {output_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")


def run_round1b(input_dir: str, output_dir: str, persona: str, job_to_be_done: str):
    """Execute Round 1B: Persona-Based Section Relevance Extraction"""
    logger.info("Starting Round 1B: Persona-Based Section Relevance Extraction")
    
    extractor = RelevanceExtractor()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    logger.info(f"Persona: {persona}")
    logger.info(f"Job to be done: {job_to_be_done}")
    
    try:
        # Process all PDFs together for relevance extraction
        result = extractor.extract_relevant_sections(
            pdf_files=[str(f) for f in pdf_files],
            persona=persona,
            job_to_be_done=job_to_be_done
        )
        
        # Save result as JSON
        output_file = output_path / "relevance_analysis.json"
        extractor.save_result(result, str(output_file))
        
        logger.info(f"Completed relevance analysis -> {output_file.name}")
        
    except Exception as e:
        logger.error(f"Error in relevance extraction: {str(e)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Adobe Hackathon Document Intelligence')
    parser.add_argument('--round', choices=['1a', '1b'], default='1a', 
                       help='Which round to execute (default: 1a)')
    parser.add_argument('--input', default='/app/input', 
                       help='Input directory path (default: /app/input)')
    parser.add_argument('--output', default='/app/output', 
                       help='Output directory path (default: /app/output)')
    parser.add_argument('--persona', default='Research Analyst',
                       help='Persona for Round 1B (default: Research Analyst)')
    parser.add_argument('--job', default='Extract key insights from documents',
                       help='Job to be done for Round 1B')
    
    args = parser.parse_args()
    
    # Check if running in Docker environment
    if not os.path.exists(args.input):
        logger.error(f"Input directory not found: {args.input}")
        return 1
    
    try:
        if args.round == '1a':
            run_round1a(args.input, args.output)
        elif args.round == '1b':
            run_round1b(args.input, args.output, args.persona, args.job)
        
        logger.info("Processing completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())