import typer
from pathlib import Path
from resights_ownership_structure_calculator.utils.validate import validate_file, FileValidationError

app = typer.Typer(
    name="validate",
    help="Commands for validating data files",
    add_completion=False,
)

@app.command()
def file(
    path: str = typer.Argument(help="The file to validate"),
) -> None:
    """Validate a file"""
    typer.echo(f"Validating file: {path}")
    try:    
        validate_file(Path(path))
        typer.echo(f"File {path} is valid")
    except FileValidationError as e:
        typer.echo(f"File {path} is invalid: {e}")
        raise typer.Abort()
