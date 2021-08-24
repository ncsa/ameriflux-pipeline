# AmeriFlux-pipeline

**AmeriFlux-pipeline** is an automated process of handling flux data <br>
TODO: need to revised and rewritten

## Prerequisites

* Requirements: Python 3.8+, Anaconda or Miniconda.
## Files :
- data
  - csv files to be processed for EddyPro
- preprocessing.py takes care of the data preprocessing steps
- main.py is the main file to run.
- requirements.txt lists the required packages
## Installation

1. Clone the GitHub repository
```
git clone https://github.com/ncsa/ameriflux-pipeline.git
```
2. Change working directory
```
cd ameriflux-pipeline
```
3. Install dependencies: The model is tested on Python 3.8, with dependencies listed in requirements.txt. To install these Python dependencies, please run
```
pip install -r requirements.txt
```
Or if you prefer to use conda,
```
conda install --file requirements.txt
```
## Usage :
1. To request all command line parameters, please run:
```
python main.py --help
```
2. To run python module with default parameters, please run:
```
python main.py
```
3. Specify input data path with input agrument and output data path with output argument. For example :
```
python main.py --input data/<filename>.csv --output <filename>.csv
```