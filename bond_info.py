from rdkit.Chem import MolFromSmiles, rdmolops
from rdkit.Chem import AllChem, AddHs
import numpy as np
import json
import linecache
from random import sample
from matplotlib import pyplot as plt

def mean_angle(m):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem import rdMolTransforms
    #m = Chem.MolFromSmiles('CCOC(=O)C(C#N)=NNc1ccc(S(=O)(=O)NC(C)=O)cc1')
    AllChem.MMFFOptimizeMolecule(m)
    conf = m.GetConformer()
    count = 0
    mean_angle = 0
    for i in m.GetBonds():
        for j in m.GetBonds():
            if i.GetEndAtomIdx() == j.GetBeginAtomIdx():
                count= count +1
                mean_angle = mean_angle + rdMolTransforms.GetAngleDeg(conf, i.GetBeginAtomIdx(),i.GetEndAtomIdx(),j.GetEndAtomIdx())
            elif i.GetEndAtomIdx() == j.GetEndAtomIdx() and i.GetBeginAtomIdx() != j.GetBeginAtomIdx():
                count= count +1
                mean_angle = mean_angle + rdMolTransforms.GetAngleDeg(conf, i.GetBeginAtomIdx(),i.GetEndAtomIdx(),j.GetBeginAtomIdx())
            elif i.GetBeginAtomIdx() == j.GetBeginAtomIdx() and i.GetEndAtomIdx() != j.GetEndAtomIdx():
                count= count +1
                mean_angle = mean_angle + rdMolTransforms.GetAngleDeg(conf, i.GetEndAtomIdx(),i.GetBeginAtomIdx(),j.GetEndAtomIdx())
            elif i.GetBeginAtomIdx() == j.GetEndAtomIdx():
                count= count +1
                mean_angle = mean_angle + rdMolTransforms.GetAngleDeg(conf, i.GetEndAtomIdx(),i.GetBeginAtomIdx(),j.GetBeginAtomIdx())

    return mean_angle/count

def mean_length(mol):
    A=rdmolops.GetAdjacencyMatrix(mol)
    AllChem.MMFFOptimizeMolecule(mol)
    D=AllChem.Get3DDistanceMatrix(mol)
    return np.mean(A*D)

file = open('./CLI_examples/final_component.json')
mapper = json.load(file)
for i in mapper['mapper']['nodes']:
    node_mean_length = 0
    node_mean_angle = 0
    samp = sample(i['vertices'],min(1000,len(i['vertices'])))
    count = 0
    for j in samp:
        line = linecache.getline("./CLI_examples/processed_data.csv", j+2)
        # SMILES for methanol
        smi = line.split(',')[-1]
        mol=MolFromSmiles(smi)
        mol=AddHs(mol)
        if AllChem.EmbedMolecule(mol) > -1:
            count = count + 1
            node_mean_length = node_mean_length + mean_length(mol)
            node_mean_angle = node_mean_angle + mean_angle(mol)
    if count > 0:
        i['avgs']['MHFP6_avg'] = node_mean_length/count
        i['avgs']['MHFP6_rand_avg'] = node_mean_angle/count
    else:
        i['avgs']['MHFP6_avg'] = 0
        i['avgs']['MHFP6_rand_avg'] = 0


with open('./CLI_examples/final_component.json', 'w', encoding='utf-8') as f:
    json.dump(mapper, f, ensure_ascii=False, indent=4)