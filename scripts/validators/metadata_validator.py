"""
Metadata Validation Module

Validates YAML front matter metadata in Markdown documents against JSON schemas.
Supports:
  - Schema-based validation (jsonschema)
  - Cross-reference validation (upstream/downstream APNs)
  - Status transition validation (Draft→Review→Active→Retired)
  - Structured error reporting

Usage:
    from scripts.validators.metadata_validator import validate_metadata, ValidationReport

    # Validate single document
    is_valid, errors = validate_metadata('drafts/SOP-200.md', 'schemas/sop_metadata.json')

    if not is_valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")

    # Validate with detailed report
    report = validate_document('drafts/SOP-200.md')
    print(report.format_report())

Author: SSP Pipeline Team
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import jsonschema
from jsonschema import validate, ValidationError, SchemaError


class ValidationReport:
    """Structured validation error and warning report"""

    def __init__(self):
        """Initialize empty validation report"""
        self.errors: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []

    def add_error(self, field: str, message: str) -> None:
        """
        Add validation error

        Args:
            field: Field name that failed validation
            message: Error message
        """
        self.errors.append({
            'field': field,
            'message': message,
            'severity': 'error'
        })

    def add_warning(self, field: str, message: str) -> None:
        """
        Add validation warning

        Args:
            field: Field name with warning
            message: Warning message
        """
        self.warnings.append({
            'field': field,
            'message': message,
            'severity': 'warning'
        })

    def is_valid(self) -> bool:
        """
        Check if validation passed (no errors)

        Returns:
            True if no errors, False if any errors exist
        """
        return len(self.errors) == 0

    def format_report(self) -> str:
        """
        Format validation report as human-readable text

        Returns:
            Formatted report string
        """
        output = []

        if self.errors:
            output.append("ERRORS:")
            for e in self.errors:
                output.append(f"  - {e['field']}: {e['message']}")

        if self.warnings:
            if output:
                output.append("")
            output.append("WARNINGS:")
            for w in self.warnings:
                output.append(f"  - {w['field']}: {w['message']}")

        if not self.errors and not self.warnings:
            output.append("Validation passed: No errors or warnings")

        return "\n".join(output)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export report as dictionary

        Returns:
            Dictionary with errors and warnings lists
        """
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'is_valid': self.is_valid()
        }


def parse_yaml_metadata(markdown_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract YAML front matter from Markdown file

    Args:
        markdown_path: Path to Markdown file

    Returns:
        Parsed YAML metadata dictionary, or None if no front matter found

    Raises:
        FileNotFoundError: If markdown_path does not exist
        yaml.YAMLError: If YAML parsing fails
    """
    path = Path(markdown_path)

    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for YAML front matter delimiters (---)
    if not content.startswith('---'):
        return None

    # Find end of YAML block
    yaml_end = content.find('---', 3)
    if yaml_end == -1:
        raise yaml.YAMLError("YAML front matter missing closing delimiter (---)")

    # Extract and parse YAML
    yaml_text = content[3:yaml_end].strip()
    metadata = yaml.safe_load(yaml_text)

    return metadata if metadata else {}


def validate_metadata(markdown_path: str, schema_path: str) -> Tuple[bool, List[str]]:
    """
    Validate YAML front matter against JSON schema

    Args:
        markdown_path: Path to Markdown file
        schema_path: Path to JSON schema file

    Returns:
        Tuple of (is_valid, errors) where errors is list of error messages

    Examples:
        >>> is_valid, errors = validate_metadata('drafts/SOP-200.md', 'schemas/sop_metadata.json')
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    errors = []

    try:
        # Parse YAML metadata
        metadata = parse_yaml_metadata(markdown_path)

        if metadata is None:
            return False, ["No YAML front matter found"]

        # Load JSON schema
        schema_path_obj = Path(schema_path)
        if not schema_path_obj.exists():
            return False, [f"Schema file not found: {schema_path}"]

        with open(schema_path_obj, 'r') as f:
            schema = json.load(f)

        # Validate against schema
        try:
            validate(instance=metadata, schema=schema)
            return True, []

        except ValidationError as e:
            # Extract meaningful error message
            error_msg = f"{e.json_path}: {e.message}" if hasattr(e, 'json_path') else str(e.message)
            return False, [error_msg]

        except SchemaError as e:
            return False, [f"Schema error: {e.message}"]

    except FileNotFoundError as e:
        return False, [str(e)]

    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {e}"]

    except Exception as e:
        return False, [f"Unexpected error: {e}"]


def validate_cross_references(metadata: Dict[str, Any], document_registry: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate upstream_apn and downstream_apn cross-references

    Args:
        metadata: Parsed YAML metadata dictionary
        document_registry: Dictionary of all known document IDs

    Returns:
        Tuple of (is_valid, errors)

    Examples:
        >>> registry = {'SOP-001': {}, 'SOP-002': {}, 'REF-2201': {}}
        >>> metadata = {'upstream_apn': ['SOP-001'], 'downstream_apn': ['REF-9999']}
        >>> is_valid, errors = validate_cross_references(metadata, registry)
        >>> print(errors)
        ['Downstream APN not found: REF-9999']
    """
    errors = []

    # Validate upstream_apn references
    for apn in metadata.get('upstream_apn', []):
        if apn not in document_registry:
            errors.append(f"Upstream APN not found: {apn}")

    # Validate downstream_apn references
    for apn in metadata.get('downstream_apn', []):
        if apn not in document_registry:
            errors.append(f"Downstream APN not found: {apn}")

    return len(errors) == 0, errors


def validate_status_transition(old_metadata: Dict[str, Any], new_metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate status transitions and revision increments

    Transition Rules:
      - Draft → Review: Revision stays same
      - Review → Active: Increment revision
      - Active → Active (update): Increment revision
      - Active → Retired: Revision stays same

    Args:
        old_metadata: Previous document metadata
        new_metadata: New document metadata

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> old = {'status': 'Draft', 'revision': 0}
        >>> new = {'status': 'Review', 'revision': 1}
        >>> is_valid, error = validate_status_transition(old, new)
        >>> print(error)
        'Draft → Review: revision must stay same (expected 0, got 1)'
    """
    old_status = old_metadata.get('status')
    new_status = new_metadata.get('status')
    old_rev = old_metadata.get('revision', 0)
    new_rev = new_metadata.get('revision', 0)

    # Draft → Review: revision unchanged
    if old_status == 'Draft' and new_status == 'Review':
        if new_rev != old_rev:
            return False, f"Draft → Review: revision must stay same (expected {old_rev}, got {new_rev})"

    # Review → Active: increment revision
    elif old_status == 'Review' and new_status == 'Active':
        if new_rev != old_rev + 1:
            return False, f"Review → Active: must increment revision (expected {old_rev + 1}, got {new_rev})"

    # Active → Active: increment revision
    elif old_status == 'Active' and new_status == 'Active':
        if new_rev <= old_rev:
            return False, f"Active update: must increment revision (expected > {old_rev}, got {new_rev})"

    # Active → Retired: revision unchanged
    elif old_status == 'Active' and new_status == 'Retired':
        if new_rev != old_rev:
            return False, f"Active → Retired: revision must stay same (expected {old_rev}, got {new_rev})"

    return True, None


def validate_document(markdown_path: str, schema_path: Optional[str] = None,
                      document_registry: Optional[Dict[str, Any]] = None,
                      old_metadata: Optional[Dict[str, Any]] = None) -> ValidationReport:
    """
    Comprehensive document validation with detailed reporting

    Args:
        markdown_path: Path to Markdown document
        schema_path: Path to JSON schema (auto-detected if None)
        document_registry: Registry of all documents (for cross-ref validation)
        old_metadata: Previous metadata (for status transition validation)

    Returns:
        ValidationReport object

    Examples:
        >>> report = validate_document('drafts/SOP-200.md')
        >>> if not report.is_valid():
        ...     print(report.format_report())
    """
    report = ValidationReport()

    try:
        # Parse metadata
        metadata = parse_yaml_metadata(markdown_path)

        if metadata is None:
            report.add_error('metadata', 'No YAML front matter found')
            return report

        # Auto-detect schema if not provided
        if schema_path is None:
            category = metadata.get('category', '').lower()
            if category in ['sop', 'std', 'ref', 'app']:
                schema_path = f'schemas/{category}_metadata.json'
            else:
                report.add_error('category', f"Unknown category '{category}', cannot auto-detect schema")
                return report

        # Schema validation
        is_valid, errors = validate_metadata(markdown_path, schema_path)
        for error in errors:
            report.add_error('schema', error)

        # Cross-reference validation
        if document_registry:
            is_valid_xref, xref_errors = validate_cross_references(metadata, document_registry)
            for error in xref_errors:
                report.add_error('cross_reference', error)

        # Status transition validation
        if old_metadata:
            is_valid_status, status_error = validate_status_transition(old_metadata, metadata)
            if not is_valid_status:
                report.add_error('status_transition', status_error)

        # Add warnings for missing optional fields
        if not metadata.get('tags'):
            report.add_warning('tags', 'No tags specified (recommended for categorization)')

        if metadata.get('effective_date') is None:
            report.add_warning('effective_date', 'No effective date set')

    except Exception as e:
        report.add_error('validation', f"Unexpected error: {e}")

    return report


if __name__ == '__main__':
    # Self-test with sample document
    import sys

    try:
        print("Testing metadata validator...")

        # Find a sample document
        drafts_dir = Path('drafts')
        if not drafts_dir.exists():
            print("  Warning: drafts/ directory not found, skipping test")
            sys.exit(0)

        sample_docs = list(drafts_dir.glob('SOP-*.md'))
        if not sample_docs:
            print("  Warning: No SOP documents found in drafts/, skipping test")
            sys.exit(0)

        sample_doc = sample_docs[0]
        print(f"  Testing with: {sample_doc.name}")

        # Test validation
        report = validate_document(str(sample_doc))

        print(f"\n  Validation Report:")
        print("  " + report.format_report().replace("\n", "\n  "))

        if report.is_valid():
            print("\n✓ Metadata validation tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Validation found errors (this may be expected for test documents)")
            sys.exit(0)  # Exit 0 for self-test (errors might be expected)

    except Exception as e:
        print(f"\n✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
