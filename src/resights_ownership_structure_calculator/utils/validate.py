from pathlib import Path
from resights_ownership_structure_calculator.models import OwnershipRelationData


class FileValidationError(Exception): ...


class FileNotFoundError(FileValidationError): ...


class FileIsNotAFileError(FileValidationError): ...


class FileIsNotAJSONFileError(FileValidationError): ...


class FileIsNotValidError(FileValidationError): ...


def validate_file(path: Path) -> None:
    """Validate a file"""
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")

    if not file_path.is_file():
        raise FileIsNotAFileError(f"File {file_path} is not a file")

    if file_path.suffix != ".json":
        raise FileIsNotAJSONFileError(f"File {file_path} is not a JSON file")

    try:
        OwnershipRelationData.load_from_file(file_path)
    except Exception as e:
        raise FileIsNotValidError(f"File {file_path} is invalid: {e}")
