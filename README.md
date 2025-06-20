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
poetry env activate
```

## Running single experiment

```bash
python -m illusion_of_thinking.run_experiments
``` 

### Command-line options

- `--simulator_type`: Type of simulator to use. Choices: `TowerOfHanoi`, `RiverCrossing`. **(required)**
- `--N`: Number of disks for Tower of Hanoi or number of actors for River Crossing. **(required)**
- `--k`: Maximum boat capacity for River Crossing (ignored for Tower of Hanoi). Default: `2`.
- `--use_tools`: Whether to use simulator tools. (flag)
- `--use_thinking`: Whether to use a thinking model or not. (flag)
- `--output_folder`: Output folder for experiment results. Default: `logs`. **(required)**

Example usage:
```bash
MISTRAL_API_KEY=<your_api_key> python -m illusion_of_thinking.run_experiment --simulator_type TowerOfHanoi --N 3 --output_folder results
```



## Running tests

```bash
# Run tests
poetry run pytest
```

## Documentation

A detailed on the implementations done in this repository can be found [here](docs/index.md).