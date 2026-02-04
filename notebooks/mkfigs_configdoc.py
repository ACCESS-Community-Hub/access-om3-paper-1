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
        "## "+title+"\n",
        " \n",
        '!['+caption+'](/assets/experiments/'+experiment+'/'+plot_fname+'){: style="height:450px;width:450px"} \n',
        " \n",
        "  Caption: "+caption+"\n",
        "  \n"
    ]

    #check if file exists
    if os.path.exists(mdpath) and string_exists_in_file(mdpath, title):
        #The case when we just want to add for the same notebook. 
        print("This notebook has already added to the figure file, so this will add an additional figure.")
        lines_to_append=lines_to_append[6:]
        print(lines_to_append)
    elif os.path.exists(mdpath):        
        lines_to_append=lines_to_append[5:]
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
