## run to validate the MI entropy-based metric for the quality of an array
##
## We use the configuration C43-4 as the test case
## NOTE: the elongated beam is probably not checked..
##
## Date: 24/6/2018
## 
################################################################
import sys
sys.path.append('../arrayconfiguation')

import shutil, os
import arrayConfigurationSim as aC
import math
import UVW
import matplotlib.pyplot as pl
import numpy.random as rd


rd.seed()

simDir =  "/home/stephane/alma/ArrayConfig/imaging/fullcombination/entropy" 
dataDir = "/home/stephane/alma/ArrayConfig/imaging/fullcombination/master/notebooks/data" 
productDir = "/home/stephane/alma/ArrayConfig/imaging/fullcombination/entropy/products" 

nsource = 20
ntrial  = 1000
antmin  = 4      ## random array
antmax  = 45     ## random array

#### create cl #####################################################################

def createSource():
    "Create a CL with nsource located randomly"
    
    clfile = simDir+"/source.cl"
    
    if os.path.exists(clfile):
        shutil.rmtree(clfile, ignore_errors=True)


    al  = rd.uniform(-90.,90., nsource)
    de =  rd.uniform(-60.,60.,nsource)
    fluxsource = rd.uniform(5e-3,100e-3,nsource)
    diskSize = rd.uniform(0.1,50.0,nsource)   
    
    for i in range(nsource):
        
        alpha =  10. + al[i]/3600.
        delta = -50. + de[i]/3600.
        decString="J2000 %6.4fdeg %6.4fdeg"%(alpha,delta)
        minmaj = "%3.1farcsec"%(diskSize[i])

        
        cl.addcomponent(dir = decString, flux = fluxsource[i], fluxunit = 'Jy', freq = "100GHz" ,shape = "Gaussian", majoraxis= minmaj, minoraxis = minmaj, positionangle = "0deg")
        
    cl.rename(clfile)
    cl.done()
    
    
def simulation(antcfg, projectname, totime ,ovrwrt= True):
    
    simalma(
        overwrite      = ovrwrt, 
        dryrun         = False,
        project        = projectname,
        complist       = "source.cl" ,
        compwidth      = '200MHz' , 
        antennalist    =  antcfg ,
        totaltime      = totime,
        pwv            = 5.0,
        mapsize        =  "150arcsec",
        niter          =   2000,
        threshold      = '0.01mJy', 
        cell           = "0.2arcsec",
        imsize         = 750)
    
    
def readPads(filepads = "Pads.cfg"):
    " Read the lines for each pads" 
    
    pads = []
    with open(dataDir+"/"+filepads) as f:
        for line in f:
            pads.append(line)
    f.close()
            
    return(pads)
        
            
def randomArrayConfiguration(listPads, nants = 43):
    "create a random array configuration using listPads and the fixed pads from the list"
    
    newArr = "# observatory=ALMA\n# coordsys=LOC (local tangent plane)\n# x y z diam pad#" 
    
    arr = np.arange(len(listPads))
    rd.shuffle(arr)
    
    for i in range(nants):
        newArr += "%s"%(listPads[arr[i]])
        
    return(newArr[0:-1])

def save_nantran(fitsimage, nant):
    " save the nant with the fitsimage in nantran.txt"
    
    filenant = "%s/nantran.txt"%(productDir)
    
    with open(filenant,"a") as f:
        f.write("%s %d\n"%(fitsimage, nant))
        f.close()
        
                
    
#####################################################################################
##### Main #########################################################################

if not os.path.exists(simDir):
    os.makedirs(simDir)
    
if not os.path.exists(productDir):
    os.makedirs(productDir)
   
filenant = "%s/nantran.txt"%(productDir)
if os.path.exists(filenant):
    os.remove(filenant)
    
cwd = os.getcwd()
os.chdir(simDir)


pads = readPads()

## For a random C32-3 we select 32 antennas in the 100 first pads
pads_3 = pads[3:93]
arrStd = "alma.cycle5.3"
inttime = "300s"
  
for i in range(ntrial):
   
    print("### Test: %d"%(i))
    createSource()
    
    #####
    project = "arrTarget"
    antcfg = "%s/%s.cfg"%(dataDir,arrStd)
  
    
    simulation(antcfg, project, inttime, True)
        
    imagename = "%s/%s/%s.%s.noisy.image"%(simDir,project,project,arrStd)
    fitsimage = "%s/%s.image.fits.%d"%(productDir,arrStd,i)
    exportfits(imagename,fitsimage,overwrite = True)
    
    imagename = "%s/%s/%s.%s.compskymodel.flat.regrid.conv"%(simDir,project,project, arrStd)
    fitsimage = "%s/%s.compskymodel.flat.regrid.conv.fits.%d"%(productDir,arrStd,i)
    exportfits(imagename,fitsimage,overwrite = True)
    

    #####
    project = "simRan"
    nantran = rd.randint(antmin,antmax)
    arrRan  = randomArrayConfiguration(pads_3, nants = nantran)
    
    antcfg = "alma.%s%d.cfg"%(project,i)   
    with open(antcfg,"w") as f:
        f.write(arrRan)   
    f.close()  
     
    
    simulation(antcfg, project, inttime, True)
        
    imagename = "%s/%s/%s.alma.%d.noisy.image"%(simDir,project,project,i)
    fitsimage = "%s/%s.image.fits.%d"%(productDir,project,i)
    fitsname = "%s.image.fits.%d"%(project,i)
    exportfits(imagename,fitsimage,overwrite = True)
    save_nantran(fitsname, nantran)
    
    
    imagename = "%s/%s/%s.alma.%s%d.compskymodel.flat.regrid.conv"%(simDir,project,project,project,i)
    fitsimage = "%s/%s.compskymodel.flat.regrid.conv.fits.%d"%(productDir,project,i)
    fitsname =  "%s.compskymodel.flat.regrid.conv.fits.%d"%(project,i) 
    res = exportfits(imagename,fitsimage,overwrite = True)
    save_nantran(fitsname, nantran)

        
 
 
