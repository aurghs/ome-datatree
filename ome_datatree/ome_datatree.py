import os
import pathlib
import typing as T

import datatree
import xarray as xr
import zarr


class DummyStore(object):
    def __init__(self, zarr_group):
        self.zarr_group = zarr_group


def _iter_zarr_groups(root, parent=""):
    parent = pathlib.Path(parent)
    for path, group in root.groups():
        gpath = parent / path
        yield str(gpath)
        yield from _iter_zarr_groups(group, parent=gpath)


def open_variable(
    path: str,
    group: zarr.hierarchy.Group,
    dimensions: T.List[str],
):
    array = group[path]
    store = DummyStore(group)
    zarray_wrapper = xr.backends.zarr.ZarrArrayWrapper(path, store)
    data = xr.core.indexing.LazilyIndexedArray(zarray_wrapper)
    attributes = dict(array.attrs)

    if getattr(array, "fill_value") is not None:
        attributes["_FillValue"] = array.fill_value
    return xr.core.variable.Variable(dimensions, data, attributes)


def open_group(
    store,
    path: str = None,
    consolidated: bool = False,
    **open_kwargs,
):
    if isinstance(store, os.PathLike):
        store = os.fspath(store)

    if "chunk_store" in open_kwargs:
        if consolidated is None:
            consolidated = False

    if consolidated:
        zarr_group = zarr.open_consolidated(store, mode="r", path=path, **open_kwargs)
    else:
        zarr_group = zarr.open_group(store, mode="r", path=path, **open_kwargs)
    return zarr_group


def read_datasets(
    group: zarr.hierarchy.Group,
    chunks: int = None,
):
    path = group.path
    attrs = group.attrs.asdict()
    axes = group.attrs.get("axes", [])
    multiscales = group.attrs.get("multiscales", [])

    datasets_attrs = {}
    dataset_axes = {}
    for multiscale in multiscales:
        for ds_attrs in multiscale["datasets"]:
            datasets_attrs[ds_attrs["path"]] = ds_attrs
            dataset_axes[ds_attrs["path"]] = multiscale.get("axes", axes)

    datasets = {path or "root": xr.Dataset(data_vars={}, attrs=attrs)}
    for ds_name, data in list(group.arrays()):
        rel_path = os.path.relpath(data.path, path)
        attrs = datasets_attrs.get(rel_path, {}).copy()
        axes = dataset_axes.get(rel_path, None)
        var = open_variable(rel_path, group, dimensions=axes)
        ds = xr.Dataset(data_vars={ds_name: var}, attrs=attrs)
        if chunks is not None:
            ds = ds.chunk(chunks)
        datasets[data.path] = ds
    return datasets


def open_ome_datatree(
    store,
    path: str = None,
    chunks: T.Optional[int] = None,
    consolidated: bool = None,
    **open_kwargs,
) -> datatree.DataTree:

    with open_group(
        store, path=path, consolidated=consolidated, **open_kwargs
    ) as root_group:
        datasets = read_datasets(root_group, **open_kwargs)
        tree = datatree.DataTree.from_dict(datasets)
        for path_subgroup in _iter_zarr_groups(root_group):
            try:
                datasets = read_datasets(root_group[path_subgroup], chunks=chunks)
                for ds_path, ds in datasets.items():
                    tree[ds_path] = ds
            except zarr.errors.PathNotFoundError:
                tree[ds_path] = None
    return tree
