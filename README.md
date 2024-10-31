# QGIS Jupyter notebook extension: use qgis in jupyter notebook  

## Installation from source

Clone the repository then install with pip from inside the repository:

```
pip install .
```

## Description

Qgis notebook extension is syntactic sugar around qgis to leverage use of qgis in jupyter-notebook environment

Load in your notebook with:

```
%load_ext qgisnbextension
```

## Magic commands

### %qgis

#### How it works

Start a qgis session by initialising a QgsApplication and Message hooks to QgisMessageLog.

Options:

- `--processing` : Initialize Qgis processing providers


## See also

- https://jupyter.org/
- IPython documentation: https://ipython.readthedocs.io/en/stable/config/extensions


