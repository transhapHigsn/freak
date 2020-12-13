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

Freak is a data flow engine.
</div>

## About

Freak is currently under active development. Following test case should give you an idea how it implements data flows.

```python
from freak.engine import butler, prosecutioner
from freak.flows.base_flow import base_flow, locator, organizer
from freak.models.input import InputModel, InputModelB
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext


@base_flow(
    name="func_one", order=1, input_model=InputModel
)
def func_one(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}
    )


@base_flow(
    name="func_two", order=2, input_model=InputModel
)
def func_two(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 2, "b": b + 3},
    )


@base_flow(
    name="func_three", order=3, input_model=InputModel
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@base_flow(
    name="func_four", order=4, input_model=InputModelB
)
def func_four(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    c = ctx.input["c"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 4, "b": b + 5, "c": c + 6},
    )


def test_base_flow_prosecutioner():
    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        data={"a": 4, "b": 7},
    )

    responses = output.responses
    total_steps = output.to_step - output.from_step + 1

    assert output.from_step == 1
    assert output.to_step == 4

    assert total_steps == 4
    assert len(responses) == total_steps

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

    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        data={"a": 4, "b": 7, "c": 5},
        step=4,
    )

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 8, "b": 12, "c": 11}

    assert output.last_successful_step == 4
    assert output.from_step == 4
    assert output.to_step == 4

```

Using above code, it is also possible to generate input schema for every step. Following test case will demonstrate this behaviour.

```python

from freak.engine import inspector

def test_base_flow_fetch_schema():
    responses = inspector(
        module_name=__name__,
        decorator_name="base_flow",
    )

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

### Makefile usage

[`Makefile`](https://github.com/transhaphigsn/freak/blob/master/Makefile) contains many functions for fast assembling and convenient work.

<details>
<summary>1. Download Poetry</summary>
<p>

```bash
make download-poetry
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

```bash
make install
```

If you do not want to install pre-commit hooks, run the command with the NO_PRE_COMMIT flag:

```bash
make install NO_PRE_COMMIT=1
```

</p>
</details>

<details>
<summary>3. Check the security of your code</summary>
<p>

```bash
make check-safety
```

This command launches a `Poetry` and `Pip` integrity check as well as identifies security issues with `Safety` and `Bandit`. By default, the build will not crash if any of the items fail. But you can set `STRICT=1` for the entire build, or you can configure strictness for each item separately.

```bash
make check-safety STRICT=1
```

or only for `safety`:

```bash
make check-safety SAFETY_STRICT=1
```

multiple

```bash
make check-safety PIP_STRICT=1 SAFETY_STRICT=1
```

> List of flags for `check-safety` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`.

</p>
</details>

<details>
<summary>4. Check the codestyle</summary>
<p>

The command is similar to `check-safety` but to check the code style, obviously. It uses `Black`, `Darglint`, `Isort`, and `Mypy` inside.

```bash
make check-style
```

It may also contain the `STRICT` flag.

```bash
make check-style STRICT=1
```

> List of flags for `check-style` (can be set to `1` or `0`): `STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<details>
<summary>5. Run all the codestyle formaters</summary>
<p>

Codestyle uses `pre-commit` hooks, so ensure you've run `make install` before.

```bash
make codestyle
```

</p>
</details>

<details>
<summary>6. Run tests</summary>
<p>

```bash
make test
```

</p>
</details>

<details>
<summary>7. Run all the linters</summary>
<p>

```bash
make lint
```

the same as:

```bash
make test && make check-safety && make check-style
```

> List of flags for `lint` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<!-- <details>
<summary>8. Build docker</summary>
<p>

```bash
make docker
```

which is equivalent to:

```bash
make docker VERSION=latest
```

More information [here](https://github.com/transhaphigsn/freak/tree/master/docker).

</p>
</details>

<details>
<summary>9. Cleanup docker</summary>
<p>

```bash
make clean_docker
```

or to remove all build

```bash
make clean
```

More information [here](https://github.com/transhaphigsn/freak/tree/master/docker).

</p>
</details> -->

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
