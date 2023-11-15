from string import Template
from ComsolToovf import CRLFToLF
from utils import Debug

def findKeysInTemplate(template):
    lines = template.readlines()
    keys=[]
    for line in lines:
        if '$' in line:
            #Found a key, read it
            beginKey = line.index("{")
            endKey = line.index("}")
            keys.append(line[beginKey+1:endKey])
    return keys

                

def generateMumaxScript(data,pathToSimulationFolder):
    #Generates a mumax script using the yaml config data

    filename = data["Simulation_Name"]+".mx3"
    mumax_script_template = data["Mumax_template"]
    keys = data["mumax_params"]
    if keys == None :
        keys = {}
    
    with open(mumax_script_template,'r') as mumax_template:
        key_names = findKeysInTemplate(mumax_template)
    with open(mumax_script_template,'r') as mumax_template:
        scripttmpl = Template(mumax_template.read())
        #Build the dict
        for key in key_names:
            if key =="geom_file":
                geom_filename="geom_"+str(data["cell_number"])+".png"
                keys["geom_file"] = geom_filename
            elif key =="oersted_file":
                Oersted_filename = "Oersted_"+str(data["cell_number"])+"_"+data["input_current"].replace('[','').replace(']','')+".ovf"
                keys["oersted_file"] = Oersted_filename
            elif key =="J_file":
                J_filename = "J_"+str(data["cell_number"])+"_"+data["input_current"].replace('[','').replace(']','')+".ovf"
                keys["J_file"] = J_filename
            elif key =="cell_size":
                keys["cell_size"] = 2*4.980e-7/data["cell_number"]
            else:
                if key not in keys:
                    keys[key] = data[key]

        with open(pathToSimulationFolder+"/"+filename,'w') as mumax_script:
            script = scripttmpl.substitute(keys)
            mumax_script.write(script)
    with open("RunMUMAX3_template.slurm",'r') as slurmTemplate:
        scripttmpl = slurmTemplate.read()
        script = scripttmpl.replace("$MUMAX_SCRIPT",filename)
        script = script.replace("$JOB_NAME",filename[:-4])
        with open(pathToSimulationFolder+"/"+"RunMUMAX3.slurm",'w') as slurmFile:
            slurmFile.write(script)
    CRLFToLF(pathToSimulationFolder+"/"+"RunMUMAX3.slurm")
        
if __name__ == "__main__":
    import sys
    
    yamlFile = sys.argv[1]
    GenerateMumaxScript(yamlFile)

