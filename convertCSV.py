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
root.destroy()
xx = np.genfromtxt(file_path, skip_header=33, delimiter=';', skip_footer=1)

xox = path.split(file_path)
print(xox[0] + "\out\\"+xox[1])

cl = xx[1800:1950, :]
np.savetxt(xox[0] + "\out\\"+xox[1],cl, delimiter="," )


import matplotlib.pyplot as plt
plt.scatter(cl[:,0], cl[:,1])
plt.show()

print("average wavelength: ", np.average(cl[np.argpartition(cl[:,1], -3)[-3:],0]))
