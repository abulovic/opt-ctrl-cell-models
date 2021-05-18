# opt-ctrl-cell-models
Simple optimal control cell models with different degrees of complexity. They are encoded in JSON files which can be converted into Bocop-compatible files and simulated using the mentioned software (https://www.bocop.org/).

## Models
There are two types of models included. One type is without, and the other with mRNA production.
In both cases, I provide simple cell models of varying degrees of complexity. The simplest one includes only a ribosome and an enzyme, while the most complex one features three different types of enzymes, ribosome, chaperone, protease and housekeeping protein.
The original intent behind developing models was to study adaptation to heat shock. Therefore, certain parameters of the models are functions of the temperature.

## Simulation
All of the models can be converted to Bocop-compatible files and simulated as a standalone optimal control problem using Bocop.
As my objective was to study adaptation to changing temperature, and as this cannot be done in a single simulation, I have developed a receding horizon simulation that uses Bocop simulator for the individual simulation steps.
In order to use the simulators developed here, you need to:
* have Bocop downloaded and unpackaged on your computer,
* edit the ```BOCOPPATH``` variable in the ```py/build.sh``` file to point to the directory where the Bocop is unpackaged on your computer and
* have ```python3``` installed.
Each simulation will store the simulation results in the ```PATH_TO_MODEL/results/``` directory, and the name of the results directory will be the date and time of simulation. In it, you can find the plots of all the states, algebraic variables, controls and adjoing variables of the receding horizon problem. You can also find the ```txt``` files which contain the original data which is represented in the plots.
Additionaly, for the sake of reproducibility, in each result directory you can find a ```model.tar.gz``` file which containts the original JSON model files, generated bocop files, results in txt format and the plots.

The code I offer is really not of premium quality in the sense of style, but it does the job.
You can choose which model you want to simulate by editing the ```receding_horizon.py``` file, by changing the ```MODELS_DIR``` and ```MODEL_NUM``` variables.
You can edit the sequence of temperatures to which the model will react by editing ```T_VEC```. The time that elapses between the temperature changes is given in the ```TIMESTEP``` variable.

Therefore, to run the simulation, you make the appropriate adjustments to the ```receding_horizon.py``` file and run it:
```python3 receding_horizon.py```
If you chose to simulate model number 8 from the ```cell_models_mRNA``` type, the results will be in ```cell_models_mRNA/model_8/results/[DATE_AND_TIME]``` directory.
