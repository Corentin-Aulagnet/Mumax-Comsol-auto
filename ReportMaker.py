from GoogleGmailAPIConnect import connectToGoogleAPI,readEmails
import time
from utils import Debug
import os
from datetime import datetime
import sys
import dominate
from dominate.tags import *

class Simulation:
    def __init__(self,name,path,status='Created',slurmId='0'):
        self.name = name
        self.path = path
        self.status = status
        self.slurmId = slurmId
    def __equal__(a):
        return self.name == a.name

class Reporter:
    def __init__(self,global_simulation_path,timeout,interval,updateHTML = False):
        self.trackedSimulations = []
        self.checkerTimeout = timeout #s
        self.checkerInterval = interval #s
        self.global_simulation_path = global_simulation_path
        
        self.reportPageHTML = global_simulation_path+'/html/report_main.html'
        self.reportPageCSS = global_simulation_path+'/html/main_style.css'
        self.updateHTML = updateHTML
        if(self.updateHTML):
            self.startHTML()

    def startHTML(self):
        try:
            os.mkdir(global_simulation_path+'/html')
        except FileExistsError:
            pass
        f=open(self.reportPageHTML,'w')
        f.close()
        f=open(self.reportPageCSS,'w')
        f.close()

    def addTracker(self,simulation:Simulation):
        self.trackedSimulations.append(simulation)
    
    def updateTrackerStatus(self,simulationName,newStatus):
        for sim in self.trackedSimulations:
            if sim.name == simulationName:
                sim.status

    def processEmails(self,global_simulation_path,interval = 600,timeout = 10800):#timeout is 3h by default, interval is 10min by default
        startTime = time.time()
        lastCheckTime = time.time()
        creds = connectToGoogleAPI()
        shortcut = False
        Debug.Log("Starting email reading thread",'blue')
        nSimsFinished = 0
        while (time.time() - startTime) < timeout:
            #continue reading emails
            if (time.time() - lastCheckTime) >= interval or shortcut:
                shortcut = False
                Debug.Log("Checking emails",'blue')
                #interval is over, check emails
                lastCheckTime = time.time()
                runFinished = readEmails(creds)
                if runFinished != None:
                    for run in runFinished:
                        nSimsFinished += 1
                        if run['status'] == "COMPLETED":
                            #run ended correctly, grab data
                            simulation_path = "{}/{}".format(global_simulation_path,run['jobName'])
                            Debug.Log("Run {} completed in {}, getting data back from remote".format(run['jobName'],run['runTime']),'green')
                            try:
                                os.mkdir("{}/results".format(simulation_path) )
                            except FileExistsError:
                                Debug.LogWarning("{} already has a result folder")
                            os.system("scp -P 5097 anx13@193.54.9.82:Mumax_simulations/{0}/output_{1}/{1}.out/table.txt {0}/results/table.txt".format(simulation_path,run['jobName']))
                    
                            os.system("python ../_scripts/plot_main.py mhLoop -d {1} -f {0}/results/table.txt -o graphs/{2}.png".format(simulation_path,run['jobName'][-1],run['jobName']))#Careful with it
                        else:
                            #something wrong happened
                            Debug.LogError("Something wrong happened with run {} runtime was {}".format(run['jobName'],run['runTime']))
                            Debug.LogError("Exit code : {}, status {}".format(run['exitCode'],run['status']))                 
                else:
                    Debug.Log("Nothing to download",'blue')
        Debug.Log("Done checking emails",'blue')
        self.writeHTML()

    def writeHTML(self):
        with open(self.reportPageCSS,'w') as f:
            f.write("""   
             table.tableSection {
                display: table;
                width: 100%;
                
            }
            table.tableSection th, table.tableSection td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            table.tableSection thead, table.tableSection tbody {
                float: left;
                width: 100%;
                text-align : left;
                border-right: 1px solid black;
            }
            table.tableSection tbody {
                overflow: auto;
                height: 150px;
            }
            table.tableSection tr {
                overflow: auto;
                width: 100%;
                display: table;
                text-align: left;
            }
            table.tableSection tr,table.tableSection th {
                width: 300px;
            }
    """)
        doc = dominate.document(title='Dominate your HTML')

        with doc.head:
            link(rel='stylesheet', href='main_style.css')
            #script(type='text/javascript', src='script.js')

        with doc:
            with div(id='header').add(ol()):
                for i in ['home', 'about', 'contact']:
                    li(a(i.title(), href='/%s.html' % i))

            with div():
                attr(cls='body')
                p('Lorem ipsum..')
                with table():
                    attr(cls="tableSection")
                    with thead():
                        with tr():
                            th("Name")
                            th("Path")
                            th("Status")
                            th("Slurm Id")
                    with tbody():
                        for index,sim in enumerate(self.trackedSimulations):
                            r = tr()
                            r.add(td(sim.name))
                            r.add(td(a(sim.path,sim.path)))
                            r.add(td(sim.status))
                            r.add(td(sim.slurmId))

        with open(self.reportPageHTML,'w') as f:
            f.write(doc.render())

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



if __name__ == "__main__":
    date = datetime.today().strftime('%Y-%m-%d')
    try:
        date = sys.argv[3]
    except : 
        pass
    reporter = Reporter('.',interval=float(sys.argv[1]),timeout=float(sys.argv[2]))
    reporter.processEmails(date,interval=float(sys.argv[1]),timeout=float(sys.argv[2]))