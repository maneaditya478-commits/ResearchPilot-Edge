"""
ResearchPilot Edge - Document Cleaner
Normalizes extracted text while preserving structural markers (headings, lists, equations).
"""

import re
from typing import List, Tuple

class DocumentCleaner:
    """Cleans and standardizes raw text extracted from academic and technical documents."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes extraneous whitespace, fix broken hyphenations, and normalizes line breaks."""
        if not text:
            return ""
        
        # Replace non-breaking spaces and unicode spaces with standard space
        text = text.replace("\u00a0", " ").replace("\u200b", "")
        
        # Rejoin hyphenated words broken across line breaks (e.g., "archi-\ntecture" -> "architecture")
        text = re.sub(r'(\w+)-\n\s*(\w+)', r'\1\2', text)
        
        # Replace multiple consecutive newlines with double newline to preserve paragraphs
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple horizontal spaces/tabs with single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Strip trailing and leading whitespace on lines
        lines = [line.strip() for line in text.split('\n')]
        cleaned = '\n'.join(lines)
        
        return cleaned.strip()

    @staticmethod
    def detect_headings(text: str) -> List[Tuple[str, int]]:
        """
        Detects potential section headings (e.g., '1. Introduction', 'Abstract', '3. Methodology').
        Returns a list of (heading_title, character_offset).
        """
        heading_patterns = [
            r'^(?:[0-9]+\.|\b[IVXLCDM]+\.)\s+[A-Z][A-Za-z0-9\s,\-:]{2,60}$',
            r'^(?:ABSTRACT|INTRODUCTION|RELATED WORK|METHODOLOGY|EXPERIMENTS|RESULTS|DISCUSSION|CONCLUSION|REFERENCES|LIMITATIONS|DATASET)\b.*$'
        ]
        
        headings = []
        for match in re.finditer(r'^([^\n]+)$', text, re.MULTILINE):
            line = match.group(1).strip()
            for pattern in heading_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    headings.append((line, match.start()))
                    break
        return headings
