# FB2 to EPUB Converter

A simple and efficient CLI tool to convert FB2 books to EPUB format.

## Features

- Batch conversion of multiple files.
- Preserves metadata (title, author, language).
- Handles images.
- Generates Table of Contents (TOC).

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd fb2toepub
    ```

2.  Install dependencies using `uv` (recommended) or `pip`:
    ```bash
    uv sync
    # OR
    pip install -r requirements.txt
    ```

## Usage

1.  Place your `.fb2` files in the `input` directory (create it if it doesn't exist).
2.  Run the converter:
    ```bash
    python cli.py
    ```
3.  Find your converted `.epub` files in the `output` directory.

### Custom Directories

You can specify custom input and output directories:

```bash
python cli.py --input /path/to/fb2/files --output /path/to/save/epub
```

## Development

- `converter.py`: Contains the `FB2Converter` class logic.
- `cli.py`: Contains the CLI implementation using `typer`.

## Testing

To run the tests, use `pytest`:

```bash
uv run pytest
```

## Requirements

To generate `requirements.txt` files:

```bash
# For production dependencies
uv export --no-dev --output-file requirements.txt

# For development dependencies
uv export --output-file requirements-dev.txt
```
