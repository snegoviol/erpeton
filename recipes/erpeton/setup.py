# ==================================================================================================
# recipes/erpeton/setup.py
# ==================================================================================================

from pathlib import Path
from setuptools import setup, Extension
import pybind11

# ==================================================================================================

CORE = Path("src/erpeton")
STOCKFISH = CORE / "stockfish11"

sources = [
    str(CORE / "_core.cpp"),
    *[str(p) for p in STOCKFISH.glob("*.cpp")],
    str(STOCKFISH / "syzygy" / "tbprobe.cpp"),
]

# ==================================================================================================

setup(
    ext_modules= [
        Extension(
            "erpeton._core",
            sources=sources,
            include_dirs=[
                str(CORE),
                pybind11.get_include(),
            ],
            language="c++",
            extra_compile_args=[
                "-O3",
                "-DNDEBUG",
                "-march=native",
                "-DUSE_POPCNT",
                "-fvisibility=hidden",
                "-pthread",
                "-std=c++14",
            ],
            extra_link_args=[
                "-pthread"
            ],
        ),
    ]
)

# ==================================================================================================
