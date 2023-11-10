from PIL import Image
import numpy as np
from utils import Debug
def GeomOVFtopng(filename):
    '''Converts a Geometry ovf file to an image with the right colors matching'''
    Debug.Log("Opening "+filename)
    with open(filename,'r') as file:
        lines = file.readlines()
        #Find the resolution
        res = 0
        i =0
        domains0=''
        domains1=''
        while res<=0:
            line = lines[i]
            if "# xnodes" in line:
                #found resolution
                
                res = int(line[10:-1])
                Debug.Log("Found resolution " + str(res))
            i+=1
        img=np.empty((res,res,4),dtype='uint8')
        j=0
        for i,line in enumerate(lines):
            if(line[0]!='#'):
                #data line
                if(domains0 == ''): 
                    domains0 = int(line[0]) 
                elif(domains1=='' and int(line[0])!=domains0):
                    domains1 = int(line[0])
                if(int(line[0])==domains0):
                    img[j//res,j%res] = [0,0,0,255]
                if(int(line[0])==domains1):
                    img[j//res,j%res] = [255,255,255,255]
                j+=1
    Debug.Log("Printing image "+filename[:-4]+".png")
    im2 = Image.fromarray(img)
    im2.save(filename[:-4]+".png")

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    GeomOVFtopng(file)