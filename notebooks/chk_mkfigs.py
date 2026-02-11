#CB 30/10/2025
import glob

print("Script intended to help us find if we are missing scripts in mkfig.sh" )
try:
    with open("mkfigs.sh", "r") as file:
        lines = file.readlines()
        gettingclose=0
        files=[]
        for line in lines:

            if gettingclose==1:
                if ')' in line.strip():
                    break
                #print(line)
                #files=[script + '.ipynb' for script in line.split(' ')[1:-1]]
                #files.append(line.split(' ')[1:-1]+ '.ipynb')
                files.append(line.lstrip().rstrip()+ '.ipynb')

            #print(line.strip()) # Process each line
            if 'array' in line.strip():
                gettingclose=1
                continue
        actualfiles=sorted(glob.glob('*.ipynb')) 
        #import pdb;pdb.set_trace()

        print("" )
        print("files found from mkfigs.sh are: " + str(files))
        print("" )
        print("files found from current folder are : " + str(files))
        print("" )
        print("Their difference : " + str(set(actualfiles)-set(files)))
        print("" )
        print("" )
        print("Done" )

except FileNotFoundError:
    print("Error: The file 'mkfigs.sh' was not found.")
