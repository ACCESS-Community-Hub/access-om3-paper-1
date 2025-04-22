#inspired by
#https://stackoverflow.com/questions/37534440/passing-command-line-arguments-to-argv-in-jupyter-ipython-notebook
import sys,os
#IPYNB_FILENAME = 'test_argv.ipynb'
CONFIG_FILENAME = 'config_ipynb_tmp'

def main(argv):
    with open(CONFIG_FILENAME,'w') as f:
        f.write(' '.join(argv))
    #os.system('jupyter nbconvert --execute {:s} --to html'.format(IPYNB_FILENAME))
    os.system('jupyter nbconvert --execute {:s} --to html'.format(argv[1]))
    #os.system('jupyter nbconvert --execute {:s} '.format(IPYNB_FILENAME))
    return None

if __name__ == '__main__':
    main(sys.argv)
