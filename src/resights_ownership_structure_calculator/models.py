from __future__ import annotations
from pydantic import BaseModel, ConfigDict, model_validator, Field

from typing import Optional, List



class Entity(BaseModel):
    """Represents an entity in the ownership structure.
    
    Args:
        id: Unique identifier for the entity
        name: Name of the entity
    """
    id: str = Field(description="Unique identifier for the entity")
    name: str = Field(description="Name of the entity")

    model_config = ConfigDict(frozen=True)
    


class OwnershipRelation(BaseModel):
    """Represents an ownership relationship between two entities.
    
    Args:
        id: Unique identifier for the relationship
        source: ID of the source entity (owner)
        source_name: Name of the source entity
        source_depth: Depth level of the source entity in the ownership tree
        target: ID of the target entity (owned)
        target_name: Name of the target entity
        target_depth: Depth level of the target entity in the ownership tree
        share: String representation of ownership percentage (e.g., "100%", "5-10%", "<5%")
        real_lower_share: Lower bound of the ownership percentage
        real_average_share: Average of the ownership percentage range
        real_upper_share: Upper bound of the ownership percentage
        active: Whether the ownership relationship is currently active
    """
    id: str = Field(description="Unique identifier for the relationship")
    source: int = Field(description="ID of the source entity (owner)")
    source_name: str = Field(description="Name of the source entity")
    source_depth: int = Field(description="Depth level of the source entity in the ownership tree")
    target: int = Field(description="ID of the target entity (owned)")
    target_name: str = Field(description="Name of the target entity")
    target_depth: int = Field(description="Depth level of the target entity in the ownership tree")
    share: str = Field(description="String representation of ownership percentage (e.g., '100%', '5-10%', '<5%')")
    real_lower_share: Optional[float] = Field(None, description="Lower bound of the ownership percentage")
    real_average_share: Optional[float] = Field(None, description="Average of the ownership percentage range")
    real_upper_share: Optional[float] = Field(None, description="Upper bound of the ownership percentage")
    active: bool = Field(description="Whether the ownership relationship is currently active")

    @model_validator(mode='after')
    def calculate_real_shares(self) -> 'OwnershipRelation':
        """Calculate real_lower_share, real_average_share, and real_upper_share based on the share string.
        
        The share string can be in formats like "100%", "5-10%", "<5%", etc.
        
        Returns:
            The updated OwnershipRelation instance
        """
        # Handle exact percentage
        if self.share == "100%":
            self.real_lower_share = 100.0
            self.real_average_share = 100.0
            self.real_upper_share = 100.0
            return self

        # Handle less than percentage
        if self.share.startswith("<"):
            percentage = float(self.share[1:-1])
            self.real_lower_share = 0.0
            self.real_average_share = percentage / 2
            self.real_upper_share = percentage
            return self

        # Handle range percentage (e.g., "5-10%")
        if "-" in self.share:
            lower, upper = map(float, self.share[:-1].split("-"))
            self.real_lower_share = lower
            self.real_average_share = (lower + upper) / 2
            self.real_upper_share = upper
            return self

        # If we can't parse the share string, set all values to None
        self.real_lower_share = None
        self.real_average_share = None
        self.real_upper_share = None
        return self
    
    def entities(self) -> List[Entity]:
        """Return a list of entities in the ownership structure."""
        return [Entity(id=str(self.source), name=self.source_name), Entity(id=str(self.target), name=self.target_name)]


class OwnershipStructure(BaseModel):
    """Represents the complete ownership structure with multiple ownership relationships.
    
    Args:
        relations: List of ownership relationships
    """
    relations: List[OwnershipRelation] = Field(description="List of ownership relationships")

    @classmethod
    def from_json(cls, data: List[dict]) -> "OwnershipStructure":
        """Create an OwnershipStructure from a list of relation dictionaries.
        
        Args:
            data: List of ownership relation dictionaries
            
        Returns:
            OwnershipStructure instance
        """
        relations = [OwnershipRelation(**relation) for relation in data]
        return cls(relations=relations)
    
    def calculate_all_real_shares(self) -> None:
        """Calculate real shares for all relations in the ownership structure."""
        for relation in self.relations:
            relation.calculate_real_shares()

    def entities(self) -> List[Entity]:
        """Return a list of entities in the ownership structure."""
        return list(set([entity for relation in self.relations for entity in relation.entities()]))

