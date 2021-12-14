# ee
Environments Everywhere

# Important

For now, client and server live in the same repo. This will change in the near future.

# Installation

```
mamba env create -n ee -f env.yml
```

# Run the server

```
python -m ee.server
```

# Admin CLI

## new

Create a new environment definition from the given JSON file.

For example, consider a file `env.json`:

```json
{
    "packages": {
        "python": "3.9",
        "pandas": ">=1.2,<1.3"
    }
}

```

You can add that environment with:

```bash
python -m ee.admin_cli new env.json
```

## assoc

To associate an environment id (hash) with an application (my-app) and environment (prod):

```
python -m ee.admin_cli assoc my-app prod
```


# Client CLI

## To run stuff

```bash
python -m ee.cli my-app prod python -c "import pandas; print(pandas.__version__)"
```
