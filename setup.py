from setuptools import find_packages, setup

setup(
    name="ee",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False,
    use_scm_version={"write_to": "src/ee/_version.py"},
    setup_requires=["setuptools-scm", "setuptools>=30.3.0"],
    python_requires=">=3.8",
    extras_require={"testing": ["pytest", "pytest-mock", "responses"]},
    entry_points={
        "ee_command": [
            "runserver = ee.server:runserver",
            "run = ee.cli:run",
        ],
        "console_scripts": [
            "ee = ee.cli:main",
        ],
    },
)
