from freak.utils import validate_flow


def test_valid_dag() -> None:
    step_graph = {
        None: [1],
        1: [2, 3],
        2: [3, 4],
    }
    is_valid_flow = validate_flow(step_graph=step_graph)
    assert is_valid_flow == True


def test_cyclic_dag() -> None:
    step_graph = {
        None: [1],
        1: [2, 3],
        2: [3, 4],
        4: [1, 5],
    }
    is_valid_flow = validate_flow(step_graph=step_graph)
    assert is_valid_flow == False
