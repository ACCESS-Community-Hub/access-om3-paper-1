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

    mdpath=mdfol+experiment+'.md'
    print('Adding a figure to markdown doc: '+mdpath)

    lines_to_append = [
        "# "+experiment+"\n",
        " \n",
        "# This page shows evaluation figures from ACCESS-OM3 experiment "+ experiment+ " for discussion and see plotting scripts have a look at [this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
        " \n",
        "## "+title+"\n",
        " \n",
        '!['+caption+'](mkmd/'+plot_fname+') \n',
        "  Caption: "+caption+"\n",
        "  \n"
    ]

    #check if file exists
    if os.path.exists(mdpath):
        lines_to_append=lines_to_append[4:]

    #should add a check to see if title already exists 
    if string_exists_in_file(mdpath, title):
        print("This notebook has already added to the figure file, so this will add an additional figure.")
        lines_to_append=lines_to_append[5:]

    try:
        with open(mdpath, 'a') as file:
            file.writelines(lines_to_append)
        print(f"Lines appended to {mdpath} successfully.")
    except Exception as e:
        print(f"Error: {e}")
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
        print(f"Error: The file '{filename}' was not found.")
        return False

