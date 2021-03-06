# -*- coding: utf-8 -*-
from . import __version__
from intake.source.base import DataSource, Schema

import json
import dask.dataframe as dd
from datetime import datetime, timedelta


class ShapeSource(DataSource):
    """Shape file intake source"""
    name = 'shape'
    version = __version__
    container = 'dataframe'
    partition_access = True

    def __init__(self, urlpath, bbox=None, geopandas_kwargs=None, metadata=None):
        """
        Parameters
        ----------
        urlpath : str or iterable, location of data
            Either the absolute or relative path to the file or URL to be opened.
            Some examples:
            - ``{{ CATALOG_DIR }}data/states.shp``
            - ``http://some.domain.com/data/dtates.shp``
        bbox : tuple | GeoDataFrame or GeoSeries, default None
            Filter features by given bounding box, GeoSeries, or GeoDataFrame.
            CRS mis-matches are resolved if given a GeoSeries or GeoDataFrame.
        geopandas_kwargs : dict
            Any further arguments to pass to geopandas's read_file.
        """
        self.urlpath = urlpath
        self._bbox = bbox
        self._geopandas_kwargs = geopandas_kwargs or {}
        self._dataframe = None

        super(ShapeSource, self).__init__(metadata=metadata)

    def _open_dataset(self, urlpath):
        """Open dataset using geopandas and use pattern fields to set new columns
        """
        import geopandas

        self._dataframe = geopandas.read_file(
            urlpath, bbox=self._bbox, **self._geopandas_kwargs)

    def _get_schema(self):
        if self._dataframe is None:
            self._open_dataset(self.urlpath)

        dtypes = self._dataframe.dtypes.to_dict()
        dtypes = {n: str(t) for (n, t) in dtypes.items()}
        return Schema(datashape=None,
                      dtype=dtypes,
                      shape=(None, len(dtypes)),
                      npartitions=1,
                      extra_metadata={})

    def _get_partition(self, i):
        self._get_schema()
        return self._dataframe

    def read(self):
        self._get_schema()
        return self._dataframe

    def to_dask(self):
        raise NotImplementedError()

    def _close(self):
        self._dataframe = None
