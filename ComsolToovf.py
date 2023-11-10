
from PIL import Image
import numpy as np
import os
from utils import Debug
def toOvf(filename,Nnodes,remove=True):
    #Convert a txt file exported from Comsol to an readable ovf

    #Read file
    J_dens=False
    geom = False
    with open(filename,'r') as file:
        content = file.read()
        if("dom" in content):
            #this is a geometry file
            J_dens=False
            geom = True
        if("mf.normJ" in content):
            #this is a geometry file
            J_dens=True
            geom = False
    stepsize = 2*4.980e-7 / Nnodes
    outputfilename = filename[:-3]+"ovf"
    outputfile = open(outputfilename,'w')
    #Add the header
    header_3D = ["# OOMMF OVF 2.0\n",
    "# Segment count: 1\n",
    "# Begin: Segment\n",
    "# Begin: Header\n",
    "# Title: J_ext\n",
    "# meshtype: rectangular\n",
    "# meshunit: m\n",
    "# xmin: -4.980E-7\n", 
    "# ymin: -4.980E-7\n", 
    "# zmin: -4.960E-9\n", 
    "# xmax: 4.980E-7\n",
    "# ymax: 4.980E-7\n",
    "# zmax: 0\n",
    "# valuedim: 3\n",
    "# valuelabels: Jx Jy Jz\n",
    "# valueunits: A/m2 A/m2 A/m2\n", 
    "# Desc: Total simulation time:  0  s\n",
    "# xbase: 0\n",
    "# ybase: 0\n",
    "# zbase: 0\n",
    "# xnodes: {}\n".format(Nnodes),
    "# ynodes: {}\n".format(Nnodes),
    "# znodes: 1\n",
    "# xstepsize: {}\n".format(stepsize),
    "# ystepsize: {}\n".format(stepsize),
    "# zstepsize: 4.960E-9\n",
    "# End: Header\n",
    "# Begin: Data Text\n"]

    header_1D = ["# OOMMF OVF 2.0\n",
    "# Segment count: 1\n",
    "# Begin: Segment\n",
    "# Begin: Header\n",
    "# Title: J_ext\n",
    "# meshtype: rectangular\n",
    "# meshunit: m\n",
    "# xmin: -4.980E-7\n", 
    "# ymin: -4.980E-7\n", 
    "# zmin: -4.960E-9\n", 
    "# xmax: 4.980E-7\n",
    "# ymax: 4.980E-7\n",
    "# zmax: 0\n",
    "# valuedim: 1\n",
    "# valuelabels: Jx\n",
    "# valueunits: A/m2\n", 
    "# Desc: Total simulation time:  0  s\n",
    "# xbase: 0\n",
    "# ybase: 0\n",
    "# zbase: 0\n",
    "# xnodes: {}\n".format(Nnodes),
    "# ynodes: {}\n".format(Nnodes),
    "# znodes: 1\n",
    "# xstepsize: {}\n".format(stepsize),
    "# ystepsize: {}\n".format(stepsize),
    "# zstepsize: 4.960E-9\n",
    "# End: Header\n",
    "# Begin: Data Text\n"]
    header =[]
    if(geom):
        header = header_1D
    else:
        header = header_3D
    outputfile.writelines(header)

    #Write data to the .ovf file
    with open(filename,'r') as file:
        lines=file.readlines()
        for line in lines:
            if line[0] == "%":
                #Line is part of the Comsol header
                #Remove it
                line=''
            else:
                #Line is part of the data section
                #Write it without the first two columns
                #Split the line along " "
                line = line.split(" ")
                while "" in line: line.remove("")
                #Remove the first two columns and join in 1 string
                line = line[2:]
                if(J_dens):
                    #File contains J_dens -> need to add 2 zeros columns
                    line.insert(0,"0 0")
                line = " ".join(line)
            
            
            #Write the new line

            outputfile.write(line)
    #Add the footer
    outputfile.writelines(["# End: Data Text\n",
    "# End: Segment"])
    outputfile.close()
    CRLFToLF(outputfilename)
    os.remove(filename)
    return outputfilename


def CRLFToLF(file_path):
    #Convert ending lines to LF
    # replacement strings
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    # relative or absolute file path, e.g.:

    with open(file_path, 'rb') as open_file:
        content = open_file.read()

    open_file.close()

    # Windows ➡ Unix
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    # Unix ➡ Windows
    #content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)

    with open(file_path, 'wb') as open_file:
        open_file.write(content)
    
def LFToCRLF(file_path):
    #Convert ending lines to LF
    # replacement strings
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    # relative or absolute file path, e.g.:

    with open(file_path, 'rb') as open_file:
        content = open_file.read()

    open_file.close()

    # Windows ➡ Unix
    #content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    # Unix ➡ Windows
    content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)

    with open(file_path, 'wb') as open_file:
        open_file.write(content)

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    Nnodes = int(sys.argv[2])
    toOvf(filename,Nnodes,remove=False)