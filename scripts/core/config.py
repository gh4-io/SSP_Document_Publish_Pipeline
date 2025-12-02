"""
Configuration Management Module

Provides hierarchical configuration loading with profile support and dot-notation access.
Configuration priority (later overrides earlier):
  1. default.yaml (base system configuration)
  2. profiles/{profile}.yaml (document family-specific overrides)
  3. local.yaml (local machine overrides, gitignored)

Usage:
    from scripts.core.config import Config

    # Load configuration for SOP documents
    config = Config(profile='sop')

    # Access with dot notation
    pandoc_exe = config.get('pipeline.pandoc.executable')
    max_workers = config.get('pipeline.batch.max_workers', default=4)

    # Set values
    config.set('pipeline.batch.max_workers', 8)

Author: SSP Pipeline Team
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Hierarchical configuration manager with profile support"""

    def __init__(self, profile: Optional[str] = None, config_dir: str = 'config'):
        """
        Initialize configuration loader

        Args:
            profile: Document family profile (sop, std, ref, app) or None for defaults only
            config_dir: Directory containing configuration files (default: 'config')
        """
        self.profile = profile
        self.config_dir = Path(config_dir)
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load and merge configuration files in priority order

        Returns:
            Merged configuration dictionary
        """
        config = {}

        # Define load order (later files override earlier)
        files = ['default.yaml']

        # Add profile if specified
        if self.profile:
            files.append(f'profiles/{self.profile}.yaml')

        # Add local overrides (gitignored)
        files.append('local.yaml')

        # Load and merge each file
        for filename in files:
            path = self.config_dir / filename
            if path.exists():
                with open(path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:  # Handle empty files
                        config = self._deep_merge(config, data)

        return config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge dictionaries (override wins on conflicts)

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary (base + override)
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value (or add new key)
                result[key] = value

        return result

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path

        Args:
            path: Dot-separated key path (e.g., 'pipeline.pandoc.executable')
            default: Default value if path not found

        Returns:
            Configuration value at path, or default if not found

        Examples:
            >>> config = Config('sop')
            >>> config.get('pipeline.pandoc.executable')
            '/usr/bin/pandoc'
            >>> config.get('pipeline.batch.max_workers', default=4)
            4
        """
        keys = path.split('.')
        value = self.data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path: str, value: Any) -> None:
        """
        Set configuration value by dot-notation path

        Args:
            path: Dot-separated key path (e.g., 'pipeline.batch.max_workers')
            value: Value to set

        Examples:
            >>> config = Config('sop')
            >>> config.set('pipeline.batch.max_workers', 8)
        """
        keys = path.split('.')
        data = self.data

        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        # Set final key
        data[keys[-1]] = value

    def has(self, path: str) -> bool:
        """
        Check if configuration path exists

        Args:
            path: Dot-separated key path

        Returns:
            True if path exists, False otherwise

        Examples:
            >>> config = Config('sop')
            >>> config.has('pipeline.pandoc.executable')
            True
            >>> config.has('nonexistent.path')
            False
        """
        keys = path.split('.')
        value = self.data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return False

        return True

    def get_section(self, path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get entire configuration section

        Args:
            path: Dot-separated path to section
            default: Default value if section not found

        Returns:
            Configuration section dictionary

        Examples:
            >>> config = Config('sop')
            >>> config.get_section('pipeline.pandoc')
            {'executable': '/usr/bin/pandoc', 'filters': [...], ...}
        """
        value = self.get(path, default=default)

        if isinstance(value, dict):
            return value
        elif default is not None:
            return default
        else:
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Export full configuration as dictionary

        Returns:
            Complete configuration dictionary
        """
        return self.data.copy()

    def reload(self) -> None:
        """Reload configuration from files (useful if files changed)"""
        self.data = self._load_config()

    def __repr__(self) -> str:
        """String representation of Config object"""
        return f"Config(profile={self.profile!r}, keys={len(self.data)})"


# Convenience function for quick config loading
def load_config(profile: Optional[str] = None, config_dir: str = 'config') -> Config:
    """
    Load configuration with optional profile

    Args:
        profile: Document family profile (sop, std, ref, app)
        config_dir: Configuration directory

    Returns:
        Config instance

    Examples:
        >>> config = load_config('sop')
        >>> pandoc_exe = config.get('pipeline.pandoc.executable')
    """
    return Config(profile=profile, config_dir=config_dir)


if __name__ == '__main__':
    # Self-test
    import sys

    try:
        # Test default config
        print("Testing default configuration...")
        config = Config()
        pandoc_exe = config.get('pipeline.pandoc.executable')
        print(f"  Pandoc executable: {pandoc_exe}")

        # Test SOP profile
        print("\nTesting SOP profile...")
        sop_config = Config('sop')
        schema = sop_config.get('pipeline.validation.schema')
        print(f"  SOP schema: {schema}")

        # Test dot-notation access
        print("\nTesting dot-notation access...")
        max_workers = sop_config.get('pipeline.batch.max_workers', default=4)
        print(f"  Max workers: {max_workers}")

        # Test section retrieval
        print("\nTesting section retrieval...")
        pandoc_section = sop_config.get_section('pipeline.pandoc')
        print(f"  Pandoc section keys: {list(pandoc_section.keys())}")

        print("\n✓ All configuration tests passed!")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
