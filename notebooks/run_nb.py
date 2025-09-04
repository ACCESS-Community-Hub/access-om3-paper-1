import sys,os
import json
import glob

def main(argv):
    #cb: 29/8/2025
    #https://access-nri.zulipchat.com/#narrow/channel/470323-med-team/topic/No.20such.20kernel.20named.20conda-env-analysis3-25.2E07-py.3F/with/536711167
    #yeah so the problem was when one opens a notebook in ARE it assigns a kernal that can't used on the command line, thanks Charles Turner!!
    #https://stackoverflow.com/questions/64589345/how-to-change-the-kernel-of-a-jupyter-notebook-from-the-command-line
    #https://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python
    with open(argv[1] , 'r') as f:
        d=json.load(f)

    #print(d['metadata']['kernelspec'])
    d['metadata']['kernelspec']['display_name']="Python 3 (ipykernel)"
    d['metadata']['kernelspec']['name']='python3'
    #print(d['metadata']['kernelspec'])

    newf=argv[1][:-6]+'_tmp.ipynb'
    with open(newf, "w") as jsonFile:
        json.dump(d, jsonFile)
    #import pdb;pdb.set_trace()

    os.rename(newf,argv[1])
    
    return None

if __name__ == '__main__':
    main(sys.argv)
