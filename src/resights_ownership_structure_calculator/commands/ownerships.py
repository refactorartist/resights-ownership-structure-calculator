from pathlib import Path
import typer

from resights_ownership_structure_calculator.models import (
    OwnershipGraph,
    OwnershipRelationData,
)
from resights_ownership_structure_calculator.utils.validate import (
    FileValidationError,
    validate_file,
)

app = typer.Typer(
    name="ownership",
    help="Commands for calculating ownership structure",
    add_completion=False,
)


@app.command()
def calculate(
    path: str = typer.Argument(
        ..., help="The file to calculate the ownership structure from"
    ),
    company: str = typer.Argument(
        ..., help="The company to calculate the ownership structure for"
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="The target company to calculate the ownership relations for; if no target is provided the focus company will be used",
    ),
) -> None:
    try:
        file_path = Path(path)
        validate_file(file_path)

        data = OwnershipRelationData.load_from_file(file_path)
        graph = OwnershipGraph.from_relation_data(data)

        target_company = (
            graph.get_owner_by_name(target) if target else graph.get_focus_company()
        )

        source_company = graph.get_owner_by_name(company)

        ownership_path = graph.get_ownership_path(source_company, target_company)

        typer.echo(
            f"Ownership path from {source_company.name} to {target_company.name}:"
        )

        has_inactive_relations = False
        for relationship in ownership_path:
            if not relationship.active:
                has_inactive_relations = True
                typer.secho(
                    " Warning: The ownership path contains inactive relations.",
                    fg=typer.colors.RED,
                )

            typer.echo(
                f" {relationship.source.name} -> {relationship.target.name} ({relationship.share} )"
            )

        if not has_inactive_relations:
            real_ownership = graph.get_real_ownership(source_company, target_company)
            typer.echo(f"Total ownership: {real_ownership}")
        else:
            typer.secho(
                "Unable to calculate real ownership due to inactive relations.",
                fg=typer.colors.RED,
            )

    except FileValidationError as e:
        typer.echo(f"File Validation Error: {e}")
        raise typer.Abort()
    

@app.command() 
def list_all(
    path: str = typer.Argument(
        ..., help="The file to calculate the ownership structure from"
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="The target company to get all owners for; if no target is provided the focus company will be used",
    ),
) -> None:
    try:
        file_path = Path(path)
        validate_file(file_path)

        data = OwnershipRelationData.load_from_file(file_path)
        graph = OwnershipGraph.from_relation_data(data)

        target_company = (
            graph.get_owner_by_name(target) if target else graph.get_focus_company()
        )

        owners = graph.get_all_owners(target_company)

        typer.echo(f"Owners of {target_company.name}:")

        for owner in owners:
            typer.echo(f" - {owner.name}")

        typer.echo(f"Total owners: {len(owners)}")

        
    except FileValidationError as e:
        typer.echo(f"File Validation Error: {e}")
        raise typer.Abort()


@app.command() 
def list_owned(
    path: str = typer.Argument(
        ..., help="The file to calculate the ownership structure from"
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="The target company to get all owners for; if no target is provided the focus company will be used",
    ),
) -> None:
    try:
        file_path = Path(path)
        validate_file(file_path)

        data = OwnershipRelationData.load_from_file(file_path)
        graph = OwnershipGraph.from_relation_data(data)

        target_company = (
            graph.get_owner_by_name(target) if target else graph.get_focus_company()
        )   

        owned = graph.get_direct_owned(target_company)

        typer.echo(f"Owned by {target_company.name}:")

        for relation in owned:
            typer.echo(f" - {relation.target.name}")

        typer.echo(f"Total owned: {len(owned)}")

        
    except FileValidationError as e:
        typer.echo(f"File Validation Error: {e}")
        raise typer.Abort()



@app.command() 
def list_owners(
    path: str = typer.Argument(
        ..., help="The file to calculate the ownership structure from"
    ),
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="The target company to get all owners for; if no target is provided the focus company will be used",
    ),
) -> None:
    try:
        file_path = Path(path)
        validate_file(file_path)

        data = OwnershipRelationData.load_from_file(file_path)
        graph = OwnershipGraph.from_relation_data(data)

        target_company = (
            graph.get_owner_by_name(target) if target else graph.get_focus_company()
        )   

        owners = graph.get_direct_owners(target_company)

        typer.echo(f"Owners of {target_company.name}:")

        for relation in owners:
            typer.echo(f" - {relation.source.name}")

        typer.echo(f"Total owners: {len(owners)}")

        
    except FileValidationError as e:
        typer.echo(f"File Validation Error: {e}")
        raise typer.Abort()
