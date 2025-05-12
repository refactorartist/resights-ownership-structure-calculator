import typer
from .commands import (
    ownerships,
    validate
)

app = typer.Typer(help="Resights Ownership Structure Calculator CLI")


app.add_typer(validate.app, name="validate")
app.add_typer(ownerships.app, name="ownership")