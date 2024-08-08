import sys
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit.sping import PIL
from rdkit.Chem import rdRGroupDecomposition
from rdkit.Chem import BRICS
from PIL import Image
from PIL import ImageDraw
import linecache
import base64
from PIL import ImageFont

lst = []

line = linecache.getline("./CLI_examples/processed_data.csv", 20)
structure = line.split(',')[-1]
mol = Chem.MolFromSmiles(structure)
pieces = [Chem.MolFromSmiles(x) for x in BRICS.BRICSDecompose(mol)]


print(pieces)
Draw.MolsToGridImage(pieces,molsPerRow=4)