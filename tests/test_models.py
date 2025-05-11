import pytest
import json
import tempfile
from typing import List, Dict, Any
from pydantic import TypeAdapter

from resights_ownership_structure_calculator.models import (
    OwnershipRelationData,
    OwnershipNode,
    ShareRange,
    OwnershipRelation,
    OwnershipGraph,
    OwnershipRelationFile
)


@pytest.fixture
def sample_relation_data() -> Dict[str, Any]:
    return {
        "id": "36427426_29205272",
        "source": 36427426,
        "source_name": "CASA HOLDING A/S",
        "source_depth": 1,
        "target": 29205272,
        "target_name": "CASA A/S",
        "target_depth": 0,
        "share": "100%",
        "real_lower_share": 100.0,
        "real_average_share": 100.0,
        "real_upper_share": 100.0,
        "active": False
    }


@pytest.fixture
def sample_relations_data() -> List[Dict[str, Any]]:
    return [
        {
            "id": "36427426_29205272",
            "source": 36427426,
            "source_name": "CASA HOLDING A/S",
            "source_depth": 1,
            "target": 29205272,
            "target_name": "CASA A/S",
            "target_depth": 0,
            "share": "100%",
            "real_lower_share": 100.0,
            "real_average_share": 100.0,
            "real_upper_share": 100.0,
            "active": False
        },
        {
            "id": "37577723_29205272",
            "source": 37577723,
            "source_name": "CC OSCAR HOLDING I A/S",
            "source_depth": 1,
            "target": 29205272,
            "target_name": "CASA A/S",
            "target_depth": 0,
            "share": "100%",
            "real_lower_share": 100.0,
            "real_average_share": 100.0,
            "real_upper_share": 100.0,
            "active": True
        }
    ]


class TestOwnershipRelationData:
    def test_ownership_relation_data_creation(self, sample_relation_data: Dict[str, Any]) -> None:
        relation_data = OwnershipRelationData(**sample_relation_data)
        
        assert relation_data.id == sample_relation_data["id"]
        assert relation_data.source == sample_relation_data["source"]
        assert relation_data.source_name == sample_relation_data["source_name"]
        assert relation_data.source_depth == sample_relation_data["source_depth"]
        assert relation_data.target == sample_relation_data["target"]
        assert relation_data.target_name == sample_relation_data["target_name"]
        assert relation_data.target_depth == sample_relation_data["target_depth"]
        assert relation_data.share == sample_relation_data["share"]
        assert relation_data.real_lower_share == sample_relation_data["real_lower_share"]
        assert relation_data.real_average_share == sample_relation_data["real_average_share"]
        assert relation_data.real_upper_share == sample_relation_data["real_upper_share"]
        assert relation_data.active == sample_relation_data["active"]

    @pytest.mark.parametrize("field,value", [
        ("share", "50-67%"),
        ("real_lower_share", 50.0),
        ("real_average_share", 58.5),
        ("real_upper_share", 67.0),
        ("active", True)
    ])
    def test_ownership_relation_data_field_update(self, sample_relation_data: Dict[str, Any], field: str, value: Any) -> None:
        sample_relation_data[field] = value
        relation_data = OwnershipRelationData(**sample_relation_data)
        assert getattr(relation_data, field) == value
    
    def test_load_from_file(self, sample_relations_data: List[Dict[str, Any]]) -> None:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as temp_file:
            json.dump(sample_relations_data, temp_file)
            temp_file.flush()
            
            loaded_data = OwnershipRelationData.load_from_file(temp_file.name)
            
            assert len(loaded_data) == len(sample_relations_data)
            assert loaded_data[0].id == sample_relations_data[0]["id"]
            assert loaded_data[1].id == sample_relations_data[1]["id"]


class TestOwnershipNode:
    def test_ownership_node_creation(self) -> None:
        node = OwnershipNode(id="29205272", name="CASA A/S")
        assert node.id == "29205272"
        assert node.name == "CASA A/S"
    
    def test_ownership_node_immutability(self) -> None:
        node = OwnershipNode(id="29205272", name="CASA A/S")
        with pytest.raises(Exception):
            node.id = "new_id"


class TestShareRange:
    @pytest.mark.parametrize("lower,average,upper,share", [
        (100.0, 100.0, 100.0, "100%"),
        (50.0, 58.5, 67.0, "50-67%"),
        (10.0, 12.5, 15.0, "10-15%")
    ])
    def test_share_range_creation(self, lower: float, average: float, upper: float, share: str) -> None:
        share_range = ShareRange(lower=lower, average=average, upper=upper, share=share)
        assert share_range.lower == lower
        assert share_range.average == average
        assert share_range.upper == upper
        assert share_range.share == share


class TestOwnershipRelation:
    def test_ownership_relation_creation(self) -> None:
        source = OwnershipNode(id="36427426", name="CASA HOLDING A/S")
        target = OwnershipNode(id="29205272", name="CASA A/S")
        share_range = ShareRange(lower=100.0, average=100.0, upper=100.0, share="100%")
        
        relation = OwnershipRelation(
            id="36427426_29205272",
            source=source,
            target=target,
            share=share_range,
            active=False
        )
        
        assert relation.id == "36427426_29205272"
        assert relation.source == source
        assert relation.target == target
        assert relation.share == share_range
        assert relation.active is False


class TestOwnershipGraph:
    def test_ownership_graph_creation(self) -> None:
        node1 = OwnershipNode(id="36427426", name="CASA HOLDING A/S")
        node2 = OwnershipNode(id="29205272", name="CASA A/S")
        share_range = ShareRange(lower=100.0, average=100.0, upper=100.0, share="100%")
        
        relation = OwnershipRelation(
            id="36427426_29205272",
            source=node1,
            target=node2,
            share=share_range,
            active=False
        )
        
        graph = OwnershipGraph(nodes={node1, node2}, relations={relation})
        
        assert len(graph.nodes) == 2
        assert node1 in graph.nodes
        assert node2 in graph.nodes
        assert len(graph.relations) == 1
        assert relation in graph.relations
    
    def test_ownership_graph_immutability(self) -> None:
        graph = OwnershipGraph(nodes=set(), relations=set())
        with pytest.raises(Exception):
            graph.nodes = {OwnershipNode(id="test", name="test")}


class TestOwnershipRelationFile:
    def test_validate_json(self, sample_relations_data: List[Dict[str, Any]]) -> None:
        validated_data = TypeAdapter(list[OwnershipRelationData]).validate_python(sample_relations_data)
        assert len(validated_data) == len(sample_relations_data)
        assert all(isinstance(item, OwnershipRelationData) for item in validated_data)
