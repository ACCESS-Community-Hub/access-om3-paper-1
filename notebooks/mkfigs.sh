#!/bin/bash
# bash script that runs all the notebooks
set -x
python run_nb.py notebook_template.ipynb my_input_file --int_param 16
