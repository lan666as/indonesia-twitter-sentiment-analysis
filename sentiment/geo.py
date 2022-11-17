import geopandas
from shapely.geometry import Point

class PointSpatialJoin(object):
    """
    Give ISO 3166-2 code to a given point coordinate
    """

    def __init__(self, path='sentiment/assets/geoBoundaries-IDN-ADM1.geojson'):
        self.path = path
        self.gdf = geopandas.read_file(self.path)
        self.province_dict = self.build_dict(self.gdf)

    def build_dict(self, gdf):
        return {row["shapeISO"] : row["geometry"] for i, row in gdf.iterrows()}

    def find_province(self, x, y):
        if (abs(x-0.0) < 1e-6 and abs(y-0.0) < 1e-6):
            return ""

        point = Point(x, y)
        for k, v in self.province_dict.items():
            if point.within(v):
                return k
        
        return ""
