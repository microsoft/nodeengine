# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.utility import eval_template
import pytest

values = {
    "id": 123,
    "agent": {"name": "biggy", "config": {"voice": "gruff"}, "paths": [1, 2, 3]},
    "colors": ["red", "green", "blue"],
    "agents": [
        {"name": "biggy", "config": {"voice": "gruff"}},
        {"name": "smalls", "config": {"voice": "squeaky"}},
    ],
}

tests = [
    ("{{id}}", "123"),
    ("{{agent}}", values["agent"]),
    ("Hi {{agent.name}}", "Hi biggy"),
    ("{{agent.name}}", "biggy"),
    ("{{agent.config.voice}}", "gruff"),
    ("{{agent.paths[1]}}", "2"),
    ("{{colors[1]}}", "green"),
    ("{{agents[1].name}}", "smalls"),
    ("{{id}} is {{agent.name}}", "123 is biggy"),
    # Not found test cases
    ("{{nothing}}", "{{nothing}}"),
    ("Hi {{nothing}}", "Hi {{nothing}}"),
    ("{{agent.nothing}}", "{{agent.nothing}}"),
    ("{{agent.config.nothing}}", "{{agent.config.nothing}}"),
    ("{{agent.nothing.config}}", "{{agent.nothing.config}}"),
    ("{{colors[1000]}}", "{{colors[1000]}}"),
    ("{{agent.dogs[0].name}}", "{{agent.dogs[0].name}}"),
    ("{{agents[1000].config.voice}}", "{{agents[1000].config.voice}}"),
    ("Voice: {{agents[1000].config.voice}}", "Voice: {{agents[1000].config.voice}}"),
]


@pytest.mark.parametrize("input, expected", tests)
def test_eval_template(input, expected) -> None:
    actual = eval_template(input, values)
    assert expected == actual
