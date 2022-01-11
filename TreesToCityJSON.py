import struct
import bpy
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



sourcePath  = bpy.path.abspath("//SourceTiles/terrain_121000-486000-lod1.bin")

#Read CSV's

#

with open(sourcePath, "rb") as f:
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
    # make collection
    new_collection = bpy.data.collections.new('new_collection')
    bpy.context.scene.collection.children.link(new_collection)
    # add object to scene collection
    new_collection.objects.link(new_object)
    
    #determine height at a point
    ray_begin = Vector((0.5, 0, 100))
    ray_end = Vector((0.5, 0,-100))
    ray_direction = ray_end - ray_begin
    ray_direction.normalize()
    # covert ray_begin to "plane_ob" local space
    
    # do a ray cast on newly created plane
    success, rayHitLocation, normal, poly_index = new_object.ray_cast(ray_begin, ray_direction)
    print("cast_result:", rayHitLocation)
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=rayHitLocation, scale=(1, 1, 1))
    
    
    # convert RD and other way around
    rd = Rijksdriehoek()
    
    print("Original coordinates in WGS’84: {},{}".format(str(52.3761973), str(4.8936216))) 
    rd.from_wgs(52.3761973, 4.8936216) 
    print("Rijksdriehoek: {},{}".format(str(rd.rd_x), str(rd.rd_y))) 