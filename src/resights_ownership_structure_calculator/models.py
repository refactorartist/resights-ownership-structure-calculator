from __future__ import annotations
import json
from typing import Optional, Set
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class DataModel(BaseModel):
    ... 



class OwnershipRelationData(DataModel):
    id: str = Field(description="Unique identifier for the ownership relation")
    source: int = Field(description="ID of the source entity (owner)")
    source_name: str = Field(description="Name of the source entity")
    source_depth: int = Field(description="Depth level of the source entity in the ownership structure")
    target: int = Field(description="ID of the target entity (owned)")
    target_name: str = Field(description="Name of the target entity")
    target_depth: int = Field(description="Depth level of the target entity in the ownership structure")
    share: str = Field(description="Ownership share as a string (e.g. '100%', '10-15%')")
    real_lower_share: Optional[float] = Field(default=None, description="Lower bound of the ownership percentage")
    real_average_share: Optional[float] = Field(default=None, description="Average ownership percentage")
    real_upper_share: Optional[float] = Field(default=None, description="Upper bound of the ownership percentage")
    active: bool = Field(description="Whether the ownership relation is currently active")

    @classmethod 
    def load_from_file(cls, file_path: str) -> list["OwnershipRelationData"]:
        with open(file_path, "r") as f:
            data = json.load(f)
        return TypeAdapter(list[OwnershipRelationData]).validate_python(data)


OwnershipRelationFile = TypeAdapter(list[OwnershipRelationData])


class ProcessedModels(DataModel):
    model_config = ConfigDict(frozen=True)


class OwnershipNode(ProcessedModels): 
    id: str = Field(description="Unique identifier for the entity")
    name: str = Field(description="Name of the entity")


class ShareRange(ProcessedModels): 
    lower: float = Field(description="Lower bound of the ownership percentage")
    average: float = Field(description="Average ownership percentage")
    upper: float = Field(description="Upper bound of the ownership percentage")
    share: str = Field(description="Original share string representation")


class OwnershipRelation(ProcessedModels): 
    id: str = Field(description="Unique identifier for the ownership relation")
    source: OwnershipNode = Field(description="Source entity (owner)")
    target: OwnershipNode = Field(description="Target entity (owned)")
    share: ShareRange = Field(description="Range of ownership percentages")
    active: bool = Field(description="Whether the ownership relation is currently active")


class OwnershipGraph(ProcessedModels): 
    nodes: Set[OwnershipNode] = Field(description="Set of all entities in the ownership structure")
    relations: Set[OwnershipRelation] = Field(description="Set of all ownership relations between entities")
