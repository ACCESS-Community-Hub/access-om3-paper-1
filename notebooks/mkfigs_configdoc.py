import os
#little function to create a figure file for om3 configs
#cb
def mkmd(title,caption,experiment,plot_fname,mdfol):
    print('')
    print(title)
    print(caption)
    print(experiment)
    print(plot_fname)
    print('')

    mdpath=mdfol+experiment+'.md'

    lines_to_append = [
        "# "+experiment+"\n",
        " \n",
        "# This page shows evaluation figures from ACCESS-OM3 experiment "+ experiment+ " for discussion and see plotting scripts have a look at [this repository](https://github.com/acCESS-Community-Hub/access-om3-paper-1/) and related [issues](https://github.com/ACCESS-Community-Hub/access-om3-paper-1/issues).\n",
        " \n",
        "## "+title+"\n",
        "<!-- The next line will hopefully be a rendered figure. --> \n",
        '!['+caption+'](mkmd/'+plot_fname+') \n',
        "  Caption: "+caption+"\n",
        "  \n"
    ]

    #check if file exists
    if os.path.exists(mdpath):
        lines_to_append=lines_to_append[3:]

    #should add a check to see if title already exists :q


    try:
        with open(mdpath, 'a') as file:
            file.writelines(lines_to_append)
        print(f"Lines appended to {mdpath} successfully.")
    except Exception as e:
        print(f"Error: {e}")
    return

