"""
Document registry builder for SSP document automation pipeline.

Scans drafts directory and builds comprehensive registry of all documents.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import hashlib
from datetime import datetime
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.core.logging_config import get_logger

logger = get_logger(__name__)


class DocumentRegistry:
    """
    Build and maintain registry of all documents in the pipeline.

    The registry provides a single source of truth for document metadata,
    enabling cross-reference validation and dependency tracking.
    """

    def __init__(self, drafts_dir: Optional[Path] = None, output_file: Optional[Path] = None):
        """
        Initialize document registry builder.

        Args:
            drafts_dir: Path to drafts directory (default: ./drafts)
            output_file: Path to output registry JSON (default: ./document_registry.json)
        """
        if drafts_dir is None:
            drafts_dir = Path(__file__).parent.parent.parent / "drafts"
        if output_file is None:
            output_file = Path(__file__).parent.parent.parent / "document_registry.json"

        self.drafts_dir = Path(drafts_dir)
        self.output_file = Path(output_file)
        self.registry: Dict[str, Dict[str, Any]] = {}

    def scan_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan drafts directory and extract metadata from all Markdown files.

        Returns:
            Dictionary mapping document_id to document metadata

        Raises:
            FileNotFoundError: If drafts directory doesn't exist
        """
        if not self.drafts_dir.exists():
            raise FileNotFoundError(f"Drafts directory not found: {self.drafts_dir}")

        logger.info(f"Scanning documents in {self.drafts_dir}")
        document_count = 0

        # Find all Markdown files
        markdown_files = list(self.drafts_dir.glob("*.md"))
        logger.info(f"Found {len(markdown_files)} Markdown files")

        for md_file in markdown_files:
            try:
                metadata = self._extract_metadata(md_file)
                if metadata and 'document_id' in metadata:
                    doc_id = metadata['document_id']

                    # Calculate file hash for dependency tracking
                    file_hash = self._calculate_file_hash(md_file)

                    # Build registry entry
                    self.registry[doc_id] = {
                        'document_id': doc_id,
                        'file_path': str(md_file.relative_to(self.drafts_dir.parent)),
                        'file_name': md_file.name,
                        'file_hash': file_hash,
                        'title': metadata.get('title', ''),
                        'status': metadata.get('status', 'Draft'),
                        'revision': metadata.get('revision', '1.0'),
                        'owner': metadata.get('owner', ''),
                        'approver': metadata.get('approver', ''),
                        'effective_date': metadata.get('effective_date', ''),
                        'upstream_apn': metadata.get('upstream_apn', []),
                        'downstream_apn': metadata.get('downstream_apn', []),
                        'family': self._determine_family(doc_id),
                        'last_scanned': datetime.now().isoformat()
                    }
                    document_count += 1
                    logger.debug(f"Registered: {doc_id}")

            except Exception as e:
                logger.error(f"Error processing {md_file.name}: {e}")
                continue

        logger.info(f"Successfully registered {document_count} documents")
        return self.registry

    def _extract_metadata(self, md_file: Path) -> Optional[Dict[str, Any]]:
        """
        Extract YAML front matter from Markdown file.

        Args:
            md_file: Path to Markdown file

        Returns:
            Dictionary of metadata or None if not found
        """
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for YAML front matter
            if not content.startswith('---'):
                logger.warning(f"No YAML front matter found in {md_file.name}")
                return None

            # Extract front matter
            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning(f"Invalid YAML front matter in {md_file.name}")
                return None

            yaml_content = parts[1].strip()
            metadata = yaml.safe_load(yaml_content)

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata from {md_file.name}: {e}")
            return None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for dependency tracking.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _determine_family(self, document_id: str) -> str:
        """
        Determine document family from document ID.

        Args:
            document_id: Document ID (e.g., "SOP-001", "STD-042")

        Returns:
            Document family (SOP, STD, REF, APP)
        """
        if document_id.startswith('SOP-'):
            return 'SOP'
        elif document_id.startswith('STD-'):
            return 'STD'
        elif document_id.startswith('REF-'):
            return 'REF'
        elif document_id.startswith('APP-'):
            return 'APP'
        else:
            return 'UNKNOWN'

    def save_registry(self) -> None:
        """
        Save registry to JSON file.

        The registry file is written with human-readable formatting
        for easy inspection and version control.
        """
        logger.info(f"Saving registry to {self.output_file}")

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

        logger.info(f"Registry saved: {len(self.registry)} documents")

    def build_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build complete registry: scan documents and save to file.

        Returns:
            Complete document registry

        Example:
            >>> from scripts.core.registry import DocumentRegistry
            >>> registry = DocumentRegistry()
            >>> docs = registry.build_registry()
            >>> print(f"Registered {len(docs)} documents")
        """
        self.scan_documents()
        self.save_registry()
        return self.registry

    def validate_cross_references(self) -> List[str]:
        """
        Validate all upstream/downstream APN references.

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        for doc_id, doc_info in self.registry.items():
            # Check upstream APNs
            for upstream in doc_info.get('upstream_apn', []):
                if upstream not in self.registry:
                    errors.append(f"{doc_id}: upstream_apn '{upstream}' not found in registry")

            # Check downstream APNs
            for downstream in doc_info.get('downstream_apn', []):
                if downstream not in self.registry:
                    errors.append(f"{doc_id}: downstream_apn '{downstream}' not found in registry")

        if errors:
            logger.warning(f"Found {len(errors)} cross-reference validation errors")
        else:
            logger.info("All cross-references validated successfully")

        return errors


def main():
    """
    Command-line entry point for registry builder.

    Usage:
        python3 scripts/core/registry.py
    """
    from scripts.core.logging_config import setup_logging
    setup_logging(log_level="INFO")

    logger.info("=== Document Registry Builder ===")

    registry_builder = DocumentRegistry()
    registry = registry_builder.build_registry()

    print(f"\n✓ Registered {len(registry)} documents")
    print(f"✓ Registry saved to: {registry_builder.output_file}")

    # Validate cross-references
    errors = registry_builder.validate_cross_references()
    if errors:
        print(f"\n⚠ Found {len(errors)} cross-reference errors:")
        for error in errors[:10]:  # Show first 10
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    else:
        print("\n✓ All cross-references validated")

    # Summary by family
    families = {}
    for doc_info in registry.values():
        family = doc_info['family']
        families[family] = families.get(family, 0) + 1

    print("\nDocument summary by family:")
    for family, count in sorted(families.items()):
        print(f"  {family}: {count}")


if __name__ == "__main__":
    main()
