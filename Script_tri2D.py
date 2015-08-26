'''
Notes on running this python script for salome automatically:
in the bash run the command:
	salome720 -t -u <pathToScript>
Where -t = TUI only and -u execute pythonscript
afterwards execute following command to kill all sleeping salome sessions
	salome720 --killall
'''


####----------####
#### Preamble ####
####----------####

#importing necessary libraries and defining functions

import salome
from salome.geom import geomBuilder
geompy = geomBuilder.New(salome.myStudy)
gg = salome.ImportComponentGUI("GEOM")

import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh =  smeshBuilder.New(salome.myStudy)

import math

##-----------##
## Functions ##
##-----------##

def PrintMeshInfo(theMesh):
        aMesh = theMesh.GetMesh()
        print("Mesh description", aMesh.Dump())
        pass

####----------####
#### Geometry ####
####----------####

print("GEOMETRY TIME !")

##-----------##
## Constants ##
##-----------##
print "Reading in constants ..."

#lenght of tank m = 2.250
l=2.250
#thickness of pilot m = 0.01
w=0.01
#hight of pilot m = 0.825
h=0.825
#length of in/outlet
lin=0.125
hin=0.125
lout=0.125
hout=0.125

# export the mesh to a unv file or not
exportMesh = True

# usage of symmetry planes to lower computational burden
usesymmmetryplanes = True

#generation of north and south box
print("Making boxes")
tank = geompy.MakeBox(0,-w/2.,hin,l,w/2.,h-hout)
boxin =  geompy.MakeBox(l,-w/2.,0,l+lin,w/2.,hin)
boxout =  geompy.MakeBox(-lout,-w/2.,h-hout,0,w/2.,h)
tank_down = geompy.MakeBox(0,-w/2.,0,l,w/2.,hin)
tank_up = geompy.MakeBox(0,-w/2.,h-hout,l,w/2.,h)

#show
print("Showing the boxes in the study")
geompy.addToStudy(tank,"Boxtank")
geompy.addToStudy(boxin,"Boxin")
geompy.addToStudy(boxout,"Boxout")
geompy.addToStudy(tank_down,"Boxdown")
geompy.addToStudy(tank_up,"Boxup")

## Fuse
#Fuse_tb_in = geompy.MakeFuse(tank, boxin)
#Fuse_tb_out = geompy.MakeFuse(Fuse_tb_in, boxout)
#Fuse_tb_up = geompy.MakeFuse(Fuse_tb_out, tank_up)
#Fuse_tb_down = geompy.MakeFuse(Fuse_tb_up, tank_down)

#make compound
print("Generating of the compound")
#compound = geompy.MakeCompound(Fuse_tb_down)
compound = geompy.MakeCompound([tank, boxin, boxout, tank_down, tank_up])
geompy.addToStudy(compound,"compound")

#check if the generated shape is valid
print("Checking whether the created shape is valid")
IsValid = geompy.CheckShape(compound)
if IsValid == 0:
    raise(RuntimeError, "Invalid reactor created")
else:
    print("Hurray! Created reactor is valid!")

####----------####
####  Mesing  ####
####----------####

# Define a mesh on a geometry
hexa = smesh.Mesh(compound, "compound: Tetrahedrical mesh")

# create a Regular 1D algorithm for edges
algo1D_compound  = hexa.Segment()
algo1D_compound.MaxSize(0.05)
 
# create a 2D algorithm for faces
algo2D_compound = hexa.Triangle()
#algo2D_compound.LengthFromEdges()

# create a 3D algorithm for solids
algo3D_compound = hexa.Tetrahedron()

print("Computing the mesh ...")
# compute the mesh
test = hexa.Compute()
if test == 0:
    print "problem when computing the mesh"
else:
    print "mesh computed"
    pass   
print "End of script -- Feest!"