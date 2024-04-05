import sys
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit.sping import PIL

def draw_chem(str):
    m = Chem.MolFromSmiles(str)
    Draw.MolToFile(m,"./app/sample.png")
