"""
Document Processing Pipeline
Handles document ingestion, screenshot generation, vision analysis, and vectorization
"""
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
import pandas as pd

from app.services.llm_service import llm_service
from app.services.vision_service import vision_service
from app.services.pgvector_service import pgvector_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Document processing pipeline with vision model integration
    """

    def __init__(self):
        self.screenshot_dir = Path("./screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    def process_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main pipeline: Extract text, generate screenshots, analyze with vision model, vectorize

        Returns:
            Dict with status and processed document info
        """
        try:
            file_path = Path(file_path)
            file_type = file_path.suffix.lower()

            logger.info(f"Processing document: {file_path.name}")

            # Extract text content
            text_content = self._extract_text(file_path, file_type)

            # Generate screenshots (for visual context)
            screenshots = self._generate_screenshots(file_path, file_type)

            # Analyze screenshots with vision model
            vision_analysis = []
            for screenshot_path in screenshots:
                analysis = vision_service.analyze_document_image(screenshot_path)
                vision_analysis.append(analysis)

            # Generate enhanced summary using vision + text
            enhanced_summary = self._generate_enhanced_summary(
                text_content,
                vision_analysis
            )

            # Chunk text for better retrieval
            chunks = self._chunk_text(text_content)

            # Generate embeddings and store in pgvector
            stored_docs = []
            for i, chunk in enumerate(chunks):
                # Get or generate embedding
                embedding = self._get_embedding(chunk)

                # Prepare metadata
                doc_metadata = {
                    'source': file_path.name,
                    'type': file_type[1:],  # Remove dot
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    **(metadata or {})
                }

                # Determine which screenshot to associate
                screenshot_idx = min(i, len(screenshots) - 1)
                screenshot_path = screenshots[screenshot_idx] if screenshots else None

                # Store in pgvector
                success = pgvector_service.add_document(
                    content=chunk,
                    embedding=embedding,
                    metadata=doc_metadata,
                    summary=enhanced_summary if i == 0 else None,
                    screenshot_path=str(screenshot_path) if screenshot_path else None
                )

                if success:
                    stored_docs.append({
                        'chunk_index': i,
                        'screenshot': str(screenshot_path) if screenshot_path else None
                    })

            logger.info(f"Successfully processed {file_path.name}: {len(stored_docs)} chunks")

            return {
                'status': 'success',
                'file': file_path.name,
                'chunks': len(chunks),
                'screenshots': len(screenshots),
                'enhanced_summary': enhanced_summary,
                'vision_insights': [a.get('summary') for a in vision_analysis]
            }

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}", exc_info=True)
            return {
                'status': 'error',
                'file': str(file_path),
                'error': str(e)
            }

    def batch_process_documents(
        self,
        file_paths: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple documents in batch for better performance"""
        results = []
        for i, file_path in enumerate(file_paths):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
            result = self.process_document(file_path, metadata)
            results.append(result)
        return results

    def _extract_text(self, file_path: Path, file_type: str) -> str:
        """Extract text content from various document types"""
        try:
            if file_type == '.pdf':
                reader = PdfReader(str(file_path))
                text = "\n\n".join([page.extract_text() for page in reader.pages])

            elif file_type in ['.docx', '.doc']:
                doc = Document(str(file_path))
                text = "\n\n".join([para.text for para in doc.paragraphs])

            elif file_type in ['.pptx', '.ppt']:
                prs = Presentation(str(file_path))
                text_parts = []
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            text_parts.append(shape.text)
                text = "\n\n".join(text_parts)

            elif file_type in ['.xlsx', '.xls', '.csv']:
                if file_type == '.csv':
                    df = pd.read_csv(str(file_path))
                else:
                    df = pd.read_excel(str(file_path))
                text = df.to_string()

            else:
                # Plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()

            return text

        except Exception as e:
            logger.error(f"Text extraction error for {file_path}: {e}")
            return ""

    def _generate_screenshots(self, file_path: Path, file_type: str) -> List[Path]:
        """Generate screenshots from documents"""
        screenshots = []

        try:
            if file_type == '.pdf':
                # Convert PDF pages to images
                images = convert_from_path(
                    str(file_path),
                    dpi=150,  # Balance between quality and size
                    fmt='png'
                )

                for i, image in enumerate(images[:10]):  # Limit to first 10 pages
                    screenshot_name = f"{file_path.stem}_page{i+1}.png"
                    screenshot_path = self.screenshot_dir / screenshot_name
                    image.save(screenshot_path, 'PNG', optimize=True)
                    screenshots.append(screenshot_path)

            elif file_type in ['.pptx', '.ppt']:
                # For PPT, would need additional library like python-pptx with pillow
                # Placeholder: would implement slide-to-image conversion
                logger.info(f"Screenshot generation for {file_type} not fully implemented yet")

            # For other types, could generate preview images if needed

        except Exception as e:
            logger.error(f"Screenshot generation error for {file_path}: {e}")

        return screenshots

    def _generate_enhanced_summary(
        self,
        text_content: str,
        vision_analysis: List[Dict[str, Any]]
    ) -> str:
        """Generate enhanced summary combining text and vision analysis"""
        # Combine text and vision insights
        text_summary = text_content[:500]  # First 500 chars

        vision_insights = []
        for analysis in vision_analysis:
            if analysis.get('summary'):
                vision_insights.append(analysis['summary'])
            if analysis.get('key_points'):
                vision_insights.extend(analysis['key_points'][:2])  # Top 2 points

        combined = f"{text_summary}\n\n시각적 분석:\n" + "\n".join(f"- {insight}" for insight in vision_insights[:5])

        return combined

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks with overlap for better context preservation

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for sep in ['. ', '.\n', '! ', '?\n']:
                    last_sep = text[start:end].rfind(sep)
                    if last_sep > chunk_size * 0.7:  # At least 70% of chunk size
                        end = start + last_sep + len(sep)
                        break

            chunks.append(text[start:end].strip())
            start = end - overlap

        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding with caching"""
        # Check cache first
        cached = cache_service.get_cached_embedding(text)
        if cached:
            return cached

        # Generate new embedding
        embedding = llm_service.get_embedding(text)

        # Cache it
        if embedding:
            cache_service.cache_embedding(text, embedding)

        return embedding or []


# Global instance
document_processor = DocumentProcessor()
