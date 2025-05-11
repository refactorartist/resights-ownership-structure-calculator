import pytest
from resights_ownership_structure_calculator.models import Entity, OwnershipRelation, OwnershipStructure


@pytest.fixture
def sample_relation_data():
    return {
        "id": "12345_67890",
        "source": 12345,
        "source_name": "Source Company",
        "source_depth": 1,
        "target": 67890,
        "target_name": "Target Company",
        "target_depth": 0,
        "share": "100%",
        "real_lower_share": None,
        "real_average_share": None,
        "real_upper_share": None,
        "active": True
    }


@pytest.fixture
def sample_relations_data():
    return [
        {
            "id": "12345_67890",
            "source": 12345,
            "source_name": "Source Company",
            "source_depth": 1,
            "target": 67890,
            "target_name": "Target Company",
            "target_depth": 0,
            "share": "100%",
            "real_lower_share": None,
            "real_average_share": None,
            "real_upper_share": None,
            "active": True
        },
        {
            "id": "54321_67890",
            "source": 54321,
            "source_name": "Another Source",
            "source_depth": 1,
            "target": 67890,
            "target_name": "Target Company",
            "target_depth": 0,
            "share": "5-10%",
            "real_lower_share": None,
            "real_average_share": None,
            "real_upper_share": None,
            "active": True
        }
    ]


class TestEntity:
    def test_entity_creation(self):
        entity = Entity(id="12345", name="Test Entity")
        assert entity.id == "12345"
        assert entity.name == "Test Entity"

    def test_entity_equality(self):
        entity1 = Entity(id="12345", name="Test Entity")
        entity2 = Entity(id="12345", name="Test Entity")
        entity3 = Entity(id="67890", name="Different Entity")
        
        assert entity1 == entity2
        assert entity1 != entity3
        assert hash(entity1) == hash(entity2)
        assert hash(entity1) != hash(entity3)


class TestOwnershipRelation:
    def test_ownership_relation_creation(self, sample_relation_data):
        relation = OwnershipRelation(**sample_relation_data)
        assert relation.id == "12345_67890"
        assert relation.source == 12345
        assert relation.target == 67890
        assert relation.share == "100%"
        assert relation.active is True

    @pytest.mark.parametrize("share,expected_lower,expected_avg,expected_upper", [
        ("100%", 100.0, 100.0, 100.0),
        ("<5%", 0.0, 2.5, 5.0),
        ("5-10%", 5.0, 7.5, 10.0),
        ("33-50%", 33.0, 41.5, 50.0),
        ("invalid%", None, None, None)
    ])
    def test_calculate_real_shares(self, sample_relation_data, share, expected_lower, expected_avg, expected_upper):
        sample_relation_data["share"] = share
        relation = OwnershipRelation(**sample_relation_data)
        
        assert relation.real_lower_share == expected_lower
        assert relation.real_average_share == expected_avg
        assert relation.real_upper_share == expected_upper
    
    def test_entities_method(self, sample_relation_data):
        relation = OwnershipRelation(**sample_relation_data)
        entities = relation.entities()
        
        assert len(entities) == 2
        assert entities[0].id == str(sample_relation_data["source"])
        assert entities[0].name == sample_relation_data["source_name"]
        assert entities[1].id == str(sample_relation_data["target"])
        assert entities[1].name == sample_relation_data["target_name"]


class TestOwnershipStructure:
    def test_ownership_structure_creation(self, sample_relations_data):
        structure = OwnershipStructure(relations=[OwnershipRelation(**data) for data in sample_relations_data])
        assert len(structure.relations) == 2
        assert structure.relations[0].id == "12345_67890"
        assert structure.relations[1].id == "54321_67890"

    def test_from_json(self, sample_relations_data):
        structure = OwnershipStructure.from_json(sample_relations_data)
        assert len(structure.relations) == 2
        assert structure.relations[0].id == "12345_67890"
        assert structure.relations[1].id == "54321_67890"

    @pytest.mark.parametrize("shares,expected_values", [
        (
            ["100%", "5-10%"],
            [
                (100.0, 100.0, 100.0),  # First relation: lower, average, upper
                (5.0, 7.5, 10.0)        # Second relation: lower, average, upper
            ]
        ),
        (
            ["<5%", "33-50%"],
            [
                (0.0, 2.5, 5.0),        # First relation: lower, average, upper
                (33.0, 41.5, 50.0)      # Second relation: lower, average, upper
            ]
        )
    ])
    def test_calculate_all_real_shares(self, sample_relations_data, shares, expected_values):
        # Set the shares for the relations
        for i, share in enumerate(shares):
            sample_relations_data[i]["share"] = share
        
        structure = OwnershipStructure.from_json(sample_relations_data)
        structure.calculate_all_real_shares()
        
        # Verify each relation's calculated shares
        for i, (exp_lower, exp_avg, exp_upper) in enumerate(expected_values):
            assert structure.relations[i].real_lower_share == exp_lower
            assert structure.relations[i].real_average_share == exp_avg
            assert structure.relations[i].real_upper_share == exp_upper
    
    def test_entities_method(self, sample_relations_data):
        structure = OwnershipStructure.from_json(sample_relations_data)
        entities = structure.entities()
        
        # Should have 3 unique entities (2 sources and 1 target)
        assert len(entities) == 3
        
        # Check that all expected entity IDs are present
        entity_ids = {entity.id for entity in entities}
        assert "12345" in entity_ids
        assert "54321" in entity_ids
        assert "67890" in entity_ids
        
        # Check entity names
        entity_names = {entity.name for entity in entities}
        assert "Source Company" in entity_names
        assert "Another Source" in entity_names
        assert "Target Company" in entity_names
