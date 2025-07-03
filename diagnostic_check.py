# diagnostic_check.py

import os
import sys
import platform

print("\n🔎 PYTHON & ENVIRONMENT INFO")
print("-----------------------------")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Environment path: {sys.prefix}")

try:
    import pyproj
    print("\n🧭 pyproj INFO")
    print("--------------")
    print(f"pyproj version: {pyproj.__version__}")
    print("PROJ data dir:", pyproj.datadir.get_data_dir())
except Exception as e:
    print("pyproj ERROR:", e)

try:
    import geopandas as gpd
    from shapely.geometry import Point
    print("\n🗺️  geopandas TEST")
    print("------------------")
    gdf = gpd.GeoDataFrame(geometry=[Point(144.9631, -37.8136)], crs='EPSG:4326')
    gdf_proj = gdf.to_crs(epsg=3857)
    print("Projection successful. Sample result:")
    print(gdf_proj)
except Exception as e:
    print("geopandas ERROR:", e)

try:
    import osmnx as ox
    print("\n🚲 osmnx INFO")
    print("-------------")
    print(f"osmnx version: {ox.__version__}")
except Exception as e:
    print("osmnx ERROR:", e)
