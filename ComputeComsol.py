from ComsolToovf import toOvf
from GeomOVFTopng import GeomOVFtopng
import os
import csv
import shutil
from yaml import Loader, safe_load
from utils import Debug
def computeComsol(yamlFile,simulationPath):
    #Write the parameters.csv file for comsol from the yaml config file
    with open(yamlFile, 'r') as file:
        params = safe_load(file)
        current = params["input_current"]
        cell_number = params["cell_number"]
        simulation_flag = params["Simulate_Comsol"]
        simulation_name= params["Simulation_Name"]
    with open("{}/parameters.csv".format(simulationPath),'w') as csvfile:   
        csvfile.write("{0},{1}\n".format(cell_number,current))
    nNodes = cell_number
    current =current.replace("]","").replace("[","")
    outputDir=  "ComsolResults_"+str(nNodes)+"_"+current
    if (simulation_flag):
        comsolFile = params["comsol_file"]
        #copy the comsol file to the simulation folder
        newComsolFile = params["Simulation_Name"]+".mph"
        shutil.copy(comsolFile,simulationPath+"/"+newComsolFile)
        Debug.Log("Copied Comsol model to "+simulationPath+"/"+newComsolFile)
        #Call to compute Comsol
        Debug.Log("Starting Comsol with file {}".format(comsolFile))
        os.system("\"C:/Program Files/COMSOL/COMSOL55/Multiphysics/bin/win64/comsolbatch.exe\" -inputfile {0} -methodcall methodcall2 -nosave > {1}/comsol_simulation.log".format(simulationPath+"\\"+newComsolFile,simulationPath))
        Debug.Log("Finished Comsol simulation with file {}".format(comsolFile))
        #Call python scripts to generate ovf files from Comsol outputs
        Debug.Log("Converting Comsol outputs to .ovf")
        #Read the parameter csv file
        sim = []
        with open("{}/parameters.csv".format(simulationPath), newline='\r\n') as csvfile:   
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                sim=[row[0],row[1]]
        #The current file
        J_prefix =simulationPath+"/"+outputDir+"/J_"+str(nNodes)+"_"
        toOvf(J_prefix+current+".txt",nNodes)
        #The Oersted file
        Oersted_prefix = simulationPath+"/"+outputDir+"/Oersted_"+str(nNodes)+"_"
        toOvf(Oersted_prefix+current+".txt",nNodes)
        #The geom file
        geomFileName = toOvf(simulationPath+"/"+outputDir+"/geom_"+str(nNodes)+".txt",int(nNodes))
        #Convert geometry to an image
        GeomOVFtopng(geomFileName)
    else: 
        Debug.Log("Comsol-Simulation flag was off")
        Debug.Log("Unzipping files for scp")
        os.system("unzip -q {0}/{1}.zip -d {0}".format(simulation_path+'/'+outputDir,simulation_name))
        os.system("rm {0}/{1}.zip")
    return outputDir

if __name__ == "__main__":
    import argparse
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(add_help=False,description='Command-line argument example')

    # Add a string parameter
    parser.add_argument('-f','--comsolFile', type=str, dest='comsolFile',help='The comsol file name')

    # Configure help message
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help="Computes a comsol file and generate the ovf files for the spin current density, the Oersted field and the geometry")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the string parameter
    comsolFile = args.comsolFile

    computeComsol(comsolFile)


    
    

