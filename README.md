# ZIP Analyzer

**ZIP Analyzer** is a tool for scanning your hard drive, identifying ZIP archives that have already been extracted elsewhere, and helping you free up space by deleting redundant ZIP files.

## Features

- **Indexes your drive** and builds a database of all files.
- **Identifies ZIP files** and analyzes their contents.
- **Detects extracted folders** that match ZIP contents.
- **Confidence scoring** for extraction detection.
- **(Optional) User interface** for reviewing and deleting redundant archives.

## Quick Start

1. **Install requirements**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Index your drive and analyze ZIP files**:
    ```bash
    python zip_analyzer.py
    ```

3. **(Optional) Use the GUI**:
    ```bash
    python zip_manager_gui.py
    ```

## Requirements

- Python 3.8+
- Dependencies: `PyQt5` (for GUI), standard Python libraries

## License

MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer

**Use with caution!** Deleting ZIP files is irreversible. Always double-check before confirming deletions.