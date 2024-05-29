# Mapper Interactive (Particularly for chemistry)



Mapper Interactive is a web-based framework for interactive analysis and visualization of high-dimensional point cloud data  built upon the Mapper algorithm. It is an open source software released under the MIT License.

The Mapper algorithm is a tool from topological data analysis first introduced by Gurjeet Singh, Facundo Mémoli and Gunnar Carlsson in 2007 (http://dx.doi.org/10.2312/SPBG/SPBG07/091-100). 


## Installation

```bash
git clone https://github.com/DhruvMeduri/chemical_mapper.git
cd MapperInteractive
python3 run.py
```

After running the above commands, you can run Mapper Interactive by visiting http://127.0.0.1:8080/ on the local machine (If possible, please use Chrome).

## Dependencies
This software requires [Kepler Mapper](https://kepler-mapper.scikit-tda.org/), [scikit-learn](https://scikit-learn.org/stable/), [NetworkX](https://networkx.github.io/), [flask](https://flask.palletsprojects.com/en/1.1.x/) and [rdkit](https://www.rdkit.org/) to run.

If you do not have these packages installed, please use the following command to intall them.

```bash
pip install scikit-learn
pip install networkx
pip install flask
pip install flask_assets
pip install rdkit
```

## Command-line API
Please refer to a user-guide [here](CLI_README.md) for the command-line API. For larger dataset with more that 50k points, one will need to use the CLI implementation.

## Interactive Visualizaton of precomputed Mapper

Place the computed mapper graph (final_.json) in the CLI_examples folder along with the conrresponding processed_data.csv file. Both these files will be generated by the end of running the CLI script. Then import the CLI_examples folder using import graph on the sidebar. A few of the  mappers and processed_data files have been uploaded to the following google drive.




