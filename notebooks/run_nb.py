#inspired by
#https://stackoverflow.com/questions/37534440/passing-command-line-arguments-to-argv-in-jupyter-ipython-notebook
import sys,os
import json
CONFIG_FILENAME = 'config_ipynb_tmp'

def main(argv):
    try:
        os.remove(CONFIG_FILENAME)
    except OSError:
        pass

    with open(CONFIG_FILENAME,'w') as f:
        f.write(' '.join(argv))

    #import pdb;pdb.set_trace()
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

    newf=argv[1][:-6]+'_new.ipynb'
    with open(newf, "w") as jsonFile:
        json.dump(d, jsonFile)

    os.system('jupyter nbconvert --execute {:s} --to html'.format(newf))
    os.remove(newf)
    os.rename(newf[:-6]+'.html',newf[:-10]+'.html')
    print('File created: '+newf[:-10]+'.html')

    return None

if __name__ == '__main__':
    main(sys.argv)
