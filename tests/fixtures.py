import pytest
from typing import List
from resights_ownership_structure_calculator.models import (
    OwnershipRelationData,
    OwnershipGraph
)


@pytest.fixture
def sample_relation_data() -> List[OwnershipRelationData]:
    """Fixture providing sample ownership relation data."""
    return [
        OwnershipRelationData(
            id="1_2",
            source=1,
            source_name="Company A",
            source_depth=1,
            target=2,
            target_name="Company B",
            target_depth=0,
            share="100%",
            real_lower_share=None,
            real_average_share=None,
            real_upper_share=None,
            active=True
        ),
        OwnershipRelationData(
            id="3_2",
            source=3,
            source_name="Company C",
            source_depth=1,
            target=2,
            target_name="Company B",
            target_depth=0,
            share="50-67%",
            real_lower_share=None,
            real_average_share=None,
            real_upper_share=None,
            active=True
        ),
        OwnershipRelationData(
            id="4_3",
            source=4,
            source_name="Company D",
            source_depth=2,
            target=3,
            target_name="Company C",
            target_depth=1,
            share="<5%",
            real_lower_share=None,
            real_average_share=None,
            real_upper_share=None,
            active=True
        )
    ]


@pytest.fixture
def ownership_graph(sample_relation_data: List[OwnershipRelationData]) -> OwnershipGraph:
    """Fixture providing an OwnershipGraph instance."""
    return OwnershipGraph.from_relation_data(sample_relation_data)
