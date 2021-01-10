# freak

<div align="center">

[![Build status](https://github.com/transhaphigsn/freak/workflows/build/badge.svg?branch=master&event=push)](https://github.com/transhaphigsn/freak/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/freak.svg)](https://pypi.org/project/freak/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/transhaphigsn/freak/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/transhaphigsn/freak/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/transhaphigsn/freak/releases)
[![License](https://img.shields.io/github/license/transhaphigsn/freak)](https://github.com/transhaphigsn/freak/blob/master/LICENSE)

**Freak** is a data flow engine.
</div>

## About

**Freak** is primarily composed of two components, Engine and Flow, which are further divided into smaller components. Engine is encapsulation of logic on how to read flows and execute them in order of specified definition. Engine does this using components:

- **Butler**
- **Executor**
- **Inspector**

Before explaining about these components, it is a good idea to understand what exactly is a flow in a Freak and how it is implemented. A flow is nothing but a set of steps intended to achieve an objective. This objective can be anything that is identifiable as business logic. The implementation of flow is done by defining three components:

- **Flow decorator**, it is used to identify steps of the flow and enforce policies on how it is used or executed.

- **Locator**, it uses flow decorator to locate steps defined in a module (module here is used as reference to single python file). Every flow is required to define one of its own, so that `Butler` can use it to identify and execute the flow.

Since, we have a basic understanding of what exactly a flow in freak is, let's move on to engine components.

- **Butler** is responsible for reading python modules, locating steps and organizing them using locator specified by flow.

- **Executor** is core component of the engine. It is responsible for executing steps. Currently, it only supports linear flows.

- **Inspector** is used to return input schema for every step defined by the flow. This is intended to be part of view logic of the engine.

**Freak** is currently under active development. Following code should give you an idea how it implements data flows.

This is how you define a flow using base flow.

```python
from freak.flows.base_flow import base_flow
from freak.models.input import InputModel, InputModelB
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext
from freak.types import Flow


@base_flow(
    name="func_one",
    order=1,
    input_model=InputModel,
    uid="func_one",
    parent_uid=None,
)
def func_one(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}
    )


@base_flow(
    name="func_two",
    order=2,
    input_model=InputModel,
    uid="func_two",
    parent_uid="func_one",
)
def func_two(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 2, "b": b + 3},
    )


@base_flow(
    name="func_three",
    order=3,
    input_model=InputModel,
    uid="func_three",
    parent_uid="func_two",
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@base_flow(
    name="func_four",
    order=4,
    input_model=InputModelB,
    uid="func_four",
    parent_uid="func_three",
)
def func_four(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    c = ctx.input["c"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 4, "b": b + 5, "c": c + 6},
    )
```

Following test case will use above defintion to execute the flow.

```python
from freak.engine import Engine

def test_base_flow_prosecutioner():
    executioner = Engine(module_name=__name__, decorator_name="base_flow")

    response = executioner.execute(data={"a": 4, "b": 7}, from_step="func_one")

    output, path_traversed = response

    assert path_traversed == {
        "last_step": "func_three",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_three"],
            "func_three": ["func_four"],
        },
    }

    responses = output.responses

    assert output.from_step == 1
    assert output.to_step == 4

    assert output.last_successful_step == 3

    assert responses[0].output == {"a": 5, "b": 9}
    assert responses[1].output == {"a": 6, "b": 10}
    assert responses[2].output == {"a": 7, "b": 11}

    assert responses[3].success == False
    assert responses[3].output == {}
    assert (
        responses[3].messages[0]
        == "Variable: c | Type: value_error.missing | Message: field required"
    )

    response = executioner.execute(
        data={"a": 4, "b": 7, "c": 5},
        from_step="func_four",
        executed_steps=path_traversed,
    )

    output, path_traversed = response

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 8, "b": 12, "c": 11}

    assert output.last_successful_step == 4
    assert output.from_step == 4
    assert output.to_step == 4

    assert path_traversed == {
        "last_step": "func_four",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_three"],
            "func_three": ["func_four"],
            "func_four": [],
        },
    }
```

Using above code, it is also possible to generate input schema for every step. Following test case will demonstrate this behaviour.

```python
from freak.engine import Engine

def test_base_flow_fetch_schema():
    executioner = Engine(module_name=__name__, decorator_name="base_flow")
    responses = executioner.inspect()

    input_model_b_schema = {
        "title": "InputModelB",
        "description": "Class for defining structure of request data.",
        "type": "object",
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "integer"},
            "c": {"title": "C", "type": "integer"},
        },
        "required": ["a", "b", "c"],
    }
    input_model_schema = {
        "title": "InputModel",
        "description": "Class for defining structure of request data.",
        "type": "object",
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "integer"},
        },
        "required": ["a", "b"],
    }

    assert input_model_schema == InputModel.schema()
    assert input_model_b_schema == InputModelB.schema()

    assert responses[0]["schema"] == input_model_schema
    assert responses[1]["schema"] == input_model_schema
    assert responses[2]["schema"] == input_model_schema
    assert responses[3]["schema"] == input_model_b_schema
```

<!-- ## Very first steps

### Building your package

Building a new version of the application contains steps:

- Bump the version of your package `poetry version <version>`. You can pass the new version explicitly, or a rule such as `major`, `minor`, or `patch`. For more details, refer to the [Semantic Versions](https://semver.org/) standard.
- Make a commit to `GitHub`.
- Create a `GitHub release`.
- And... publish 🙂 `poetry publish --build` -->

<!-- ## What's next

Articles:

- [Open Source Guides](https://opensource.guide/)
- [GitHub Actions Documentation](https://help.github.com/en/actions)
- Maybe you would like to add [gitmoji](https://gitmoji.carloscuesta.me/) to commit names. This is really funny. 😄 -->

<!-- ## Installation

```bash
pip install freak
```

or install with `Poetry`

```bash
poetry add freak
```

Then you can run

```bash
freak --help
```

```bash
freak --name Roman
```

or if installed with `Poetry`:

```bash
poetry run freak --help
```

```bash
poetry run freak --name Roman
``` -->

<!-- ## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/transhaphigsn/freak/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

We use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.

For Pull Request this labels are configured, by default:

|               **Label**               |  **Title in Releases**  |
|:-------------------------------------:|:----------------------:|
| `enhancement`, `feature`              | 🚀 Features             |
| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |
| `build`, `ci`, `testing`              | 📦 Build System & CI/CD |
| `breaking`                            | 💥 Breaking Changes     |
| `documentation`                       | 📝 Documentation        |
| `dependencies`                        | ⬆️ Dependencies updates |

You can update it in [`release-drafter.yml`](https://github.com/transhaphigsn/freak/blob/master/.github/release-drafter.yml).

GitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them. -->

## 🛡 License

[![License](https://img.shields.io/github/license/transhaphigsn/freak)](https://github.com/transhaphigsn/freak/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/transhaphigsn/freak/blob/master/LICENSE) for more details.

## 📃 Citation

```
@misc{freak,
  author = {transhapHigsn},
  title = {Freak is a data flow engine.},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/transhaphigsn/freak}}
}
```

## Credits

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).
