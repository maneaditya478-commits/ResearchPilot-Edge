"""
ResearchPilot Edge - Demo Setup Utility
Populates the local vector database with synthetic research papers for immediate judge demonstration.

Usage:
    python scripts/setup_demo.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.backend.service import service
from app.core.logger import logger

def main():
    print("=" * 70)
    print(" ResearchPilot Edge -- Initializing Demo Dataset")
    print("=" * 70)

    print("Ingesting pre-packaged research papers into local vector database...")
    results = service.load_demo_dataset()

    if not results:
        print("Note: Demo papers are already indexed or no new files were found.")
    else:
        for r in results:
            print(f"  [+] Ingested '{r['document']}': {r['pages']} pages, {r['chunks']} chunks in {r['duration_sec']}s")

    doc_list = service.vector_store.get_document_list()
    print("\n--- Current Indexed Document Library ---")
    for doc in doc_list:
        print(f"  * {doc['document']:<55} | Pages: {doc['page_count']:<3} | Chunks: {doc['chunk_count']:<3}")

    print(f"\nTotal Chunks in Local Vector Database: {service.vector_store.total_chunks}")
    print("=" * 70)
    print("Demo dataset is ready! You can now launch the web application with:")
    print("  python run.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
