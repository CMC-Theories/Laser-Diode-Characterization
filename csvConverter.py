import numpy as np
import sys
import tkinter as tk
from tkinter import filedialog
import os.path as path
root = tk.Tk()
root.withdraw()
if len(sys.argv) == 1:
    file_path = filedialog.askopenfilename()
else:
    file_path = sys.argv[1]

xx = np.genfromtxt(file_path, skip_header=33, delimiter=';', skip_footer=1)

xox = path.split(file_path)
print(xox[0] + "\out"+xox[1])
np.savetxt(xox[0] + "\out"+xox[1],xx, delimiter="," )
filedialog.asksaveasfilename