import pytest
import json
import networkx as nx
from typing import List, Tuple, Any
from pathlib import Path

from resights_ownership_structure_calculator.models import (
    OwnershipRelationData,
    ShareRange,
    OwnershipGraph
)


class TestShareRange:
    @pytest.mark.parametrize("share_string, expected", [
        ("100%", (100.0, 100.0, 100.0)),
        ("50-67%", (50.0, 58.5, 67.0)),
        ("<5%", (0.0, 2.5, 5.0)),
    ])
    def test_from_share_string(self, share_string: str, expected: Tuple[float, float, float]) -> None:
        """Test parsing different share string formats."""
        share_range = ShareRange.from_share_string(share_string)
        assert share_range.lower == expected[0]
        assert share_range.average == expected[1]
        assert share_range.upper == expected[2]

    def test_invalid_share_string(self) -> None:
        """Test that invalid share strings raise ValueError."""
        with pytest.raises(ValueError):
            ShareRange.from_share_string("invalid")


class TestOwnershipGraph:
    def test_from_relation_data(self, sample_relation_data: List[OwnershipRelationData]) -> None:
        """Test creating an OwnershipGraph from relation data."""
        graph = OwnershipGraph.from_relation_data(sample_relation_data)
        
        # Check that all nodes were created
        assert len(graph.nodes) == 4
        assert "1" in graph.nodes
        assert "2" in graph.nodes
        assert "3" in graph.nodes
        assert "4" in graph.nodes
        
        # Check that all relations were created
        assert len(graph.relations) == 3
        assert "1_2" in graph.relations
        assert "3_2" in graph.relations
        assert "4_3" in graph.relations

    def test_get_graph(self, ownership_graph: OwnershipGraph) -> None:
        """Test that get_graph returns a valid NetworkX DiGraph."""
        graph = ownership_graph.get_graph()
        assert isinstance(graph, nx.DiGraph)
        assert len(graph.nodes) == 4
        assert len(graph.edges) == 3
        
        # Check edge attributes
        edge_1_2 = graph.get_edge_data("1", "2")
        assert edge_1_2["id"] == "1_2"
        assert edge_1_2["lower"] == 100.0
        assert edge_1_2["active"] is True

    def test_get_focus_company(self, ownership_graph: OwnershipGraph) -> None:
        """Test getting the focus company (depth=0)."""
        focus = ownership_graph.get_focus_company()
        assert focus.name == "Company B"
        assert focus.id == "2"

    def test_get_direct_owners(self, ownership_graph: OwnershipGraph) -> None:
        """Test getting direct owners of a node."""
        focus = ownership_graph.get_focus_company()
        direct_owners = ownership_graph.get_direct_owners(focus)
        
        assert len(direct_owners) == 2
        owner_names = {relation.source.name for relation in direct_owners}
        assert "Company A" in owner_names
        assert "Company C" in owner_names

    def test_get_direct_owned(self, ownership_graph: OwnershipGraph) -> None:
        """Test getting entities directly owned by a node."""
        company_c = ownership_graph.get_owner_by_name("Company C")
        direct_owned = ownership_graph.get_direct_owned(company_c)
        
        assert len(direct_owned) == 1
        assert next(iter(direct_owned)).target.name == "Company B"

    def test_get_all_owners(self, ownership_graph: OwnershipGraph) -> None:
        """Test getting all owners of a node, including indirect owners."""
        focus = ownership_graph.get_focus_company()
        all_owners = ownership_graph.get_all_owners(focus)
        
        assert len(all_owners) == 3
        owner_names = {owner.name for owner in all_owners}
        assert "Company A" in owner_names
        assert "Company C" in owner_names
        assert "Company D" in owner_names

    def test_get_ownership_path(self, ownership_graph: OwnershipGraph) -> None:
        """Test getting the ownership path between two nodes."""
        company_d = ownership_graph.get_owner_by_name("Company D")
        company_b = ownership_graph.get_owner_by_name("Company B")
        
        path = ownership_graph.get_ownership_path(company_d, company_b)
        
        assert len(path) == 2
        assert path[0].source.name == "Company D"
        assert path[0].target.name == "Company C"
        assert path[1].source.name == "Company C"
        assert path[1].target.name == "Company B"

    def test_get_owner_by_name(self, ownership_graph: OwnershipGraph) -> None:
        """Test finding a node by name."""
        node = ownership_graph.get_owner_by_name("Company A")
        assert node.id == "1"
        
        with pytest.raises(ValueError):
            ownership_graph.get_owner_by_name("Nonexistent Company")

    def test_get_real_ownership(self, ownership_graph: OwnershipGraph, monkeypatch: Any) -> None:
        """Test calculating real ownership percentages along a path."""
        # Mock print to avoid output during tests
        monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)
        
        company_d = ownership_graph.get_owner_by_name("Company D")
        company_b = ownership_graph.get_owner_by_name("Company B")
        
        share_range = ownership_graph.get_real_ownership(company_d, company_b)
        
        # D owns <5% of C, which owns 50-67% of B
        # So D's real ownership in B should be:
        # Lower: 0 * 50 / 100 = 0
        # Average: 2.5 * 58.5 / 100 = 1.4625
        # Upper: 5 * 67 / 100 = 3.35
        assert share_range.lower == 0.0
        assert pytest.approx(share_range.average, 0.001) == 1.4625
        assert pytest.approx(share_range.upper, 0.001) == 3.35


class TestOwnershipRelationData:
    def test_load_from_file(self, tmp_path: Path) -> None:
        """Test loading relation data from a JSON file."""
        # Create a temporary JSON file
        data = [
            {
                "id": "1_2",
                "source": 1,
                "source_name": "Company A",
                "source_depth": 1,
                "target": 2,
                "target_name": "Company B",
                "target_depth": 0,
                "share": "100%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            }
        ]
        
        file_path = tmp_path / "test_data.json"
        with open(file_path, "w") as f:
            json.dump(data, f)
        
        # Load the data
        relations = OwnershipRelationData.load_from_file(str(file_path))
        
        assert len(relations) == 1
        assert relations[0].id == "1_2"
        assert relations[0].source_name == "Company A"
        assert relations[0].target_name == "Company B"
