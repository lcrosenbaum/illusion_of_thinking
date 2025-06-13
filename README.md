# illusion_of_thinking
Simulators and code to reproduce illusion_of_thinking from the following publication:

```bibtex
@misc{illusion-of-thinking,
title = {The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity},
author = {Parshin Shojaee*† and Iman Mirzadeh* and Keivan Alizadeh and Maxwell Horton and Samy Bengio and Mehrdad Farajtabar},
year = {2025},
URL = {https://ml-site.cdn-apple.com/papers/the-illusion-of-thinking.pdf}
}
```

## Installation

```bash
# Install poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Running tests

```bash
# Run tests
poetry run pytest
```