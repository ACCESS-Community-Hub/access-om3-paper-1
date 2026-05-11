import nci_ipynb  # requires conda/analysis3-26.03 or later
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os

dpi = 100
rcParams["figure.dpi"]= dpi

class MkmdWriter:
    """Class to keep track of exporting key Figures or Tables to a markdown file

    experiment: path to esm file, we just take the last folder to mean the experiment name
    nbname: name of notebook that this is being called from
    cwd: current working directory (will use this as the basis for plot folder)
    pm (default: False): being called by papermill?
    """
    def __init__(self, esm_file, nbname, cwd, pm=False):
        self.fignum = 1
        self.experiment = os.path.basename(os.path.dirname(esm_file))
        self.nbname = nbname
        self.cwd    = cwd
        self.papermill = pm
        self.mdfol = self.cwd+"mkmd/"

    def savefig(self, title, caption, dpi=dpi):
        """Save figure and append to markdown summary.

        title: title of figure
        caption: caption of figure
        dpi (default: 100): dpi for figure
        """
        if self.papermill:
            plot_fname = self.nbname[:-6]+"_"+str(self.fignum).zfill(2)+".png"
            
            os.makedirs(self.mdfol, exist_ok=True)
            plt.savefig(self.mdfol+plot_fname, dpi=dpi, bbox_inches="tight")
            print("Saved", self.mdfol+plot_fname)
            
            mkmd(title,
                 f"`{self.nbname}`: {caption}",
                 self.experiment,
                 plot_fname,
                 self.mdfol,
                 table='')
        self.fignum += 1

    def table(self, title, table):
        """Append table to markdown summary.
        title: title of table
        table: markdown table string (expected format is a list with strings where each new item is a new line)
        """
        if self.papermill:
            mkmd(title,
                 f"`{self.nbname}`: This is a table caption",
                 self.experiment,
                 "",
                 self.mdfol,
                 table)


def mkmd(title,caption,experiment,plot_fname,mdfol,table=''):
    """Function to create a markdown file and add a figure or a table

    title: title for figure or table 
    caption: caption for figure (not used when making a table)
    experiment: experiment name
    plot_fname: name of plot
    mdfol: directory to output markdown file and figures
    table (default: ''): if this is \neq '' then a table will be added rather than a figure
    """
    # Create the folder
    try:
        # exist_ok=True prevents an error if the directory already exists
        os.makedirs(mdfol, exist_ok=True)
    except OSError as e:
        print(f"An error occurred: {e}")
    
    mdpath=mdfol+experiment+'.md'
    print('Adding a figure to markdown doc: '+mdpath)

    if table!='':
        fig_or_table=table

        lines_to_append = [
            "<!-- push this file to documentation/docs/pages/experiments/"+experiment+" and the images to documentation/docs/assets/"+experiment+" -->"+"\n",
            "# "+experiment+"\n",
            " \n",
            "This page shows evaluation figures from ACCESS-OM3 experiment "+ experiment+ " for discussion and see plotting scripts have a look at [this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
             " \n",
            getauthors(),
            " \n",
            "## "+title+"\n",
            " \n",
        ]
        for tableline in fig_or_table:
            lines_to_append.append(tableline+"\n")
        #lines_to_append.append(" \n")
    else:
        fig_or_table='!['+caption+'](/assets/experiments/'+experiment+'/'+plot_fname+') \n'

        lines_to_append = [
            "<!-- push this file to documentation/docs/pages/experiments/"+experiment+" and the images to documentation/docs/assets/"+experiment+" -->"+"\n",
            "# "+experiment+"\n",
            " \n",
            "This page shows evaluation figures from ACCESS-OM3 experiment "+ experiment+ " for discussion and see plotting scripts have a look at [this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
             " \n",
            getauthors(),
            " \n",
            "## "+title+"\n",
            " \n",
            fig_or_table,
            " \n",
            "  Caption: "+caption+"\n",
            "  \n"
        ]

    #check if file exists
    if os.path.exists(mdpath) and string_exists_in_file(mdpath, title):
        #The case when we just want to add for the same notebook. 
        print("This notebook has already added to the figure file, so this will add an additional figure.")
        lines_to_append=lines_to_append[8:]
        print(lines_to_append)
    elif os.path.exists(mdpath):        
        lines_to_append=lines_to_append[7:]
        print(lines_to_append)
            
    try:
        with open(mdpath, 'a') as file:
            file.writelines(lines_to_append)
        print(f"Lines appended to {mdpath} successfully.")
    except:
        pass
        
    return

def string_exists_in_file(filename, search_string):
    """Checks if a string exists in a file (case-sensitive)."""
    try:
        with open(filename, 'r') as myfile:
            if search_string in myfile.read():
                return True
            else:
                return False
    except FileNotFoundError:
        print(f"Warning: First time this notebook has been included: '{filename}'.")
        return False

def getauthors(file_path='../CITATION.cff'):
    """Function to find authors from citation file and put them in the markdown file"""
    #in case one wants a downloaded one
    #import urllib.request
    #file_path= "https://raw.githubusercontent.com/ACCESS-Community-Hub/access-om3-paper-1/main/CITATION.cff"
    # Download the file
    #with urllib.request.urlopen(file_path) as response:
        #lines = response.read().decode("utf-8").splitlines()

    try:
        # Open the file in read mode ('r' is the default) with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()  # Read the entire file content into a string
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    given = None
    family = None
    
    coauthors=[]
    for line in lines:
        line = line.strip()
    
        if "given-names:" in line:
            given = line.split(":", 1)[1].strip().strip('"').rstrip()
            #print(given)
        elif line.startswith("family-names:"):
            family = line.split(":", 1)[1].strip().strip('"').rstrip()
            #print(family)
    
        # Once we have both, print and reset
        if given and family:
            #print(f"Given names: {given}, Family names: {family}")
            #print(family+", "+given+".")
            coauthors.append(family+", "+given+".")
    
            given = None
            family = None
    return 'Co-authors (alphabetically) for the notebooks that created these figures: '+', '.join(sorted(coauthors))
