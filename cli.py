import typer
from pathlib import Path
from converter import FB2Converter

app = typer.Typer()


@app.command()
def convert(
    input_dir: Path = typer.Option(
        Path("input"),
        "--input",
        "-i",
        help="Directory containing .fb2 files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        "--output",
        "-o",
        help="Directory to save .epub files",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
):
    """
    Convert all FB2 books in the INPUT directory to EPUB format in the OUTPUT directory.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        typer.echo(f"Created output directory: {output_dir}")

    fb2_files = list(input_dir.glob("*.fb2"))
    if not fb2_files:
        typer.echo(f"No .fb2 files found in {input_dir}")
        raise typer.Exit()

    typer.echo(f"Found {len(fb2_files)} files to convert.")

    success_count = 0
    for fb2_file in fb2_files:
        output_file = output_dir / (fb2_file.stem + ".epub")
        converter = FB2Converter(fb2_file, output_file)
        if converter.convert():
            success_count += 1
            typer.echo(f"Converted: {fb2_file.name}")
        else:
            typer.echo(f"Failed: {fb2_file.name}", err=True)

    typer.echo(
        f"Conversion complete. {success_count}/{len(fb2_files)} files converted."
    )


if __name__ == "__main__":
    app()
