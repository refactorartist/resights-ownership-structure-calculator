from typing import Optional
from pydantic import BaseModel


class OwnershipRelationData(BaseModel):
    """
    Represents an ownership relationship between two entities.
    Based on the structure found in the JSON data files.
    """
    id: str
    source: int
    source_name: str
    source_depth: int
    target: int
    target_name: str
    target_depth: int
    share: str
    real_lower_share: Optional[float] = None
    real_average_share: Optional[float] = None
    real_upper_share: Optional[float] = None
    active: bool


