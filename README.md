# An open source toolbox to automate basin and petroleum system modeling for statistical analysis and uncertainty quantification

Basin and petroleum system modeling is an important process to understand and validate petroleum concepts. Traditionally, the models are constructed, calibrated, and examined manually. This can be time-consuming as the number of parameters used in these models and their associated uncertainties is commonly large. The objective of this work is to enable advanced statistical analysis to basin and petroleum modeling simulation by enabling automation of model modification, model running, and interrogation of simulation results.
Methods, Procedures, Process: Please briefly explain your overall approach, including your methods, procedures, and process. (maximum 250 words/1500 characters)
An open source toolbox is developed using Python to control basin and petroleum system modeling simulations. Inputs and outputs are presented to user in the standard formats used in the Python scientific stack, e.g., Python objects, numpy arrays, and Pandas data frames. This allows integration with the large wealth of open source scientific and statistical packages available in the community. Model parameters that can be automatically updated include burial history, heat flow, and paleowater depth. Other parameters such as lithologic parameters and source rock kinetics can also be updated.

Practically, a project and starting template model is created in the software. This template is then modified automatically using the toolbox. For example, the model can be duplicated, modified, run automatically, and results are extracted. Generally, two workflows are followed: sequential, and parallel. In sequential workflows, such as in some workflows related to automated calibration, the toolbox can assist by removing human interactions between runs. In parallel workflows, such as in some sensitivity analysis workflows, multiple models can be simulated in parallel and thereby reduce the time it takes to reach the final results. 

We show that such toolbox is useful for practical applications related to basin and petroleum system modeling such parameter sensitivity analysis, automated calibration, and uncertainty quantification in Bayesian frameworks. For example, model sensitivity studies are run by sampling model parameters from prior distributions to construct model realizations. These constructed models are run in parallel. The results are then loaded back into the toolbox and analyzed using sensitivity analysis methods such as distance-based global sensitivity analysis. Another example is the use of parameter optimization toolkits to automatically calibrate basin models to observed well data, such as by modifying lithological parameters such as compaction model, and porosity-permeability relationships. 
Overall, the toolbox can be utilized in researching new workflows and in operational setting to construct end-to-end solutions related to basin and petroleum system modeling. In operational setting, graphical user interfaces are constructed for ease of use based on the user needs. Thus, all complexities of coding are hidden from the user.

The application programming interface toolbox extends an existing established basin and petroleum system modeling simulator. Thus, it is of use to the practicing geoscientists, especially with the move towards geoscientific analyses while taking uncertainty into account. The toolbox also opens more advanced opportunities such as accelerating automated calibration by combining machine learning proxy models with traditional basin and petroleum system modeling simulators.

# Usage
See notebook for example application

# Citing/referencing
If you use this code, please reference this paper:

Al Ibrahim, Mustafa A., 2023, An open source toolbox to automate basin and petroleum system modeling for statistical analysis and uncertainty quantification, Presented at IMAGE 23, Houston, Texas, 5 p.

 
