# Documentation on l2format module
This document is a code walk-through on l2format.py module

## Overview
- The [l2format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pyfluxpro/l2format.py) process creates the L2 control file for EPL-type processing.
- The module creates L2 control file based on and L2 template control file and the L1 control file produced by [l1format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l1format.md) process.
- This output L2 control file is used as input for the PyFluxPro software. 
- The pipeline calls this process in [step#15](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#15) of pre-pyfluxpro module, after the [l1format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l1format.md) process.

## Instructions to run

### Using the GUI
- There is an option to run this module from the [pipeline.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pipeline.py) GUI.
- Launch the GUI by executing ```python pipeline.py``` command.
- Click the "Run" button in the "Run PyFluxPro data preparation" section.

### Using the command line
- Running ```python pre_pyfluxpro.py``` will execute this process along with other modules within [pre_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) module.

## Process

### 1
- Inputs required by this module are described in [step#15](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#15) of pre-pyfluxpro module
- These inputs can be set from the [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md).

### 2
- Validations are done for all inputs
- The L2 files are checked if the "[Variables]", and "[Plots]" section exists and if the "level" is "L2".
- For the input L2 files, each variable is checked if ExcludeDates, RangeCheck and DependencyCheck (these are all PyFluxPro specific instructions for quality control processes) follow the expected format. 
- Validates :
  - If RangeCheck has lower and upper lines and if they are in the right format. See [NOTES #21](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#21).
  - If source line exists for DependencyCheck. In DependencyCheck a target variable is filtered based on the values of a separate source variable; "source" specifies the name of this source variable.
  - If ExcludeDates has "from" and "to" dates that are comma separated and if the dates are valid (in correct date format and the start date is earlier than the end date).
- If the validations fail, an error message is logged and process aborted.

### 3
- After validation, variables in the template L2 control file are read.
- The read variables are compared with the variables in output L1 (produced by [l1format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l1format.md)). 
- Only the variables present in BOTH the template L2 control file and the output L1 control file are to output L2 control file. The variables present in Soils key are written if present in output L1 control file, as long as at least one soil moisture and soil temperature variable is present in template L2 file.
- The variables are renamed to Ameriflux labels according to Ameriflux-Mainstem-Key file as described in [step#4 of l1format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l1format.md#4).
- The variables are also checked for duplicates. On encountering duplicate variables, the second occurance of the variable is ignored and note written to the output L2 control file.

### 4
- The soil moisture variables are converted to percentage values. The lower and upper ranges in the RangeCheck dependency are converted to percentage values.
- For DependencyCheck(s) on flux variables, the source H2O_SIGMA is used instead of H2O_IRGA_Vr. See [NOTES #14](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#14).
- DependencyCheck(s) used to implement footprint filtering (x_[0-9]) are removed.

### 5
- On successful completion of L2 format, a message will be logged and output L2 file written to the user specified location.

