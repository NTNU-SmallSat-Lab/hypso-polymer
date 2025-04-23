import numpy as np
from importlib.resources import files
from urllib.parse import urlparse, unquote

from pathlib import Path
import netCDF4 as nc

import sys
import os

from hypso import Hypso
from hypso.write import write_l1c_nc_file

#sys.path.insert(0, '/home/cameron/Projects/hypso-package/hypso/')

#POLYMER_PATH = '/home/cameron/Projects/polymer/'



import os

os.environ["DIR_POLYMER_AUXDATA"] = "/home/cameron/Projects/polymer_auxdata/"
os.environ["DIR_POLYMER_ANCILLARY"] = "/home/cameron/Projects/polymer_ancillary/"




#sys.path.insert(0, '/home/cameron/Projects/polymer/')

from polymer.main import run_atm_corr
from polymer.level1 import Level1
from polymer.level2 import Level2

#source ~/.venv/bin/activate
#python3 run_polymer.py /home/cameron/Documents/129.241.2.147:8009/image63N6E/image63N6E_2025-04-02T11-46-04Z/image63N6E_2025-04-02T11-46-04Z-l1a.nc /home/cameron/Documents/129.241.2.147:8009/image63N6E/image63N6E_2025-04-02T11-46-04Z/processing-temp/latitudes_indirectgeoref.dat /home/cameron/Documents/129.241.2.147:8009/image63N6E/image63N6E_2025-04-02T11-46-04Z/processing-temp/longitudes_indirectgeoref.dat


def main(l1a_nc_path, lats_path=None, lons_path=None) -> np.ndarray:

    # Check if the first file exists
    if not os.path.isfile(l1a_nc_path):
        print(f"Error: The file '{l1a_nc_path}' does not exist.")
        return

    # Process the first file
    print(f"Processing file: {l1a_nc_path}")

    l1a_nc_path = Path(l1a_nc_path)

    satobj = Hypso(path=l1a_nc_path, verbose=True)

    # Run indirect georeferencing
    if lats_path is not None and lons_path is not None:
        try:

            with open(lats_path, mode='rb') as file:
                file_content = file.read()
            
            lats = np.frombuffer(file_content, dtype=np.float32)

            lats = lats.reshape(satobj.spatial_dimensions)

            with open(lons_path, mode='rb') as file:
                file_content = file.read()
            
            lons = np.frombuffer(file_content, dtype=np.float32)
  
            lons = lons.reshape(satobj.spatial_dimensions)


            # Directly provide the indirect lat/lons loaded from the file. This function will run the track geometry computations.
            satobj.run_indirect_georeferencing(latitudes=lats, longitudes=lons)

        except Exception as ex:
            print(ex)
            print('Indirect georeferencing has failed. Defaulting to direct georeferencing.')

            satobj.run_direct_georeferencing()

    else:
        satobj.run_direct_georeferencing()

    satobj.generate_l1b_cube()
    satobj.generate_l1c_cube()

    write_l1c_nc_file(satobj, overwrite=True, datacube=False)

    l1c_nc_path = satobj.l1c_nc_file

    output_path = satobj.parent_dir

    #del satobj
    #satobj=None


    print("Polymer Done!")

 

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python run_acolite.py <l1a_nc_path> [lats_path] [lons_path]")
        sys.exit(1)

    l1a_nc_path = sys.argv[1]
    
    lats_path = sys.argv[2] if len(sys.argv) == 4 else None
    lons_path = sys.argv[3] if len(sys.argv) == 4 else None

    main(l1a_nc_path, lats_path, lons_path)