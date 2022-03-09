# ome-datatree

Prototype reader for [ome-zarr v0.3](https://ngff.openmicroscopy.org/0.3/) data into [datatree](https://github.com/xarray-contrib/datatree) structure.

Usage:


```python-repl
import ome_datatree
data_path = ...
dt = ome_datatree.open_ome_datatree(data_path)
``` 

A sample data can be found at: 
https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.3/idr0079A/9836998.zarr

if `ome-zarr` is installed, the data can be downloaded as follows:
```python-repl
import ome_zarr.utils
ome_zarr.utils.download("https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.3/idr0079A/9836998.zarr")
``` 

