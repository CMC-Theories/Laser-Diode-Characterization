import numpy as np
from scipy.optimize import least_squares
from astropy.modeling.models import Voigt1D


# Prep work calculating the voltage to power output and a few other bits of information.
CurrentToVoltageMultiplier = 36.52778 # V/A
PhotodiodeResponsivity = .5 # A/W

IntegratingSphereRadius = .0254 # m
IntegratingSphereInputPortRadius = .00635 # m
IntegratingSphereOutputPortRadius = .0015 # m
IntegratingSphereReflectivity = .99 

DutyCycle = .5
import math


f = (IntegratingSphereInputPortRadius**2 + IntegratingSphereOutputPortRadius**2) / ( (IntegratingSphereRadius**2))
VtoPout = (1/CurrentToVoltageMultiplier) * \
          (1/ PhotodiodeResponsivity) * \
          ( IntegratingSphereInputPortRadius**2)*(1 - IntegratingSphereReflectivity*(1-f)) / (IntegratingSphereOutputPortRadius**2 * IntegratingSphereReflectivity) * \
          (1/DutyCycle)
qO_cXplanks_ = 806554.4 # m^-3 kg^-1 s^3 A


LaserDiodeMirrorReflectivity = .33/.99





# Calculates all parameters and stores them inside of the data object. Assumes lengths is in mm and temps are in C.
def calculateAllParameters(data, lengths, temps, ILInd, IVInd, IPInd, LowInd, MedInd, HighInd):
    for mm in lengths:
        for tmp in temps:
            for current in [LowInd, MedInd, HighInd]:
                for peak_amt in [1,3,7,11,15]:
                    wavs = np.average(data[mm,tmp,current][:,0][np.argpartition(data[mm,tmp,current][:,1], -peak_amt)[-peak_amt:]])*(10**-9)
                    data[mm,tmp,-1, f"peak_wavelength_{current}_{peak_amt}"] = wavs
                    left_half = data[mm,tmp,current][:np.argmax(data[mm,tmp,current][:,1]),0]
                    right_half = data[mm,tmp,current][np.argmax(data[mm,tmp,current][:,1]):,0]
                    half_max = np.max(data[mm,tmp,current][:,1])/2
                    shifted_vals = -np.abs(data[mm,tmp,current][:,1] - half_max) # The new function is the distance away from the half max (but negative), thus arg max is the values closest to the half-max
                    left_shifted = shifted_vals[:np.argmax(data[mm,tmp,current][:,1])]
                    right_shifted = shifted_vals[np.argmax(data[mm,tmp,current][:,1]):]
                    left_wav = np.average(left_half[np.argpartition(left_shifted, -peak_amt)[-peak_amt:]])
                    right_wav = np.average(right_half[np.argpartition(right_shifted, -peak_amt)[-peak_amt:]])
                    data[mm,tmp,-1,f"wavelength_linewidth_{current}_{peak_amt}"] = (right_wav - left_wav) * (10**-9)
            data[mm,tmp,-1,"wav"] = data[mm, tmp, -1, f"peak_wavelength_{MedInd}_3"]
            data[mm, tmp, -1, "wav_line"] = data[mm, tmp, -1, f"wavelength_linewidth_{MedInd}_3"]
    for mm in lengths:
        for tmp in temps:
            opticalPower = data[mm, tmp, ILInd][:,1] * VtoPout
            slopes = np.gradient(opticalPower, data[mm,tmp,ILInd][:,0])
            
            splitPort = 0.25
            lowVal = np.average(slopes[slopes < splitPort])
            highVal = np.average(slopes[slopes > splitPort])
            mid = (highVal + lowVal)/2
            thr = np.argmin((slopes - mid)**2)
            
            DQE = data[mm,tmp,-1,"wav"] *qO_cXplanks_* np.average(slopes[thr:])
            #print(f"DQE ({mm},{tmp}C): {DQE} @ {data[mm,tmp,-1,'wav']}\t {data[mm,tmp,0][:,0][thr]}")
            data[mm,tmp,-1,"DQE"] = DQE
            data[mm,tmp,-1,"threshold_current_ind"] = thr
            data[mm,tmp,-1,"threshold_current"] = data[mm,tmp,ILInd][thr,0]
            abvthr = (thr + len(data[mm,tmp,IVInd][:,0]))//2
            LFP = np.polyfit(data[mm,tmp,IVInd][:,0][abvthr:], data[mm,tmp,IVInd][:,1][abvthr:], 1)
            SRA = LFP[0]
            
            dI = np.gradient(data[mm,tmp,IVInd][:,0][thr:])
            dV = np.gradient(data[mm,tmp,IVInd][:,1][thr:])
            
            SRD = np.mean(dV/dI)
            data[mm,tmp,-1, "Series Resist"] = (SRA, SRD)
            data[mm,tmp,-1,"dIdV"] = (dI, dV)
            
            ILD = data[mm,tmp,IPInd][abvthr:,:]
            Pin= data[mm,tmp,IVInd][abvthr:,0] * data[mm,tmp,IVInd][abvthr:,1]
            Pout = ILD[:,1]
            data[mm,tmp,-1,"WPE"] = np.mean(Pout/Pin)
            ideal_params = np.polyfit(np.log(data[mm,tmp,IVInd][50:abvthr,0]), np.log(data[mm,tmp,IVInd][50:abvthr,1]),1)
            data[mm,tmp,-1,"ideality"] = ideal_params[0]*(1.60/(1.38*(273.15 + tmp)))*10**4
    for mm in lengths:
        avgT0 = 0
        for tmi in range(len(temps)-1):
            avgT0 = avgT0+ (temps[tmi] - temps[tmi+1]) / np.log(data[mm,temps[tmi],-1,"threshold_current"]/data[mm,temps[tmi+1],-1,"threshold_current"])
        for tmp in temps:
            data[mm,tmp,-1,"T0"] = avgT0/(len(temps)-1) # Kelvin
    for tmp in temps:
        avgai = 0
        avgni = 0
        for mmi in range(len(lengths)-1):
            avgai = avgai+ -np.log(LaserDiodeMirrorReflectivity)*(data[lengths[mmi],tmp,-1,"DQE"] - data[lengths[mmi+1],tmp,-1,"DQE"])/(0.1*((0.0 + lengths[mmi])*data[lengths[mmi],tmp,-1,"DQE"] - (0.0 + lengths[mmi+1])*data[lengths[mmi+1],tmp,-1,"DQE"]))
            avgni = avgni+ data[lengths[mmi],tmp,-1,"DQE"]* data[lengths[mmi+1],tmp,-1,"DQE"] * (lengths[mmi] -lengths[mmi+1])/(lengths[mmi]*data[lengths[mmi],tmp,-1,"DQE"] - lengths[mmi+1]*data[lengths[mmi+1],tmp,-1,"DQE"])
        for mm in lengths:
            data[mm,tmp,-1,"ai"] = avgai/(len(lengths)-1)
            data[mm,tmp,-1,"ni"] = avgni/(len(lengths)-1)