## plot the UV density (radial) of the AFC wrt. C43-x+ACA
##
## 25.06.2018 : SL @ ALMA
##

sys.path.append('../arrayconfiguation')
import UVW
import matplotlib.pyplot as pl
from pylab import rcParams

simDir = "/home/stephane/Science/ALMA/ArrayConfig/imaging/fullcombination/simulations"
dataDir = "/home/stephane/Science/ALMA/ArrayConfig/imaging/fullcombination/master/data"
productDir = "/home/stephane/Science/ALMA/ArrayConfig/imaging/fullcombination/simulations/products"


##### Main
    
rcParams['figure.figsize'] = 15, 15.0

xmax = [0,300,400,500,700,1100,1300]
ymax = [0,1e-1]

for i in range(1,7):
    minRadius = 0.
    maxRadius = xmax[i]
    nBin = 50
    
    project1 = "AFC-%d"%(i)   
    msname = "%s/%s/AFC-%d.alma.afc-%d.ms"%(simDir,project1,i,i)
    ms = UVW.UVW(msname)
    rr1, rho1 = ms.radialDensity(minRadius,maxRadius,nBin)
    
    project2 = "C43-%d+ACA"%(i)
    msname = "%s/%s/C43-%d+ACA.concat.ms"%(simDir,project2,i)
    ms = UVW.UVW(msname)
    rr2, rho2 = ms.radialDensity(minRadius,maxRadius,nBin)
    
    
    pl.subplot(3, 2, i)
    pl.plot(rr1,rho1, "g-_",label =  project1)
    pl.plot(rr2,rho2, "r-_",label =  project2)
    pl.xlabel('R (meters)')
    pl.ylabel(r'$\rho_{uv}$')
    pl.axis([0., xmax[i], 0.01,50.])
    pl.yscale("log")
    pl.legend(loc = "upper right")
    
    
pl.savefig("%s/AFC-rho.png"%(productDir))
pl.show()
raw_input()
