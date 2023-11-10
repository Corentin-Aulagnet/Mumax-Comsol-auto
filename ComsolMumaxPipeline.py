from utils import Debug
import sys
import os
from GenerateMumaxScript import generateMumaxScript
from ComputeComsol import computeComsol
from yaml import Loader, load_all,dump
from datetime import datetime
from termcolor import colored
from ReportMaker import Reporter
from multiprocessing import Process
def StartPipeline(config_file,interval,timeout,test=False):
    #Read the yaml config file
    yml_stream =  open(config_file, 'r')
    Debug.Log("Reading the yaml config file")
    yml = load_all(Loader=Loader, stream = yml_stream)
    number_of_documents = len(list(yml))
    yml_stream.close()
    Debug.Log("Found {} simulations to run".format(number_of_documents),'green')
    yml_stream =  open(config_file, 'r')
    yml = load_all(Loader=Loader, stream = yml_stream)
    #Generate the folders
    global_simulation_path =  datetime.today().strftime('%Y-%m-%d')
    if test : global_simulation_path = "tests"
    try:
        os.mkdir(global_simulation_path)
    except FileExistsError:
        Debug.LogWarning("The folder {} already exists. More simulation today huh?".format(global_simulation_path))
    #Starting email reader
    reporter = Reporter(global_simulation_path,timeout,interval)
    p = Process(target=reporter.processEmails, args=(global_simulation_path,interval,timeout,))
    p.start()
    #For every simulation
    index=1
    for data in yml:
        simulation_name = data["Simulation_Name"]
        override_flag = data["override"]
        cell_number = data["cell_number"]
        input_current = data["input_current"]
        Debug.Log("Starting simulation for {}, {}/{}".format(simulation_name,index,number_of_documents),'green')
        simulation_path = "{}/{}".format(global_simulation_path,simulation_name)
        try:
            os.mkdir(simulation_path)
        except FileExistsError:
            if override_flag:
                Debug.LogWarning("The folder {} already exists but the override flag is True".format(simulation_path,config_file))
                Debug.Log("Proceeding...",'green')
            else:
                Debug.LogError("The folder {} already exists. Exiting to avoid overriding simulation. Please check the simulation name in the {} config file".format(simulation_path,config_file))
                continue
        file = open("{}/simulation_parameters.yml".format(simulation_path),'w')
        dump(data, file)
        file.close()
        comsol_results = computeComsol("{}/simulation_parameters.yml".format(simulation_path),simulation_path)
        #Generate the mumax files
        Debug.Log("Generating mumax and slurm scripts")
        generateMumaxScript(data,simulation_path,comsol_results)
        Debug.Log("Finished generating mumax and slurm scripts")
        Debug.Log("Sending files over scp")
        #Send the files over scp
        geom_filename="geom_"+str(cell_number)+".png"
        Oersted_filename = "Oersted_"+str(cell_number)+"_"+input_current.replace('[','').replace(']','')+".ovf"
        J_filename = "J_"+str(cell_number)+"_"+input_current.replace('[','').replace(']','')+".ovf"
        #os.system("cat .\\test_over_ssh.sh | ssh -p 5097 anx13@193.54.9.82 'bash -s'") to transmit command in a script
        #os.system("ssh -p 5097 anx13@193.54.9.82 some command") to transmit command direclty written
        os.system("ssh -p 5097 anx13@193.54.9.82 mkdir Mumax_simulations/{}".format(global_simulation_path))
        os.system("ssh -p 5097 anx13@193.54.9.82 mkdir Mumax_simulations/{}".format(simulation_path))
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path+'/'+comsol_results,Oersted_filename,simulation_path) )
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path+'/'+comsol_results,geom_filename,simulation_path) )
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path+'/'+comsol_results,J_filename,simulation_path) )
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path,"simulation_parameters.yml",simulation_path) )
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path,simulation_name+".mx3",simulation_path) )
        os.system("scp -P 5097 {}/{} anx13@193.54.9.82:Mumax_simulations/{}".format(simulation_path,"RunMUMAX3.slurm",simulation_path) )
        Debug.Log("Finished sending files")
        Debug.Log("Zipping Comsol files")
        os.system("zip -qmj9 {0}/{1}.zip {0}/*".format(simulation_path+'/'+comsol_results,simulation_name))
        #run mumax3
        Debug.Log("Running Mumax simulation")
        os.system("ssh -p 5097 anx13@193.54.9.82 cd Mumax_simulations/{};sbatch RunMUMAX3.slurm".format(simulation_path))
        print("\n")
    p.join()

if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='Allows the user to plot a 3D graph, a 4th dimensin can be added, it will be represented as a color gradient')

    # Define command line arguments
    parser.add_argument('input_file', type=str, help='Input file path')
    parser.add_argument('-t','--checkTimeout',default=10800,type = int,help='Timeout of the email checking thread in seconds')
    parser.add_argument('-f','--checkFrequency',default=600,type = int,help='Frequency of the email checking thread in seconds')
    # Parse command line arguments
    args = parser.parse_args()

    # Assign argument values to variables
    config_file = args.input_file
    interval = args.checkFrequency
    timeout = args.checkTimeout

    StartPipeline(config_file,interval,timeout)

    