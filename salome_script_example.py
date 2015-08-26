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

#length reactor in meter = 0.343819 m
l = 0.001
# number of cells per 100 micrometer of microreactor
cells_per_length = 20./0.0002
# simulations in 2D or in 3D
is2D = True
# width of the reactor = 0.2 mm
# attention, when using symmetry planes, w is half the width of the reactor, 
# i.e. the length from the wall to the symmetry plane.
# confusing, I know, it's just for ease of programming
w = 0.0001
# height of the reactor = 0.4 mm	
# this dimension will be reduced in 2D simulations
# 3D & symmetry planes: see above
h = 0.000001
# export the mesh to a unv file or not
exportMesh = True
# the ratio of the width of cells at the wall / at the center
cellratio = 4.
# usage of symmetry planes to lower computational burden
usesymmmetryplanes = True

#generation of north and south box
print("Making boxes")
box = geompy.MakeBox(0.,-w/2.,0.,l,w/2.,h) 

#show
print("Showing the boxe in the study")
geompy.addToStudy(box,"Box")

#make compound
print("Generating of the compound")
compound = geompy.MakeCompound([box])
geompy.addToStudy(compound,"compound")

#check if the generated shape is valid
print("Checking whether the created shape is valid")
IsValid = geompy.CheckShape(compound)
if IsValid == 0:
    raise(RuntimeError, "Invalid reactor created")
else:
    print("Hurray! Created reactor is valid!")

#find faces for generation of groups
print("Generation of groupies (aka groups) ...")
F_inlet = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(0., 0., h/2.))
F_outlet = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(l, 0., h/2.))
F_side_North = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(l/2., w/2., h/2.))
F_side_South = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(l/2., -w/2., h/2.))
F_up = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(l/2., 0., h))
F_down = geompy.GetFaceNearPoint(compound, geompy.MakeVertex(l/2., 0., -h))

#Generating lists of faces
F_wall_2D = [F_side_North, F_side_South]
F_wall_3D = [F_side_North, F_side_South, F_up, F_down]
F_front_back = [F_up, F_down]
F_sym_sym_2D = [F_side_North]
F_sym_wall_2D = [F_side_South]
F_sym_sym_3D = [F_side_North, F_down]
F_sym_wall_3D = [F_side_South, F_up]

#Generating group
group_inlet = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
group_wall = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
group_outlet = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])

geompy.UnionList(group_inlet, [F_inlet])
geompy.addToStudyInFather(compound, group_inlet, "inlet")
geompy.UnionList(group_outlet, [F_outlet])
geompy.addToStudyInFather(compound, group_outlet, "outlet")

if is2D == True:
    group_front_back = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
    geompy.UnionList(group_front_back, F_front_back)
    geompy.addToStudyInFather(compound, group_front_back, "front_back")
    if usesymmmetryplanes == False:    
        geompy.UnionList(group_wall, F_wall_2D)
        geompy.addToStudyInFather(compound, group_wall, "wall")
    if usesymmmetryplanes == True:
        geompy.UnionList(group_wall, F_sym_wall_2D)
        geompy.addToStudyInFather(compound, group_wall, "wall")
        group_symmetry = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
        geompy.UnionList(group_symmetry, F_sym_sym_2D)
        geompy.addToStudyInFather(compound, group_symmetry, "symmetry_plane")
else:
    if usesymmmetryplanes == False:
        geompy.UnionList(group_wall, F_wall_3D)
        geompy.addToStudyInFather(compound, group_wall, "wall")
    if usesymmmetryplanes == True:
        geompy.UnionList(group_wall, F_sym_wall_3D)
        geompy.addToStudyInFather(compound, group_wall, "wall")
        group_symmetry = geompy.CreateGroup(compound, geompy.ShapeType["FACE"])
        geompy.UnionList(group_symmetry, F_sym_sym_3D)
        geompy.addToStudyInFather(compound, group_symmetry, "symmetry_plane")

####------####
#### Mesh ####
####------####

print("\nMESH TIME !")

#locate edges needed for mesh specification
print("Making hypotheses ...")
#getting the edges
E_Z = geompy.GetEdgeNearPoint(compound, geompy.MakeVertex(0., w/2., h/2.))
E_inlet = geompy.GetEdgeNearPoint(compound, geompy.MakeVertex(0., 0., h))
E_side = geompy.GetEdgeNearPoint(compound, geompy.MakeVertex(l/2., w/2., h))

#Create a hexahedral mesh 
hexa_compound = smesh.Mesh(compound, "compound: hexahedrical mesh")

# create a Regular 1D algorithm for edges
algo1D_compound  = hexa_compound.Segment()

# create a quadrangle 2D algorithm for faces
algo2D_compound = hexa_compound.Quadrangle()

# create a hexahedron 3D algorithm for solids
algo3D_compound = hexa_compound.Hexahedron()

# define hypotheses
# hypotheses for all edges
algo1D_compound.NumberOfSegments(int(cells_per_length*l))

# create a sub-mesh with local 1D hypothesis and propagation
# define "Propagation" hypothesis that propagates all other 1D hypotheses
# from all edges on the opposite side of a face in case of quadrangular faces
algo_local_Z = hexa_compound.Segment(E_Z)
if is2D == True:
    algo_local_Z.NumberOfSegments(1)
if is2D == False:
    algo_local_Z.NumberOfSegments(int(cells_per_length*h), 1./cellratio)
algo_local_Z.Propagation()        

algo_local_inlet = hexa_compound.Segment(E_inlet)
#NumberOfSegments( NoOfSegments, ScaleFactor )
#==============================================================================
#     CHECK WHETHER SCALE FACTOR SHOULD BE INVERSED OR NOT
#==============================================================================
algo_local_inlet.NumberOfSegments(int(cells_per_length*w), cellratio)
algo_local_inlet.Propagation()

print("Computing the mesh ...")
# compute the mesh
hexa_compound.Compute()

hexa_compound.GroupOnGeom(group_inlet,"inlet",SMESH.FACE)
hexa_compound.GroupOnGeom(group_outlet,"outlet",SMESH.FACE)
hexa_compound.GroupOnGeom(group_wall,"wall",SMESH.FACE)
if is2D == True:
    hexa_compound.GroupOnGeom(group_front_back,"front_back",SMESH.FACE)
if usesymmmetryplanes == True:
    hexa_compound.GroupOnGeom(group_symmetry,"symmetry_plane",SMESH.FACE)
	
print("Printing mesh info!\n")
# print mesh info
PrintMeshInfo(hexa_compound)

print("Total length:\t=\t%g m" %(l))
print("Total area:\t=\t%g m^2" %(l*w))
print("Total volume:\t=\t%g m^3" %(l*w*h))

#export the mesh in a unv file
if exportMesh == True:
	print("Exporting the mesh to a unv file ...")
	hexa_compound.ExportUNV("./compound_meander_simplified.unv", 0)

print("\nEnd of script!")
