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



class ProcessedModels(DataModel):
    model_config = ConfigDict(frozen=True)


class OwnershipNode(ProcessedModels): 
    id: str = Field(description="Unique identifier for the entity")
    name: str = Field(description="Name of the entity")


class ShareRange(ProcessedModels): 
    lower: float = Field(description="Lower bound of the ownership percentage")
    average: float = Field(description="Average ownership percentage")
    upper: float = Field(description="Upper bound of the ownership percentage")

    @classmethod
    def from_share_string(cls, share: str) -> "ShareRange":
        """Parse a share string and create a ShareRange instance.
        
        Examples:
            "100%" -> lower=100, average=100, upper=100
            "50-67%" -> lower=50, average=58.5, upper=67
            "<5%" -> lower=0, average=2.5, upper=5
        """
        if share == "100%":
            return cls(lower=100.0, average=100.0, upper=100.0)
        
        if share.startswith("<"):
            upper = float(share[1:-1])
            return cls(lower=0.0, average=upper/2, upper=upper)
        
        if "-" in share:
            lower, upper = map(float, share[:-1].split("-"))
            return cls(lower=lower, average=(lower + upper)/2, upper=upper)
        
        raise ValueError(f"Invalid share format: {share}")


class OwnershipRelation(ProcessedModels): 
    id: str = Field(description="Unique identifier for the ownership relation")
    source: OwnershipNode = Field(description="Source entity (owner)")
    target: OwnershipNode = Field(description="Target entity (owned)")
    share: ShareRange = Field(description="Range of ownership percentages")
    active: bool = Field(description="Whether the ownership relation is currently active")


class OwnershipGraph(ProcessedModels): 
    nodes: Set[OwnershipNode] = Field(description="Set of all entities in the ownership structure")
    relations: Set[OwnershipRelation] = Field(description="Set of all ownership relations between entities")

    @classmethod
    def from_relation_data(cls, relations_data: list[OwnershipRelationData]) -> "OwnershipGraph":
        """Create an OwnershipGraph from a list of OwnershipRelationData objects.
        
        Args:
            relations_data: List of ownership relation data objects
            
        Returns:
            OwnershipGraph containing all nodes and relations from the data
        """
        nodes: Set[OwnershipNode] = set()
        relations: Set[OwnershipRelation] = set()
        
        for data in relations_data:
            source_node = OwnershipNode(id=str(data.source), name=data.source_name)
            target_node = OwnershipNode(id=str(data.target), name=data.target_name)
            share_range = ShareRange.from_share_string(data.share)
            
            relation = OwnershipRelation(
                id=data.id,
                source=source_node,
                target=target_node,
                share=share_range,
                active=data.active
            )
            
            nodes.add(source_node)
            nodes.add(target_node)
            relations.add(relation)
        
        return cls(nodes=nodes, relations=relations)
