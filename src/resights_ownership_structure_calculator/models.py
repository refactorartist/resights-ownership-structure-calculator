from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Set
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
import networkx as nx

class DataModel(BaseModel):
    ... 



class OwnershipRelationData(DataModel):
    """Represents ownership relation data between entities.
    
    This class stores information about ownership relationships between entities,
    including identifiers, names, ownership shares, and relationship status.
    
    Attributes:
        id: Unique identifier for the ownership relation
        source: ID of the source entity (owner)
        source_name: Name of the source entity
        source_depth: Depth level of the source entity in the ownership structure
        target: ID of the target entity (owned)
        target_name: Name of the target entity
        target_depth: Depth level of the target entity in the ownership structure
        share: Ownership share as a string (e.g. '100%', '10-15%')
        real_lower_share: Lower bound of the ownership percentage
        real_average_share: Average ownership percentage
        real_upper_share: Upper bound of the ownership percentage
        active: Whether the ownership relation is currently active
    """
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
    def load_from_file(cls, file_path: Path) -> list["OwnershipRelationData"]:
        """Loads ownership relation data from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing ownership relation data
            
        Returns:
            A list of OwnershipRelationData objects
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        return TypeAdapter(list[OwnershipRelationData]).validate_python(data)



class ProcessedModels(DataModel):
    """Base class for processed data models with frozen configuration."""
    model_config = ConfigDict(frozen=True)


class GraphModels(DataModel):
    """Base class for graph-based data models.
    
    Attributes:
        graph: NetworkX graph representation of the ownership structure
    """
    graph: Optional[nx.DiGraph] = Field(default=None, description="NetworkX graph representation of the ownership structure")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_graph(self) -> nx.DiGraph:
        """Returns the graph representation.
        
        Returns:
            A NetworkX directed graph
            
        Raises:
            NotImplementedError: If not implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement this method")


class OwnershipNode(ProcessedModels): 
    """Represents an entity in the ownership structure.
    
    Attributes:
        id: Unique identifier for the entity
        name: Name of the entity
    """
    id: str = Field(description="Unique identifier for the entity")
    name: str = Field(description="Name of the entity")


class ShareRange(ProcessedModels): 
    """Represents a range of ownership percentages.
    
    Attributes:
        lower: Lower bound of the ownership percentage
        average: Average ownership percentage
        upper: Upper bound of the ownership percentage
    """
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
            
        Args:
            share: A string representing an ownership share
            
        Returns:
            A ShareRange instance with parsed values
            
        Raises:
            ValueError: If the share string format is invalid
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
    """Represents an ownership relationship between two entities.
    
    Attributes:
        id: Unique identifier for the ownership relation
        source: Source entity (owner)
        target: Target entity (owned)
        share: Range of ownership percentages
        active: Whether the ownership relation is currently active
        source_depth: Depth level of the source entity in the ownership structure
        target_depth: Depth level of the target entity in the ownership structure
    """
    id: str = Field(description="Unique identifier for the ownership relation")
    source: OwnershipNode = Field(description="Source entity (owner)")
    target: OwnershipNode = Field(description="Target entity (owned)")
    share: ShareRange = Field(description="Range of ownership percentages")
    active: bool = Field(description="Whether the ownership relation is currently active")
    source_depth: int = Field(description="Depth level of the source entity in the ownership structure")
    target_depth: int = Field(description="Depth level of the target entity in the ownership structure")



class OwnershipGraph(GraphModels): 
    """Represents the complete ownership structure as a graph.
    
    Attributes:
        nodes: HashMap of all entities in the ownership structure
        relations: HashMap of all ownership relations between entities
        graph: NetworkX graph representation of the ownership structure
    """
    nodes: dict[str, OwnershipNode] = Field(description="HashMap of all entities in the ownership structure")
    relations: dict[str, OwnershipRelation] = Field(description="HashMap of all ownership relations between entities")

    graph: Optional[nx.DiGraph] = Field(default=None, description="NetworkX graph representation of the ownership structure")


    def get_graph(self) -> nx.DiGraph:
        """Creates or returns the NetworkX graph representation.
        
        Returns:
            A NetworkX directed graph representing the ownership structure
            
        Raises:
            ValueError: If nodes and relations are not set
        """
        if self.nodes is None or self.relations is None: 
            raise ValueError("Nodes and relations must be set before getting the graph")

        if self.graph is not None: 
            return self.graph

        self.graph = nx.DiGraph()

        for node in self.nodes.values(): 
            self.graph.add_node(node.id, name=node.name)

        for relation in self.relations.values(): 
            self.graph.add_edge(
                relation.source.id,
                relation.target.id,
                id=relation.id,
                lower=relation.share.lower,
                average=relation.share.average,
                upper=relation.share.upper,
                source_depth=relation.source_depth,
                target_depth=relation.target_depth,
                active=relation.active,
            )

        return self.graph

    @classmethod
    def from_relation_data(cls, relations_data: list[OwnershipRelationData]) -> "OwnershipGraph":
        """Create an OwnershipGraph from a list of OwnershipRelationData objects.
        
        Args:
            relations_data: List of ownership relation data objects
            
        Returns:
            OwnershipGraph containing all nodes and relations from the data
        """
        nodes: dict[str, OwnershipNode] = {}
        relations: dict[str, OwnershipRelation] = {}
        
        for data in relations_data:
            source_node = OwnershipNode(id=str(data.source), name=data.source_name)
            target_node = OwnershipNode(id=str(data.target), name=data.target_name)
            share_range = ShareRange.from_share_string(data.share)
            
            relation = OwnershipRelation(
                id=data.id,
                source=source_node,
                target=target_node,
                share=share_range,
                active=data.active,
                source_depth=data.source_depth,
                target_depth=data.target_depth
            )
            
            nodes[source_node.id] = source_node
            nodes[target_node.id] = target_node
            relations[relation.id] = relation
        
        return cls(nodes=nodes, relations=relations)
    
    def get_focus_company(self) -> OwnershipNode:
        """Gets the focus company (company with depth = 0).
        
        Returns:
            The focus company node
            
        Raises:
            ValueError: If no focus company is found
        """
        for relation in self.relations.values():
            if relation.target_depth == 0:
                return relation.target   

        raise ValueError("No focus company found (no node with depth = 0)")

    def get_focus_company_via_graph(self) -> OwnershipNode:
        """Gets the focus company (company with depth = 0) using graph attributes.
        
        Returns:
            The focus company node
            
        Raises:
            ValueError: If no focus company is found
        """
        graph: nx.DiGraph = self.get_graph()
        
        # Find nodes with target_depth = 0 using graph attributes
        for node_id, node_attrs in graph.nodes(data=True):
            # Check edges where this node is a target
            for source_id, target_id, edge_attrs in graph.in_edges(node_id, data=True):
                if edge_attrs.get('target_depth') == 0:
                    # Find the corresponding node from our nodes set
                    if node_id in self.nodes: 
                        return self.nodes[node_id]
        
        raise ValueError("No focus company found (no node with depth = 0)")

    def get_direct_owners(self, target: OwnershipNode) -> Set[OwnershipRelation]:
        """Gets all direct ownership relations where the given node is the target.
        
        Args:
            target: The target node to find owners for
            
        Returns:
            A set of ownership relations where the given node is directly owned
        """
        graph = self.get_graph()
        relations = set()

        # Get all incoming edges to the target node
        for source_id in graph.predecessors(target.id):
            edge_data = graph.get_edge_data(source_id, target.id)

            relation = self.relations.get(edge_data['id'])

            if not relation: 
                continue 

            relations.add(relation)

        
        return relations

    def get_direct_owned(self, source: OwnershipNode) -> Set[OwnershipRelation]:
        """Gets all direct ownership relations where the given node is the source.
        
        Args:
            source: The source node to find owned entities for
            
        Returns:
            A set of ownership relations where the given node is the direct owner
        """
        graph = self.get_graph()
        relations = set()
        
        # Get all outgoing edges from the source node
        for target_id in graph.successors(source.id):
            edge_data = graph.get_edge_data(source.id, target_id)

            relation = self.relations.get(edge_data['id'])

            if not relation: 
                continue 

            relations.add(relation)
        return relations
    

    def get_all_owners(self, target: OwnershipNode) -> Set[OwnershipNode]:
        """Gets all owners of a given node, including indirect owners.
        
        Args:
            target: The target node to find all owners for
            
        Returns:
            A set of all owner nodes that can reach the target node
        """
        graph = self.get_graph()
        owners = set()
        
        # Get all nodes that can reach the target node
        for source_id in nx.ancestors(graph, target.id):

            owner = self.nodes.get(source_id) 
            if not owner: 
                continue 

            owners.add(owner) 
        
        return owners

    def get_real_ownership(self, source_node: OwnershipNode, target_node: OwnershipNode) -> ShareRange:
        """Calculates the real ownership percentage of a node in the target company.
        
        This method finds a path from the given source node to the target node and
        calculates the effective ownership percentage along that path.
        
        Args:
            source_node: The source node (owner)
            target_node: The target node (owned)
            
        Returns:
            A ShareRange representing the effective ownership percentage
        """
        path = self.get_ownership_path(source_node, target_node)
        lower = 100.0
        average = 100.0
        upper = 100.0

        for ownership_relation in path: 
            lower *= ownership_relation.share.lower / 100.0
            average *= ownership_relation.share.average / 100.0
            upper *= ownership_relation.share.upper / 100.0

        return ShareRange(lower=lower, average=average, upper=upper)

    

    def get_ownership_path(self, source_node: OwnershipNode, target_node: OwnershipNode) -> list[OwnershipRelation]:
        """Finds the ownership path between two nodes.
        
        This method finds the shortest path from the source node to the target node
        in the ownership graph.
        
        Args:
            source_node: The source node (owner)
            target_node: The target node (owned)
            
        Returns:
            A list of ownership relations representing the path
            
        Raises:
            ValueError: If no ownership path exists between the nodes
        """
        graph = self.get_graph()
        
        reversed_path = False
        
        # Check if there's a path from source to target
        if not nx.has_path(graph, source_node.id, target_node.id):
            # Try the reverse direction if original path not found
            if nx.has_path(graph, target_node.id, source_node.id):
                # Swap source and target nodes
                source_node, target_node = target_node, source_node
                reversed_path = True
            else:
                raise ValueError(f"No ownership path between {source_node.name} and {target_node.name}")
        
        # Get the shortest path from node to focus company
        path = nx.shortest_path(graph, source_node.id, target_node.id)

        ownership_path: list[OwnershipRelation] = []
        
        # Calculate ownership along the path
        for i in range(len(path) - 1):
            source_id = path[i]
            target_id = path[i + 1]
            edge_data = graph.get_edge_data(source_id, target_id)

            if not edge_data: 
                continue 

            relation = self.relations.get(edge_data['id'])

            if not relation: 
                continue

            ownership_path.append(relation) 
            
        if reversed_path:
            return self.reverse_ownership_path(ownership_path)
        
        return ownership_path
    
    @staticmethod
    def reverse_ownership_path(ownership_path: list[OwnershipRelation]) -> list[OwnershipRelation]:
        reversed_ownership_path = []
        ownership_path.reverse()
        for relation in ownership_path:
            reversed_ownership_path.append(relation.model_copy(update={"source": relation.target, "target": relation.source}))
        return reversed_ownership_path
    

    def get_owner_by_name(self, name: str) -> OwnershipNode:
        """Gets an ownership node by its name.
        
        Args:
            name: The name of the node to find
            
        Returns:
            The ownership node with the given name
            
        Raises:
            ValueError: If no node with the given name is found
        """
        for node in self.nodes.values():
            if node.name == name:
                return node
        raise ValueError(f"No node found with name: {name}")
