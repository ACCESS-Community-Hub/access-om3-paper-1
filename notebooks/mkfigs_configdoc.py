import os
#little function to create a figure file for om3 configs
#cb
def mkmd(title,caption,experiment,plot_fname,mdfol):
    #print('')
    #print(title)
    #print(caption)
    #print(experiment)
    #print(plot_fname)
    #print('')
    # Create the folder
    try:
        # exist_ok=True prevents an error if the directory already exists
        os.makedirs(mdfol, exist_ok=True)
    except OSError as e:
        print(f"An error occurred: {e}")
    
    mdpath=mdfol+experiment+'.md'
    print('Adding a figure to markdown doc: '+mdpath)

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
        '!['+caption+'](/assets/experiments/'+experiment+'/'+plot_fname+'){: style="height:450px;width:900px"} \n',
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
        
    print('')

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

def get_notebook_name(notebook_name):
    if notebook_name!='not_using_mkfigs.sh':
        notebook_name=os.path.basename(os.environ.get("JPY_SESSION_NAME"))
    print("Notebook name is:", notebook_name)
    return notebook_name

def getauthors(file_path='../CITATION.cff'):
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
    #print('Co-authors (alphabetically) for the notebooks that created these figures: '+' '.join(sorted(coauthors)))
    return 'Co-authors (alphabetically) for the notebooks that created these figures: '+' '.join(sorted(coauthors))



