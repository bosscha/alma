sys.path.append('../arrayconfiguation')
import shutil, os
import arrayConfigurationSim as aC
import math
import UVW
import matplotlib.pyplot as pl

simDir = "/home/stephane/Science/alma/ArrayConfiguration/simulations"
dataDir = "/home/stephane/Science/alma/ArrayConfiguration/master/notebooks/data"
productDir = "/home/stephane/Science/alma/ArrayConfiguration/master/notebooks/products"

def simulation(antcfg, projectname, totime ,ovrwrt= True):
    
    simalma(
        overwrite      = ovrwrt, 
        dryrun         = False,
        project        = projectname,
        skymodel       =  "%s/M51ha.fits"%(dataDir),
        inbright       = "0.01Jy/pixel",
        # indirection    =  "J2000 10h00m00 -50d00m00",
        indirection    =  "J2000 10h00m00 -30d00m00",
        incenter       =  "100.0GHz",
        inwidth        =  "200MHz",
        incell         =  "0.2arcsec",
        antennalist    =  antcfg ,
        totaltime      = totime,
        pwv            = 10.0,
        mapsize        =  "150arcsec",
        niter          =   1500,
        cell           = "0.2arcsec",
        imsize         = 750)

#########################################################
# wd = "/home/stephane/Science/ALMA/ArrayConfig/imaging/fullcombination/results/"

if not os.path.exists(simDir):
    os.makedirs(simDir)
    
if not os.path.exists(productDir):
    os.makedirs(productDir)
    
cwd = os.getcwd()
print cwd
os.chdir(simDir)

for i in range(1,7):
    project = "AFC-%d"%(i)
    antcfg = "%s/alma.afc-%d.cfg"%(dataDir,i)
    inttime = "1h"
    print project
    print antcfg
    simulation(antcfg, project, inttime, True)
    
    project = "C43-%d+ACA"%(i)    
    antcfg = ["%s/alma.cycle5.%d.cfg"%(dataDir,i),"%s/aca.cycle5.cfg"%(dataDir)]
    print antcfg
    inttime = ["1h","5h"]
    simulation(antcfg, project, inttime, True)

os.chdir(cwd)

######### export image to fits ....

for i in range(1,7):
    project = "AFC-%d"%(i)
    imagename = "%s/%s/AFC-%d.alma.afc-%d.noisy.diff"%(simDir,project,i,i)
    fitsimage = "%s/AFC-%d.alma.afc-%d.diff.fits"%(productDir,i,i)
    exportfits(imagename,fitsimage,overwrite = True)
    imagename = "%s/%s/AFC-%d.alma.afc-%d.noisy.fidelity"%(simDir,project,i,i)
    fitsimage = "%s/AFC-%d.alma.afc-%d.fidelity.fits"%(productDir,i,i)
    exportfits(imagename,fitsimage,overwrite = True)
    imagename = "%s/%s/AFC-%d.alma.afc-%d.noisy.image"%(simDir,project,i,i)
    fitsimage = "%s/AFC-%d.alma.afc-%d.image.fits"%(productDir,i,i)
    exportfits(imagename,fitsimage,overwrite = True)
    imagename = "%s/%s/AFC-%d.alma.afc-%d.skymodel.flat.regrid.conv"%(simDir,project,i,i)
    fitsimage = "%s/AFC-%d.alma.afc-%d.skymodel.flat.regrid.conv.fits"%(productDir,i,i)
    exportfits(imagename,fitsimage,overwrite = True)


    project = "C43-%d+ACA"%(i)
    imagename = "%s/%s/C43-%d+ACA.concat.diff"%(simDir,project,i)
    fitsimage = "%s/C43-%d+ACA.concat.diff.fits"%(productDir,i)
    exportfits(imagename,fitsimage,overwrite = True)  
    imagename = "%s/%s/C43-%d+ACA.concat.fidelity"%(simDir,project,i)
    fitsimage = "%s/C43-%d+ACA.concat.fidelity.fits"%(productDir,i)
    exportfits(imagename,fitsimage,overwrite = True)
    imagename = "%s/%s/C43-%d+ACA.concat.image"%(simDir,project,i)
    fitsimage = "%s/C43-%d+ACA.concat.image.fits"%(productDir,i)
    exportfits(imagename,fitsimage,overwrite = True)
    
    # we compute the original convolved image here
    im0 = "%s/%s/C43-%d+ACA.concat.image"%(simDir,project,i)
    im1 = "%s/%s/C43-%d+ACA.concat.diff"%(simDir,project,i)
    immath(imagename=[im0,im1], expr='IM0+IM1', outfile= "%s/%s/C43-%d+ACA.concat.skymodel.flat.regrid.conv"%(simDir,project,i))
    
    imagename= "%s/%s/C43-%d+ACA.concat.skymodel.flat.regrid.conv"%(simDir,project,i)
    fitsimage = "%s/C43-%d+ACA.concat.skymodel.flat.regrid.conv.fits"%(productDir,i)
    exportfits(imagename,fitsimage,overwrite = True)


######### compute the beam properties.....

for i in range(1,7):
    
    ac = aC.arrayConfigurationSim(readParam = False)
    
    project = "AFC-%d"%(i)
    imagename = "%s/%s/AFC-%d.alma.afc-%d.noisy.image"%(simDir,project,i,i)
    beamname  = "%s/%s/AFC-%d.alma.afc-%d.noisy.psf"%(simDir,project,i,i)
    
    ia.open(imagename)
    beam = ia.restoringbeam()
    ia.close()
    radiusBeam , beamLevel = ac.beamLevels(beamname)  
    sidelobe = 100.*ac.findMaxLevelSideLobe(radiusBeam, beamLevel, beam['major']['value'])
 
    f = file("%s/%s-beam.txt"%(productDir,project),"w")
    f.write("## Project: %s \n"%(project))
    f.write("## \n")
    f.write("## Sidelobe  : %f \n"%(sidelobe))
    f.write("## Major axis: %f \n"%(beam['major']['value']))
    f.write("## Minor axis: %f \n"%(beam['minor']['value']))
    f.write("## AR: %f \n"%(math.sqrt(beam['minor']['value']*beam['major']['value'])))
    f.write("-------------\n")
    f.close()
    
    project = "C43-%d+ACA"%(i)   
    imagename = "%s/%s/C43-%d+ACA.concat.image"%(simDir,project,i)
    beamname  = "%s/%s/C43-%d+ACA.concat.psf"%(simDir,project,i)
    
    ia.open(imagename)
    beam = ia.restoringbeam()
    ia.close()
    radiusBeam , beamLevel = ac.beamLevels(beamname)  
    sidelobe = 100.*ac.findMaxLevelSideLobe(radiusBeam, beamLevel, beam['major']['value'])
    
    f = file("%s/%s-beam.txt"%(productDir,project),"w")
    f.write("## Project: %s \n"%(project))
    f.write("## \n")
    f.write("## Sidelobe  : %f \n"%(sidelobe))
    f.write("## Major axis: %f \n"%(beam['major']['value']))
    f.write("## Minor axis: %f \n"%(beam['minor']['value']))
    f.write("## AR: %f \n"%(math.sqrt(beam['minor']['value']*beam['major']['value'])))
    f.write("-------------\n")

############################ Creating the UV radial distribution
NBIN = 50
MINr = 0.
MAXarr= [200,330,550,800,1500,2500]    # maximum baseline for the plot

for iarr in range(1,7):
    MAXr = MAXarr[iarr-1]
    
    project1 = "AFC-%d"%(iarr)
    msname = "%s/%s/AFC-%d.alma.afc-%d.noisy.ms"%(simDir,project1,iarr,iarr)
    uv = UVW.UVW(msname)
    
    radius , rho1 = uv.radialDensity(MINr, MAXr, NBIN)
    k1 = rho1.sum()
    dr = (MAXr - MINr) / NBIN
    IRho1 = 0.
    
    for i in range(0,len(radius)):
        IRho1 += rho1[i] * 2.* pi * radius[i] * dr
    rho1 = rho1 * k1 / IRho1
    
    
    project2 = "C43-%d+ACA"%(iarr)
    msname  = "%s/%s/C43-%d+ACA.concat.ms"%(simDir,project2,iarr)
    uv = UVW.UVW(msname)
    
    radius , rho2 = uv.radialDensity(MINr, MAXr, NBIN)
    k2 = rho2.sum()
    dr = (MAXr - MINr) / NBIN
    IRho2 = 0.
    
    for i in range(0,len(radius)):
        IRho2 += rho2[i] * 2.* pi * radius[i] * dr
    rho2 = rho2 * k2 / IRho2
    
    fig = pl.figure() 
    ax = fig.add_subplot('111')
    ax.semilogy(radius,rho1,'b-',drawstyle='steps',label=project1)
    ax.semilogy(radius,rho2,'r-',drawstyle='steps',label=project2)
    ax.legend(loc = "upper right")
    ax.set_xlabel(r"$R_{UV}$ (meter)")
    ax.set_ylabel(r"$\rho_{UV}$")
        
    fig.savefig('%s/%s.radialUVdensityLog.png'%(productDir,project1))
    pl.close(fig)
    
