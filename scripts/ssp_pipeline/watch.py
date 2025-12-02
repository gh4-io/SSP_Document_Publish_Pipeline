"""File watcher for live document authoring.

Monitors Markdown files for changes and auto-rebuilds HTML/PDF.
Provides WYSIWYG-ish behavior for document authors.
Part of SSP Document Publishing Pipeline v4.
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from . import pipeline

logger = logging.getLogger(__name__)


class MarkdownChangeHandler(FileSystemEventHandler):
    """
    Handle file system events for Markdown files.

    Triggers pipeline rebuild when monitored files are modified.
    """

    def __init__(self, markdown_path: Path, profile_path: Path, debounce_seconds: float = 2.0):
        """
        Initialize change handler.

        Args:
            markdown_path: Path to Markdown file being monitored
            profile_path: Path to layout profile JSON
            debounce_seconds: Minimum time between rebuilds (prevents rapid re-triggers)
        """
        super().__init__()
        self.markdown_path = markdown_path.resolve()
        self.profile_path = profile_path
        self.debounce_seconds = debounce_seconds
        self.last_rebuild_time = 0.0

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Handle file modification event.

        Args:
            event: File system event from watchdog
        """
        # Ignore directory events
        if event.is_directory:
            return

        # Only process events for our target file
        event_path = Path(event.src_path).resolve()
        if event_path != self.markdown_path:
            return

        # Debounce: ignore if rebuild happened too recently
        current_time = time.time()
        elapsed = current_time - self.last_rebuild_time
        if elapsed < self.debounce_seconds:
            logger.debug(f"Debouncing rebuild (elapsed: {elapsed:.1f}s)")
            return

        logger.info("=" * 60)
        logger.info(f"File changed: {self.markdown_path.name}")
        logger.info("Triggering rebuild...")
        logger.info("=" * 60)

        try:
            output_path = pipeline.run_pipeline(
                self.markdown_path,
                self.profile_path,
                skip_validation=False
            )
            logger.info(f"✅ Rebuild successful: {output_path}")
            self.last_rebuild_time = current_time

        except Exception as e:
            logger.error(f"❌ Rebuild failed: {e}", exc_info=True)
            # Don't update last_rebuild_time on failure, allow retry


def watch_markdown(
    markdown_path: Path,
    profile_path: Path,
    debounce_seconds: float = 2.0,
    initial_build: bool = True
) -> None:
    """
    Watch a Markdown file for changes and auto-rebuild.

    Runs indefinitely until interrupted (Ctrl+C).

    Args:
        markdown_path: Path to Markdown file to monitor
        profile_path: Path to layout profile JSON
        debounce_seconds: Minimum time between rebuilds
        initial_build: Run initial build before starting watch

    Raises:
        FileNotFoundError: If markdown_path does not exist
        KeyboardInterrupt: When user presses Ctrl+C (expected)
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    markdown_path = markdown_path.resolve()
    watch_dir = markdown_path.parent

    logger.info("=" * 60)
    logger.info("SSP Watch Mode Starting")
    logger.info("=" * 60)
    logger.info(f"Monitoring: {markdown_path}")
    logger.info(f"Profile: {profile_path}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Initial build
    if initial_build:
        logger.info("Running initial build...")
        try:
            output_path = pipeline.run_pipeline(markdown_path, profile_path)
            logger.info(f"✅ Initial build complete: {output_path}")
        except Exception as e:
            logger.error(f"❌ Initial build failed: {e}", exc_info=True)
            logger.warning("Continuing watch mode anyway...")

    # Set up file watcher
    event_handler = MarkdownChangeHandler(markdown_path, profile_path, debounce_seconds)
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=False)
    observer.start()

    try:
        logger.info("\n👀 Watching for changes... (Ctrl+C to stop)")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopping watch mode...")
        observer.stop()

    observer.join()
    logger.info("Watch mode stopped.")


def main() -> None:
    """
    CLI entry point for watch mode.

    Example usage:
        python -m scripts.ssp_pipeline.watch drafts/SOP-200.md \\
            templates/profiles/layout_profile_dts_master_report.json
    """
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m scripts.ssp_pipeline.watch <markdown_file> <profile_json>")
        print("\nExample:")
        print("  python -m scripts.ssp_pipeline.watch drafts/SOP-200.md templates/profiles/layout_profile_dts_master_report.json")
        sys.exit(1)

    markdown_path = Path(sys.argv[1])
    profile_path = Path(sys.argv[2])

    # Set up basic logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    try:
        watch_markdown(markdown_path, profile_path)
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        # Normal exit
        pass


if __name__ == "__main__":
    main()
