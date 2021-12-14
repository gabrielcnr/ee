from setuptools import find_packages, setup

setup(
    name="ee",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "ee-run = ee.cli:app",
            "ee-admin = ee.admin_cli:app",
            "ee-server = ee.server:run",
        ],
    },
)
