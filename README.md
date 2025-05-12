# ZIP Analyzer

**ZIP Analyzer** is a tool for scanning your hard drive, identifying ZIP archives that have already been extracted elsewhere, and helping you free up space by deleting redundant ZIP files.

## Features

- **Indexes your drive** and builds a database of all files.
- **Identifies ZIP files** and analyzes their contents.
- **Detects extracted folders** that match ZIP contents.
- **Confidence scoring** for extraction detection.
- **(Optional) User interface** for reviewing and deleting redundant archives.

## Quick Start

- **Install the package** (from source):
```powershell
pip install .
```

- **Run the CLI**:
```powershell
zip-analyzer --help
zip-analyzer <drive_or_folder>
```

- **Run the GUI**:
```powershell
zip-manager-gui
```

## Requirements

- Python 3.8+
- Dependencies are managed via `pyproject.toml` and installed automatically.

## Development

- **Install dev dependencies**:
```powershell
pip install .[dev]
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer

**Use with caution!** Deleting ZIP files is irreversible. Always double-check before confirming deletions.