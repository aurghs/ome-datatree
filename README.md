# ome-datatree

Prototype reader for [ome-zarr v0.3](https://ngff.openmicroscopy.org/0.3/) data into [datatree](https://github.com/xarray-contrib/datatree) structure.

Usage:

```python-repl
import ome_datatree
dt = ome_datatree.open_ome_datatree(data_path)
``` 