# Machine learning for anomaly detction in financial data
This repository is submitted as part of undergraduate final year project at 
Queen Mary, University of London - School of Electronic Engineering and Computer Science 
as part of requirements fulfilment for the Digital and Technology Solutions (Software Engineer)
undergraduate programme.

Student name: Martin Sedlacek

# User Manual

The purpose of this document is to help the reader navigate through the code base submitted with the final report and set-up the environment to train the models discussed. 

## 1.1 Environment set-up

Firstly, ensure the latest version of python is installed on your machine.

1. Set up a virtual environment. This project used Conda and this guide is written 
for this one specifically. Using venv with pip should also work fine.
   

    conda create --name <ml_in_fin_data>
    conda activate <ml_in_fin_data>


3. Install the following dependencies:


    pytorch CPU -> conda install pytorch cpuonly -c pytorch
    (alternative) pytorch for CUDA GPUs -> conda install pytorch cudatoolkit=11.3 -c pytorch
    sklearn -> conda install -c anaconda scikit-learn
    pandas -> conda install -c anaconda pandas
    numpy -> conda install -c anaconda numpy
    Jupyter -> conda install -c anaconda jupyter
    PyOD -> conda install -c conda-forge pyod

4. Run the following command to start the jupyter server


    jupyter notebooks


## 1.2 Running the models

1. Navigate to the project folder on your disk
2. Open a .ipynb notebook for the model you wish to test
3. Set hyperparameters in the according cell, this will need to be adjusted for each dataset 
4. Press the "RUN ALL" button and select "restart kernel and run all" (most right in the topbar)

NOTE: If you are using GPU computation, which is selected by default at the top of the notebooks, 
this might cause issues, as the machine will be different from the one where the models
were originally trained on (different RAM, GPU memory, etc.). To solve this you can set
DEVICE="cpu" or troubleshoot the errors yourself. Reducing batch size has solved memory issues
during development. Sometimes there are random errors with GPU computation that just require you
to restart the notebook.

## 1.3 EDA and plot generation

Notebook are also provided for reproducing the figures for EDA and final evaluation. 
These just have to be open and run, same as the model notebooks. 