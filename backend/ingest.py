#!/usr/bin/env python3
"""
Knowledge base ingestion script.
Loads PDFs from data/knowledge_base/, chunks them, and stores embeddings in Chroma.

Usage:
    python ingest.py                        # Ingest from default directory
    python ingest.py --dir /path/to/pdfs   # Custom directory
    python ingest.py --reset               # Reset existing collection first
"""
import os
import sys
import argparse

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.knowledge_base import KnowledgeBase


def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs into Chroma knowledge base")
    parser.add_argument(
        "--dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "knowledge_base"),
        help="Directory containing PDF files to ingest",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the Chroma collection before ingesting",
    )
    args = parser.parse_args()

    pdf_dir = args.dir

    if not os.path.isdir(pdf_dir):
        print(f"❌ Directory not found: {pdf_dir}")
        print(f"   Please create it and place your PDF files inside.")
        print(f"   mkdir -p '{pdf_dir}'")
        sys.exit(1)

    # Check for PDFs
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"⚠️  No PDF files found in {pdf_dir}")
        print(f"   Place your knowledge base PDFs in this directory and re-run.")
        print(f"   Example PDFs to include: ML books, technical documentation, etc.")
        sys.exit(0)

    print(f"📄 Found {len(pdf_files)} PDF files in {pdf_dir}:")
    for f in pdf_files:
        print(f"   - {f}")

    # Initialize knowledge base
    kb = KnowledgeBase()

    # Reset if requested
    if args.reset:
        import shutil
        persist_dir = settings.CHROMA_PERSIST_DIR
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"🗑️  Removed existing Chroma data at {persist_dir}")

    # Ingest PDFs
    print(f"\n⚙️  Initializing knowledge base...")
    kb.initialize()

    print(f"\n📚 Ingesting PDFs...")
    count = kb.ingest_pdfs(pdf_dir)

    if count > 0:
        print(f"\n✅ Successfully ingested {count} chunks into Chroma!")
    else:
        print(f"\n⚠️  No chunks were ingested. Check the PDF files and try again.")


if __name__ == "__main__":
    main()