# BranchedGP

BranchedGP is a package for building Branching Gaussian process models in python, using [TensorFlow](github.com/tensorflow) and [GPFlow](https://github.com/GPflow/GPflow). 
The model is described in the paper

["BGP: Branched Gaussian processes for identifying gene-specific branching dynamics in single cell data", 
Alexis Boukouvalas, James Hensman, Magnus Rattray, bioRxiv, 2017.](http://www.biorxiv.org/content/early/2017/08/01/166868).

This is now published in [Genome Biology](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-018-1440-2).
[![Build Status](https://travis-ci.org/ManchesterBioinference/BranchedGP.svg?branch=master)](https://travis-ci.org/ManchesterBioinference/BranchedGP)
[![codecov](https://codecov.io/gh/ManchesterBioinference/BranchedGP/branch/master/graph/badge.svg)](https://codecov.io/gh/ManchesterBioinference/BranchedGP)

# Example
An example of what the model can provide is shown below.
   1. The posterior cell assignment is shown in top subpanel: each cell is assigned a probability of belonging to a  branch.
   1. In the bottom subpanel the posterior branching time is shown: the probability of branching at a particular pseudotime.
<img src="images/VAMP5_BGPAssignmentProbability.png" width="400" height="400" align="middle"/>

# Install

We use [Poetry](https://python-poetry.org/) to manage and install dependencies.
To install the package in a local virtual environment:
* [Install poetry](https://python-poetry.org/docs/#installation), and
* Run `poetry install`.

# Quick start
For a quick introduction see the `notebooks/Hematopoiesis.ipynb` notebook.
Therein we demonstrate how to fit the model and compute
the log Bayes factor for two genes.

The Bayes factor in particular is calculated by calling `CalculateBranchingEvidence`
after fitting the model using `FitModel`.

This notebook should take a total of 6 minutes to run.

# List of notebooks
To run the notebooks
```
cd BranchedGP/notebooks
jupyter notebook
```

| File <br> name | Description | 
| --- | --- | 
| Hematopoiesis       | Application of BGP to hematopoiesis data. |
| SyntheticData       | Application of BGP to synthetic data. |
| SamplingFromTheModel| Sampling from the BGP model. |


# Comparison to monocle-BEAM

In the paper we compare the BGP model to the BEAM method proposed
in monocle 2. In ```monocle/runMonocle.R``` the R script for performing
Monocle and BEAM on the hematopoiesis data is included.
# List of python library files
| File <br> name | Description | 
| --- | --- | 
| FitBranchingModel.py | Main file for user to call BGP fit, see function FitModel | 
| pZ_construction_singleBP.py | Construct prior on assignments; use by variational code. |
| assigngp_dense.py | Variational inference code to infer function labels. |
| assigngp_denseSparse.py | Sparse inducing point variational inference code to infer function labels. |
| branch_kernParamGPflow.py | Branching kernels. Includes independent kernel as used in the overlapping mixture of GPs and a hardcoded branch kernel for testing. |
| BranchingTree.py | Code to generate branching tree. |
| VBHelperFunctions.py | Plotting code. |

# Troubleshooting

## Python3.7

TensorFlow1 only supports Python up to version 3.7.
This presents a slight problem as modern operating systems tend to default 
to Python3.8.
In order to install Python3.7 on a Debian-based Linux:
* Add [the deadsnakes repository](https://github.com/deadsnakes) 
  via `sudo add-apt-repository ppa:deadsnakes/ppa`. 
* `sudo apt-get install python3.7-dev python3.7-venv`

## Poetry

It sometimes gets confused when there are multiple Python versions on your system.
If you're having any strange installation issues at all, we recommend creating 
a fresh Python3.7 virtual environment and then running poetry commands in it:
* `python3.7 -m venv .venv`
* `source .venv/bin/activate`

# Tasks

We use poetry with [taskipy](https://github.com/illBeRoy/taskipy) 
to ensure standard tasks are easy to run.

Use `poetry run task <task_id>` where `<task_id>` is one of the following:
* `run_jupyter`. This will start a [jupyter](https://jupyter.org/) server 
  enabling you to work on notebooks.
* `all_checks`. This will run the tests, formatting checks and static code analysis.
* `format`. This will re-format the code according to [black](https://pypi.org/project/black/) 
  and [isort](https://pypi.org/project/isort/). 

For other `<task_id>` values, please see `pyproject.toml`.
