<!--    
    ================================================================================================
-->

# Erpeton

*A production-oriented Python chess engine module based on Stockfish 11, focused on providing 
low-latency move validation and classical search-based best-move selection.*

<!--    
    ================================================================================================
-->

## Project Structure at a Glance

```sh
erpeton/
├── recipes/erpeton/    # Conda recipe for building and installing the project
│                       # as a dependency via `pixi build`.
│
├── LICENSE.txt         # Full text of the project's license.
│
├── pixi.toml           # Pixi environment configuration for installing the project
│                       # for development.
│
└── pixi.lock           # Fully resolved and reproducible dependency lockfile for
                        # installing the project for development.
```

<!--    
    ================================================================================================
-->

## Installation as a Dependency

### I. Prerequisites

| **Component**               | **Requirement**   |
| :-------------------------- | :---------------- |
| **Operating System**        | `GNU/Linux`-based |
| **Package Management Tool** | [`Pixi`](https://pixi.prefix.dev/latest/#installation) with `pixi-build` feature enabled |

<!--    
    ================================================================================================
-->

### II. Adding the package

To install `erpeton`, run:

```sh
pixi add \
    --git https://github.com/snegoviol/erpeton \
    --subdirectory recipes/erpeton \
    erpeton
```

### III. Usage

Once the package is installed, you can start using it in your project. Basic usage examples are provided in the module's built-in documentation, which you can view in one of two ways:

- To view it directly in the terminal, run:

    ```sh
    pixi run python -c "import erpeton; help(erpeton)"
    ```

- To view it directly in the source code, refer to the [`recipes/erpeton/src/erpeton/__init__.py`](recipes/erpeton/src/erpeton/__init__.py).

<!--    
    ================================================================================================
-->

## Installation for Development

### I. Prerequisites

| **Component**               | **Requirement**                |
| :-------------------------- | :----------------------------- |
| **CPU**                     | Supports `x86_64` architecture |
| **Operating System**        | `GNU/Linux`-based              |
| **Package Management Tool** | [`Pixi`](https://pixi.prefix.dev/latest/#installation) |

> **Note:**  
> These are not strict requirements, but rather the baseline environment where the code is 
guaranteed to run out of the box. Alternative setups are possible but may require manual 
configuration.

<!--    
    ================================================================================================
-->

### II. Setup

1. **Clone the repository**

    ```sh
    git clone https://github.com/snegoviol/erpeton.git
    cd erpeton
    ```

2. **Install dependencies**

    ```sh
    pixi install
    ```

3. **Activate environment**

    ```sh
    pixi shell
    ```

<!--    
    ================================================================================================
-->

### III. Next Steps

Once the environment is activated, you are ready to develop. You can:

- Integrate the engine into Python backends or applications.
- Modify the C++ core or `pybind11` bindings.
- Execute performance benchmarks and run the test suite.
- Iterate on search configurations and engine parameters.

<!--    
    ================================================================================================
-->

## Why «Erpeton»?

The name refers to the [tentacled snake (*Erpeton tentaculatum*)](https://en.wikipedia.org/wiki/Tentacled_snake), an aquatic Southeast Asian snake whose diet consists exclusively of fish. It hunts by ambush: it triggers a fish’s escape reflex and strikes where it expects the fish’s head to be, rather than where the fish currently is.

- **A snake-themed Python project.**  
Python projects are often named after snakes — for example, [Anaconda](https://github.com/conda/conda), [Mamba](https://github.com/mamba-org/mamba), and [Rattler](https://github.com/prefix-dev/rattler-build). *Erpeton* follows that tradition.

- **Fast by design.**  
Like the tentacled snake, *Erpeton* is built for a rapid strike. Its engine is implemented entirely in C++ and exposed to Python through pybind11, keeping move validation and best-move selection low-latency.

- **It hunts Stockfish.**  
*Erpeton* is based on Stockfish 11. In the spirit of the tentacled snake’s fish-based diet, the module can be said to "eat Stockfish": it builds on the engine and adapts it into a production-oriented Python chess engine module.

<!--    
    ================================================================================================
-->

## License

This project is a derivative work of [Stockfish 11](https://github.com/official-stockfish/Stockfish/tree/c3483fa9a7d7c0ffa9fcc32b467ca844cfb63790), which is licensed under the [GNU General Public License v3.0 or later](LICENSE.txt). Consequently, this project is licensed under the same terms.

<!--    
    ================================================================================================
-->
