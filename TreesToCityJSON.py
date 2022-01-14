import struct
import bpy
import csv
import glob
import os
import math
import random

from mathutils import Vector
from os import SEEK_CUR
from typing import BinaryIO

class Rijksdriehoek:
  def __init__(self, rd_x = None, rd_y = None):
    self.rd_x = rd_x
    self.rd_y = rd_y
    self.X0 = 155000
    self.Y0 = 463000
    self.PHI0 = 52.15517440
    self.LAM0 = 5.38720621

  def from_wgs(self, lat, lon):
    self.rd_x, self.rd_y = self.__to_rd(lat, lon)

  def to_wgs(self,):
    return self.__to_wgs(self.rd_x, self.rd_y)

  def __to_rd(self, latin, lonin):
    # based off of https://github.com/djvanderlaan/rijksdriehoek
    pqr = [(0, 1, 190094.945),
           (1, 1, -11832.228),
           (2, 1, -114.221),
           (0, 3, -32.391),
           (1, 0, -0.705),
           (3, 1, -2.34),
           (1, 3, -0.608),
           (0, 2, -0.008),
           (2, 3, 0.148)]
    
    pqs = [(1, 0, 309056.544),
           (0, 2, 3638.893),
           (2, 0, 73.077),
           (1, 2, -157.984),
           (3, 0, 59.788),
           (0, 1, 0.433),
           (2, 2, -6.439),
           (1, 1, -0.032),
           (0, 4, 0.092),
           (1, 4, -0.054)]

    dphi = 0.36 * ( latin - self.PHI0 )
    dlam = 0.36 * ( lonin - self.LAM0 )

    X = self.X0
    Y = self.Y0

    for p, q, r in pqr:
        X += r * dphi**p * dlam**q 

    for p, q, s in pqs:
        Y += s * dphi**p * dlam**q

    return [X,Y]

  def __to_wgs(self, xin, yin):
    # based off of https://github.com/djvanderlaan/rijksdriehoek

    pqk = [(0, 1, 3235.65389),
        (2, 0, -32.58297),
        (0, 2, -0.24750),
        (2, 1, -0.84978),
        (0, 3, -0.06550),
        (2, 2, -0.01709),
        (1, 0, -0.00738),
        (4, 0, 0.00530),
        (2, 3, -0.00039),
        (4, 1, 0.00033),
        (1, 1, -0.00012)]

    pql = [(1, 0, 5260.52916), 
        (1, 1, 105.94684), 
        (1, 2, 2.45656), 
        (3, 0, -0.81885), 
        (1, 3, 0.05594), 
        (3, 1, -0.05607), 
        (0, 1, 0.01199), 
        (3, 2, -0.00256), 
        (1, 4, 0.00128), 
        (0, 2, 0.00022), 
        (2, 0, -0.00022), 
        (5, 0, 0.00026)]

    dx = 1E-5 * ( xin - self.X0 )
    dy = 1E-5 * ( yin - self.Y0 )
    
    phi = self.PHI0
    lam = self.LAM0

    for p, q, k in pqk:
        phi += k * dx**p * dy**q / 3600

    for p, q, l in pql:
        lam += l * dx**p * dy**q / 3600

    return [phi,lam]


ENDIAN_PREFIXES = ("@", "<", ">", "=", "!")

#BinaryReader:
#read_bool() -> bool
#read_byte() -> int
#read_ubyte() -> int
#read_int16() -> int
#read_uint16() -> int
#read_int32() -> int
#read_uint32() -> int
#read_int64() -> int
#read_uint64() -> int
#read_int() -> int (alias of read_int32())
#read_uint() -> int (alias of read_uint32())
#read_float() -> float
#read_double() -> float

class BinaryReader:
    def __init__(self, buf: BinaryIO, endian: str = "<") -> None:
        self.buf = buf
        self.endian = endian

    def align(self) -> None:
        old = self.tell()
        new = (old + 3) & -4
        if new > old:
            self.seek(new - old, SEEK_CUR)

    def read(self, *args) -> bytes:
        return self.buf.read(*args)

    def seek(self, *args) -> int:
        return self.buf.seek(*args)

    def tell(self) -> int:
        return self.buf.tell()

    def read_string(self, size: int = None, encoding: str = "utf-8") -> str:
        if size is None:
            ret = self.read_cstring()
        else:
            ret = struct.unpack(self.endian + "%is" % (size), self.read(size))[0]

        return ret.decode(encoding)

    def read_cstring(self) -> bytes:
        ret = []
        c = b""
        while c != b"\0":
            ret.append(c)
            c = self.read(1)
            if not c:
                raise ValueError("Unterminated string: %r" % (ret))
        return b"".join(ret)

    def read_bool(self) -> bool:
        return bool(struct.unpack(self.endian + "b", self.read(1))[0])

    def read_byte(self) -> int:
        return struct.unpack(self.endian + "b", self.read(1))[0]

    def read_ubyte(self) -> int:
        return struct.unpack(self.endian + "B", self.read(1))[0]

    def read_int16(self) -> int:
        return struct.unpack(self.endian + "h", self.read(2))[0]

    def read_uint16(self) -> int:
        return struct.unpack(self.endian + "H", self.read(2))[0]

    def read_int32(self) -> int:
        return struct.unpack(self.endian + "i", self.read(4))[0]

    def read_uint32(self) -> int:
        return struct.unpack(self.endian + "I", self.read(4))[0]

    def read_int64(self) -> int:
        return struct.unpack(self.endian + "q", self.read(8))[0]

    def read_uint64(self) -> int:
        return struct.unpack(self.endian + "Q", self.read(8))[0]

    def read_float(self) -> float:
        return struct.unpack(self.endian + "f", self.read(4))[0]

    def read_double(self) -> float:
        return struct.unpack(self.endian + "d", self.read(8))[0]

    def read_struct(self, format: str) -> tuple:
        if not format.startswith(ENDIAN_PREFIXES):
            format = self.endian + format
        size = struct.calcsize(format)
        return struct.unpack(format, self.read(size))

    # Aliases

    def read_int(self) -> int:
        return self.read_int32()

    def read_uint(self) -> int:
        return self.read_uint32()

#Start ---------------------------------------------------
sourcePathGroundTiles  = bpy.path.abspath("C:/Projects/GemeenteAmsterdam/Docs/Blender/BomenNaarCityJSON/SourceTiles/")
sourcePathCSV  = bpy.path.abspath("//SourceCSV/")
outputPath = bpy.path.abspath("//Output/trees")

class Tile(object):
    trees = []
    RD = [0,0]

class Tree(object):
    name = ""
    RD = [0,0]
    instancedObject = None

#Clear scene
def ClearScene():  
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def GetVisual(description):
    objectName = description.replace(" (cultuurvariëteit)","")
    visuals = bpy.data.collections["Trees"].all_objects
    if objectName in visuals:
        return visuals[objectName]
    return visuals["Onbekend"]          
 
def EstimateHeight(heightDescription):
    possibleNumbers = heightDescription.split(" ")
    height = 0
    numbersFoundInString = 0
    for number in possibleNumbers:
        if number.isnumeric():
            height += float(number)
            numbersFoundInString += 1
    height = height / numbersFoundInString
    return height      
    
ClearScene()

#RD stuff
rd = Rijksdriehoek()

#Read tree data from CSV's
tiles = {}

for csvFile in glob.glob(os.path.join(sourcePathCSV, '*.csv')):
    with open(csvFile, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        lineNr = -1
        for tree in reader: 
            lineNr += 1
            if(lineNr == 0) or not (tree): 
                continue
            
            #convert WGS84 to RD
            rd.from_wgs(float(tree[16]), float(tree[15]))
            
            #generate tree data
            treeData = Tree()
            treeData.name = tree[0]
            treeData.height = EstimateHeight(tree[5])
            treeData.visual = GetVisual(tree[1])
            treeData.RD = [rd.rd_x,rd.rd_y]
            
            #move into proper rounded tile
            tileX = math.floor(rd.rd_x / 1000) * 1000
            tileY = math.floor(rd.rd_y / 1000) * 1000
            tileKey = str(tileX)+"-"+str(tileY)

            if tileKey not in tiles:
                newTile = Tile()
                newTile.trees = []
                newTile.RD = [tileX,tileY]
                tiles[tileKey] = newTile
                
            tile = tiles[tileKey]
            tile.RD = [tileX,tileY]
            tile.trees.append(treeData)
                
        print("Read trees: " + str(lineNr) + "")

totalTiles = len(tiles)
currentTile = 0
print("Grouped into tiles: " + str(totalTiles) + "")

for key in tiles:
    currentTile += 1
    print("Tile: " + str(currentTile) + "/" + str(totalTiles))
    
    #Write CityJSON cityobject trees
    tileTreesFile = outputPath+key+".json"
    
    tile = tiles[key]
    tileTrees = tile.trees
    print(key + " contains " + str(len(tileTrees)) + " trees")   
    
    #Load existing tree tile
    tileMeshPath = sourcePathGroundTiles + "/terrain_"+ key +"-lod1.bin"
    if not os.path.isfile(tileMeshPath):
        continue    
    else:
        print(tileMeshPath)
    
    with open(tileMeshPath, "rb") as f:
        reader = BinaryReader(f)
        
        #binary data
        version = reader.read_int()
        vertexCount = reader.read_int()
        normalsCount = reader.read_int()
        uvsCount = reader.read_int()
        indicesCount = reader.read_int()
        submeshCount = reader.read_int()
        
        vertices = []
        indices = []
        
        for i in range(vertexCount):
            vX = reader.read_float()
            vY = reader.read_float()
            vZ = reader.read_float()
            vertices.append((vX,vZ,vY)) #flip Z and Y
        
        for i in range(normalsCount):
            vnX = reader.read_float()
            vnY = reader.read_float()
            vnZ = reader.read_float()
            
        for i in range(uvsCount):
            uvX = reader.read_float()
            uvY = reader.read_float()
        
        for i in range(indicesCount):
            index = reader.read_int()
            indices.append(index)
            
        #add every triangle to face mesh
        facesCount = int(indicesCount / 3)
        print("vertices " + str(vertexCount))
        print("faces " + str(facesCount))
        faces = []
        for i in range(indicesCount):
            if((i % 3) == 0):
                pointA = indices[i]
                pointB = indices[i+1]
                pointC = indices[i+2]
                triangle = (pointA,pointB,pointC)
                faces.append(triangle)
              
        #read into new mesh      
        new_mesh = bpy.data.meshes.new('tile')
        new_mesh.from_pydata(vertices,[],faces) 

        # make object from mesh
        new_object = bpy.data.objects.new('tile', new_mesh)
        # collection
        collection = bpy.data.collections["Collection"]
        # add object to scene collection
        collection.objects.link(new_object)
        
        for tree in tileTrees:
            #determine height at a point
            coordinateInTileX = tree.RD[0] - (tile.RD[0] + 500)
            coordinateInTileY = tree.RD[1] - (tile.RD[1] + 500)
            
            #print("Planting tree at : " + str(coordinateInTileX) + "," + str(coordinateInTileY))
            ray_begin = Vector((coordinateInTileX, coordinateInTileY, 100))
            ray_direction = Vector((0,0,-1)) #Down            
            # do a ray cast on newly created plane
            success, rayHitLocation, normal, poly_index = new_object.ray_cast(ray_begin, ray_direction)
             
            #Add tree based on name
            bpy.ops.object.add_named(linked=True,name="Tree", matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (rayHitLocation.x, rayHitLocation.y, rayHitLocation.z, 1)))
            tree.instancedObject = bpy.context.object
            bpy.context.object.data.calc_loop_triangles()
            randomRotation=random.uniform(0,6.2)
            bpy.ops.transform.rotate(value=randomRotation, orient_axis='Z')
            bpy.ops.transform.resize(value=(tree.height, tree.height, tree.height), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            
    #Write CityJSON
    open(tileTreesFile, 'w').close() #Clear existing content
    f = open(tileTreesFile, "a")
    f.write("{\"type\": \"CityJSON\", \"version\": \"1.0\", \"metadata\": {}, \"CityObjects\":")
    f.write("{")
    verticesOutput = []
    uvsOutput = []
    currentVertexIndex = 0
    totalTrees = len(tileTrees)
    currentTree = 0
    maxTrees = 20 #handy for testing
    
    for tree in tileTrees:
        #Clear indices and UV list for every tree (unqique)
        indicesOutput = []
        uvIndicesOutput = []
        #convert all vertex coordinates to tile local
        for triangle in tree.instancedObject.data.loop_triangles:
            indicesOutput.append([[currentVertexIndex,currentVertexIndex+1,currentVertexIndex+2]])
            
            #every triangle is preceeded by an integer refering to texture index
            uvIndicesOutput.append([[0,currentVertexIndex,currentVertexIndex+1,currentVertexIndex+2]])
            
            currentVertexIndex += 3
            for vertIndex in triangle.vertices:
                localVertLocation = tree.instancedObject.data.vertices[vertIndex].co
                uvLocation = tree.instancedObject.data.uv_layers.active.data[vertIndex].uv
                
                matrixWorld = tree.instancedObject.matrix_world
                worldVertLocation = matrixWorld @ localVertLocation
                vertexOutput = [round(worldVertLocation.x,3),round(worldVertLocation.y,3),round(worldVertLocation.z,3)]
                uvOutput = [round(uvLocation.x,5),round(uvLocation.y,5)]
                
                verticesOutput.append(vertexOutput)
                uvsOutput.append(uvOutput)
            
        f.write("\"" + tree.name + "\":{")
        f.write("\"geometry\": [{") #geometry start
        f.write("\"type\":\"MultiSurface\",")
        f.write("\"lod\":1,")
        f.write("\"boundaries\":" + str(indicesOutput) + ",")
        f.write("\"texture\":{\"summer-textures\":{\"values\":" + str(uvIndicesOutput) + "}}")
        f.write("}],") #geometry end
        f.write("\"type\":\"Vegetation\",")
        f.write("\"identificatie\":\"" + tree.name + "\"")
        f.write("}")
        currentTree += 1
        if maxTrees != 0 and (currentTree >= maxTrees):
            break
        if(currentTree < totalTrees):
            f.write(",")
    f.write("},")
    f.write("\"appearance\":{")
    f.write("\"textures\":[{\"type\":\"PNG\",\"image\":\"trees.png\"}],")
    f.write("\"vertices-texture\":" + str(uvsOutput) + "")
    f.write("},")
    f.write("\"vertices\":" + str(verticesOutput) + ",")
    f.write("\"transform\":{\"scale\": [1, 1, 1],\"translate\": [" + str(tile.RD[0]-500) + ", " + str(tile.RD[1]-500) +", 0]}")
    f.write("}")
    f.close()
    
    ClearScene()
    
print(" ")
print("All done!")