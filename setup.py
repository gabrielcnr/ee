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
        "console_scripts": [
            "ee = ee.cli:main",
            "ee-admin = ee.admin_cli:app",
            "ee-server = ee.server:run",
        ],
    },
)
