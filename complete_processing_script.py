file_dir = r"D:\Mylife\Desktop\FinalFolder\Data" + "\\"
file_out_dir = r"D:\Mylife\Desktop\FinalFolder\Output" + "\\"
temps = [20,35]
lengths = [2,3]
ILInd = 0
IVInd = 1
IPInd = 2
LowInd = 3
MedInd = 4
HighInd = 5
index_array = [ILInd, IVInd, IPInd, LowInd, MedInd, HighInd]

experiments = [[j,i] for i in temps for j in lengths]
files = [f"{i[0]}mm_{i[1]}C" for i in experiments]
file_endings = ["_IL.csv", "_IV.csv", "_IP.csv", "_avg_low.csv", "_avg_at.csv", "_avg_high.csv"]
files_all = [[f"{file_dir}{i}{j}" for j in file_endings] for i in files]

from datamanagement import DataManagement

data = DataManagement(files_all,experiments)

from calculate_parameters import calculateAllParameters

# Calculates all laser diode parameters based on provided values
calculateAllParameters(data, lengths, temps, *index_array)

def printOutAllParametersInTable(data):
    labels = ["Current Threshold", "Diff. Quant. Eff.", "Wall Plug Eff.","Series Resistance","Peak Wavelength below threshold","-- at threshold","-- above threshold","Linewidth below threshold","-- at threshold","-- above threshold"]
    elab = ["threshold_current", "DQE", "WPE", "Series Resist"]
    alab = [f"peak_wavelength_{LowInd}_3",f"peak_wavelength_{MedInd}_3",f"peak_wavelength_{HighInd}_3", f"wavelength_linewidth_{LowInd}_3",f"wavelength_linewidth_{MedInd}_3",f"wavelength_linewidth_{HighInd}_3"]
    print("Parameter name",end=",")
    for mm in lengths:
        for tmp in temps:
            print(f"{mm}mm {tmp}C",end=",")
    print("")
    for label in range(len(labels)):
        print(labels[label], end=",")
        if label >= 4:
            for mm in lengths:
                for tmp in temps:
                    print(data[mm,tmp,-1,alab[label-4]],end=",")
        else:
            for mm in lengths:
                for tmp in temps:
                    if label == 3:
                        print(data[mm,tmp,-1, elab[label]][0],end=",")
                    else:
                        print(data[mm,tmp,-1, elab[label]],end=",")
        print("")
    print("Parameter name",end=",")
    for tmp in temps:
        print(f"T={tmp}C",end=",")
    for mm in lengths:
        print(f"L={mm}mm", end=",")
    print("")
    nlabels = ["Injection Efficiency", "Internal Optical Loss", "Characteristic Temperatures"]
    nlab = ["ni","ai", "T0"]
    for ll in range(len(nlabels)):
        print(nlabels[ll], end=",")
        if ll != 2:
            for tmp in temps:
                print(data[lengths[0], tmp, -1, nlab[ll]],end=",")
            for mm in lengths:
                print("N/A", end=",")
        else:
            for tmp in temps:
                print("N/A", end=",")
            for mm in lengths:
                print(data[mm, temps[0], -1, nlab[ll]],end=",")
        print("")


from plot_code import *


plotVICurve_Sep(file_out_dir, False, data, lengths, temps, *index_array)
plotILCurve_Sep(file_out_dir, False, data, lengths, temps, *index_array)
plotSpectraSmoothed_Sep(file_out_dir, -1, False, [15, 1], data, lengths, temps, *index_array)

printOutAllParametersInTable(data)