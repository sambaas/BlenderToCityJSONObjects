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