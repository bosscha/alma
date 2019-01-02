### We create per configuration:
### N simulations with for each a random cl with M components (disk of random size)
### This allows to estimate the robustness of the MI metric.

#############################################################3
sys.path.append('../arrayconfiguation')
import shutil, os
import arrayConfigurationSim as aC
import math
import UVW
import matplotlib.pyplot as pl
import numpy.random as rd


simDir =  "/home/stephane/alma/ArrayConfig/imaging/fullcombination/simEntropy" 
dataDir = "/home/stephane/alma/ArrayConfig/imaging/fullcombination/master/notebooks/data" 
productDir = "/home/stephane/alma/ArrayConfig/imaging/fullcombination/simEntropy/products" 


#### create cl

nsource = 300
nsample = 10
    
rd.seed(1023)

def createSource():
    "Create a CL with nsource located randomly"
    
    clfile = simDir+"/source.cl"
    
    if os.path.exists(clfile):
        shutil.rmtree(clfile, ignore_errors=True)


    al  = rd.uniform(-90.,90., nsource)
    de =  rd.uniform(-60.,60.,nsource)
    fluxsource = rd.uniform(10e-3,50e-3,nsource)
    diskSize = rd.uniform(0.1,15.0,nsource)   
    
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
    

###################################################################################

if not os.path.exists(simDir):
    os.makedirs(simDir)
    
if not os.path.exists(productDir):
    os.makedirs(productDir)
    
cwd = os.getcwd()
print cwd
os.chdir(simDir)

for i in range(1,7):

    for j in range(nsample):
        
        createSource()
        
        project = "AFC-%d"%(i)
        antcfg = "%s/alma.afc-%d.cfg"%(dataDir,i)
        inttime = "1h"
        print project
        print antcfg
     
        
        simulation(antcfg, project, inttime, True)
        
        imagename = "%s/%s/AFC-%d.alma.afc-%d.noisy.image"%(simDir,project,i,i)
        fitsimage = "%s/AFC-%d.alma.afc-%d.image.fits.%d"%(productDir,i,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
        imagename = "%s/%s/AFC-%d.alma.afc-%d.compskymodel.flat.regrid.conv"%(simDir,project,i,i)
        fitsimage = "%s/AFC-%d.alma.afc-%d.compskymodel.flat.regrid.conv.fits.%d"%(productDir,i,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
        imagename = "%s/%s/AFC-%d.alma.afc-%d.compskymodel.flat.regrid"%(simDir,project,i,i)
        fitsimage = "%s/AFC-%d.alma.afc-%d.compskymodel.flat.regrid.fits.%d"%(productDir,i,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
        
        projectAFC = project
        
       
        project = "C43-%d+ACA"%(i)    
        antcfg = ["%s/alma.cycle5.%d.cfg"%(dataDir,i),"%s/aca.cycle5.cfg"%(dataDir)]
        print antcfg
        inttime = ["1h","5h"]
    
        simulation(antcfg, project, inttime, True)

        imagename = "%s/%s/C43-%d+ACA.concat.image"%(simDir,project,i)
        fitsimage = "%s/C43-%d+ACA.concat.image.fits.%d"%(productDir,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
    
        # we compute the original convolved image here
        im0 = "%s/%s/C43-%d+ACA.concat.image"%(simDir,project,i)
        im1 = "%s/%s/C43-%d+ACA.concat.diff"%(simDir,project,i)
        immath(imagename=[im0,im1], expr='IM0+IM1', outfile= "%s/%s/C43-%d+ACA.concat.compskymodel.flat.regrid.conv"%(simDir,project,i))
    
        imagename= "%s/%s/C43-%d+ACA.concat.compskymodel.flat.regrid.conv"%(simDir,project,i)
        fitsimage = "%s/C43-%d+ACA.concat.compskymodel.flat.regrid.conv.fits.%d"%(productDir,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
        
        imagename = "%s/%s/AFC-%d.alma.afc-%d.compskymodel.flat.regrid"%(simDir,projectAFC,i,i)
        fitsimage = "%s/C43-%d+ACA.concat.compskymodel.flat.regrid.fits.%d"%(productDir,i,j)
        exportfits(imagename,fitsimage,overwrite = True)
            
        
