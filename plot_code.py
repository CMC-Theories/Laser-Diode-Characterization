

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def get_str(spectrum_id, LowInd, MedInd, HighInd):
    if spectrum_id == LowInd:
        return "below"
    elif spectrum_id == MedInd:
        return "at"
    elif spectrum_id == HighInd:
        return "above"
    else:
        return "error"
# Raw spectra
def plotSpectraRaw_Sep(file_dir, spectrum_id, show_plots, data, lengths, temps, ILInd, IVInd, IPInd, LowInd, MedInd, HighInd):
    spec_name = get_str(spectrum_id, LowInd, MedInd, HighInd)
    if spec_name == "error":
        for mm in lengths:
            for tmp in temps:
                for sp in [LowInd, MedInd, HighInd]:
                    plt.figure()
                    spec_name = get_str(sp, LowInd, MedInd, HighInd)
                    sf = data[mm,tmp,sp][:,1]#savgol_filter(data[mm,tmp,2][:,1], 51, 1)
                    plt.plot(data[mm,tmp,sp][:,0], sf / np.max(sf), label=f"{mm}mm {tmp}C")
                    plt.axvline(data[mm,tmp,sp][:,0][np.argmax(sf)],linestyle='--', c=plt.gca().lines[-1].get_color())
                    plt.xlim(left=790, right=820)
                    plt.ylim(top=1.25,bottom=0)
                    plt.xlabel("Wavelength (nm)")
                    plt.ylabel("Intensity (arbitrary)")
                    plt.yticks([])
                    plt.title(f"Spectrum {spec_name} threshold current (raw)")
                    plt.savefig(f"{file_dir}{mm}mm_{tmp}C_{spec_name}_raw.png")
                    if show_plots:
                        plt.show()
    else:
        for mm in lengths:
            for tmp in temps:
                plt.figure()
                sf = data[mm,tmp,spectrum_id][:,1]#savgol_filter(data[mm,tmp,2][:,1], 51, 1)
                plt.plot(data[mm,tmp,spectrum_id][:,0], sf / np.max(sf), label=f"{mm}mm {tmp}C")
                plt.axvline(data[mm,tmp,spectrum_id][:,0][np.argmax(sf)],linestyle='--', c=plt.gca().lines[-1].get_color())
                plt.xlim(left=790, right=820)
                plt.ylim(top=1.25,bottom=0)
                plt.xlabel("Wavelength (nm)")
                plt.ylabel("Intensity (arbitrary)")
                plt.yticks([])
                plt.title(f"Spectrum {spec_name} threshold current (smoothed)")
                plt.savefig(f"{file_dir}{mm}mm_{tmp}C_{spec_name}_raw.png")
                if show_plots:
                    plt.show()    

def plotSpectraSmoothed_Sep(file_dir, spectrum_id, show_plots,smoothing_params, data, lengths, temps, ILInd, IVInd, IPInd, LowInd, MedInd, HighInd):
    spec_name = get_str(spectrum_id, LowInd, MedInd, HighInd)
    if spec_name == "error":
        for mm in lengths:
            for tmp in temps:
                for sp in [LowInd, MedInd, HighInd]:
                    plt.figure()
                    spec_name = get_str(sp, LowInd, MedInd, HighInd)
                    sf = savgol_filter(data[mm,tmp,sp][:,1], *smoothing_params)
                    plt.plot(data[mm,tmp,sp][:,0], sf / np.max(sf), label=f"{mm}mm {tmp}C")
                    plt.axvline(data[mm,tmp,sp][:,0][np.argmax(sf)],linestyle='--', c=plt.gca().lines[-1].get_color())
                    plt.xlim(left=790, right=820)
                    plt.ylim(top=1.25,bottom=0)
                    plt.xlabel("Wavelength (nm)")
                    plt.ylabel("Intensity (arbitrary)")
                    plt.yticks([])
                    plt.title(f"Spectrum {spec_name} threshold current (smoothed)")
                    plt.savefig(f"{file_dir}{mm}mm_{tmp}C_{spec_name}_smoothed.png")
                    if show_plots:
                        plt.show()
    else:
        for mm in lengths:
            for tmp in temps:
                plt.figure()
                sf = savgol_filter(data[mm,tmp,spectrum_id][:,1], *smoothing_params)
                plt.plot(data[mm,tmp,spectrum_id][:,0], sf / np.max(sf), label=f"{mm}mm {tmp}C")
                plt.axvline(data[mm,tmp,spectrum_id][:,0][np.argmax(sf)],linestyle='--', c=plt.gca().lines[-1].get_color())
                plt.xlim(left=790, right=820)
                plt.ylim(top=1.25,bottom=0)
                plt.xlabel("Wavelength (nm)")
                plt.ylabel("Intensity (arbitrary)")
                plt.yticks([])
                plt.title(f"Spectrum {spec_name} threshold current (smoothed)")
                plt.savefig(f"{file_dir}{mm}mm_{tmp}C_{spec_name}_smoothed.png")
                if show_plots:
                    plt.show()    

def plotILCurve_Sep(file_dir, show_plots, data, lengths, temps, ILInd, IVInd, IPInd, LowInd, MedInd, HighInd):
    for mm in lengths:
        for tmp in temps:
            plt.figure()
            plt.plot(data[mm,tmp,IPInd][:,0], data[mm,tmp,IPInd][:,1])
            plt.xlabel("Current (A)")
            plt.ylabel("Optical Power (W)")
            plt.title(f"I-L Curve for {mm}mm at {tmp}C")
            plt.savefig(f"{file_dir}{mm}mm_{tmp}C_ILPlot.png")
            if show_plots:
                plt.show()

def plotVICurve_Sep(file_dir, show_plots, data, lengths, temps, ILInd, IVInd, IPInd, LowInd, MedInd, HighInd):
    for mm in lengths:
        for tmp in temps:
            plt.figure()
            plt.plot(data[mm,tmp,IVInd][:,1], data[mm,tmp,IVInd][:,0])
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (I)")
            plt.title(f"V-I Curve for {mm}mm at {tmp}C")
            plt.savefig(f"{file_dir}{mm}mm_{tmp}C_VIPlot.png")
            if show_plots:
                plt.show()