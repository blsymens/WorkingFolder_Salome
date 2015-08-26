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

#Hexagonaal mesh of tetragonaal
MeshisHexa = False

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

#locate edges needed for mesh specification
print("Making hypotheses ...")

F_inlet = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l+lin,0,hin/2.))
F_outlet = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(-lout,0,(2*h-hout)/2.))
F_top1 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(-lout/2.,0,h))
F_top2 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,0,h))
F_bottom1 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,0,0))
F_bottom2 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex((2*l+lin)/2.,0.,0))
F_wall_left_up = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(0,0,(hin+h-hout)/2.))
F_wall_left_down = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(0,0,hin/2.))
F_wall_right_up = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l,0,(2*h-hin)/2.))
F_wall_right_down = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l,0,(hin+h-hout)/2.))
F_wall_out = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(-lout/2.,0,h-hout))
F_wall_in = geompy.GetFaceNearPoint(compound,geompy.MakeVertex((2*l+lin)/2.,0,hin))

F_back1 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(-lout/2,-w/2.,(2*h-hout)/2.))
F_back2 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,-w/2.,(2*h-hout)/2.))
F_back3 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,-w/2.,(hin+h-hout)/2.))
F_back4 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2,-w/2.,hin/2.))
F_back5 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex((2*l+lin)/2.,-w/2.,hin/2.))
F_front1 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(-lout/2,w/2.,(2*h-hout)/2.))
F_front2 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,w/2.,(2*h-hout)/2.))
F_front3 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2.,w/2.,(hin+h-hout)/2.))
F_front4 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex(l/2,w/2.,hin/2.))
F_front5 = geompy.GetFaceNearPoint(compound,geompy.MakeVertex((2*l+lin)/2.,w/2.,hin/2.))

'''
geompy.addToStudy(F_inlet,"Inlet")
geompy.addToStudy(F_outlet,"Outlet")
geompy.addToStudy(F_top1,"Top_left")
geompy.addToStudy(F_top2,"Top_right")
geompy.addToStudy(F_bottom1,"Bottom_left")
geompy.addToStudy(F_bottom2,"Bottom_right")
geompy.addToStudy(F_wall_left_up,"Left_up")
geompy.addToStudy(F_wall_right_up,"Right_up")
geompy.addToStudy(F_wall_left_down,"Left_down")
geompy.addToStudy(F_wall_right_down,"Right_down")
geompy.addToStudy(F_wall_out,"Left_out")
geompy.addToStudy(F_wall_in,"Right_in")

geompy.addToStudy(F_back1,"North_left")
geompy.addToStudy(F_back2,"North_up")
geompy.addToStudy(F_back3,"North_m")
geompy.addToStudy(F_back4,"North_down")
geompy.addToStudy(F_back5,"North_right")
geompy.addToStudy(F_front1,"South_left")
geompy.addToStudy(F_front2,"South_up")
geompy.addToStudy(F_front3,"South_m")
geompy.addToStudy(F_front4,"South_down")
geompy.addToStudy(F_front5,"South_right")
'''

#Creating lists
Wall_back_front = [F_back1,F_back2,F_back3,F_back4,F_back5,F_front1,F_front2,F_front3,F_front4,F_front5]
Wall_back_front_up_down_left_right = [F_back1,F_back2,F_back3,F_back4,F_back5,F_front1,F_front2,F_front3,
F_front4,F_front5,F_wall_out,F_wall_left_up,F_wall_left_down,F_wall_in,F_wall_left_down,F_wall_left_up,F_top1,F_top2,F_bottom1,F_bottom1]

#Creating groups
group_wall2D = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
geompy.UnionList(group_wall2D,Wall_back_front)
geompy.addToStudyInFather(compound, group_wall2D, "Wall 2D")

group_wall3D = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
geompy.UnionList(group_wall3D,Wall_back_front_up_down_left_right)
geompy.addToStudyInFather(compound, group_wall3D, "Wall 3D")
   
####----------####
####  Mesing  ####
####----------####

# Define a mesh on a geometry
if MeshisHexa == True:
    hexa = smesh.Mesh(compound, "compound: hexahedrical mesh")

    # create a Regular 1D algorithm for edges
    algo1D_compound  = hexa.Segment()
    algo1D_compound.LocalLength(0.03)                         #lengte van elke cel
    #algo1D_compound.MaxSize(0.05)                            #maximum lengte
    #algo1D_compound.Adaptive(0.02,0.10,0.10)                 #min length, max length, max afstand van segment tot edge
    #algo1D_compound.NumberOfSegments(cells_per_length)       #elk sub-deel een vast aantal cellen! Vermijden bij verschillende sub-delen
    #algo1D_compound.AutomaticLength()                        #3D mesh, kiest alles zelf!
    #algo1D_compound.Deflection1D(1e-5)    
     
    # create a quadrangle 2D algorithm for faces
    algo2D_compound = hexa.Quadrangle()

    # create a hexahedron 3D algorithm for solids
    algo3D_compound = hexa.Hexahedron()

else:
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