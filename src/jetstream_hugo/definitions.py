import os
import platform
import pickle as pkl
from pathlib import Path
from nptyping import NDArray
from typing import Any, Callable, ClassVar, Dict, Optional
from dataclasses import dataclass, field
import time

import numpy as np
import pandas as pd
import xarray as xr

np.set_printoptions(precision=5, suppress=True)
os.environ["PATH"] += os.pathsep + "/storage/homefs/hb22g102/latex/bin/x86_64-linux/"

pf = platform.platform()
if pf.find("cray") >= 0:
    NODE = "DAINT"
    DATADIR = "/scratch/snx3000/hbanderi/data/persistent"
    N_WORKERS = 8
    MEMORY_LIMIT = "8GiB"
elif platform.node()[:4] == "clim":
    NODE = "CLIM"
    DATADIR = "/scratch2/hugo"
    N_WORKERS = 8
    MEMORY_LIMIT = "4GiB"
elif pf.find("el7") >= 0:  # find better later
    NODE = "UBELIX"
    DATADIR = "/storage/workspaces/giub_meteo_impacts/ci01"
    os.environ["CDO"] = "/storage/homefs/hb22g102/mambaforge/envs/env11/bin/cdo"
    N_WORKERS = 6
    MEMORY_LIMIT = "20GB"
else:
    NODE = "LOCAL"
    N_WORKERS = 8
    DATADIR = "../data"
    MEMORY_LIMIT = "2GB"

COMPUTE_KWARGS = {
    "processes": True,
    "threads_per_worker": 1,
    "n_workers": N_WORKERS,
    "memory_limit": MEMORY_LIMIT,
}

CLIMSTOR = "/mnt/climstor/ecmwf/era5/raw"
FIGURES = "/storage/homefs/hb22g102/persistent-extremes-era5/Figures"
DEFAULT_VARNAME = "__xarray_dataarray_variable__"

DATERANGEPL = pd.date_range("19590101", "20211231")
YEARSPL = np.unique(DATERANGEPL.year)
DATERANGEPL_SUMMER = DATERANGEPL[np.isin(DATERANGEPL.month, [6, 7, 8])]

DATERANGEPL_EXT = pd.date_range("19400101", "20221231")
YEARSPL_EXT = np.unique(DATERANGEPL_EXT.year)
DATERANGEPL_EXT_SUMMER = DATERANGEPL_EXT[np.isin(DATERANGEPL_EXT.month, [6, 7, 8])]

DATERANGEPL_EXT_6H = pd.date_range("19400101", "20230101", freq="6h", inclusive="left")
DATERANGEPL_EXT_6H_SUMMER = DATERANGEPL_EXT_6H[np.isin(DATERANGEPL_EXT_6H.month, [6, 7, 8])]

DATERANGEML = pd.date_range("19770101", "20211231")

WINDBINS = np.arange(0, 25, 0.5)
LATBINS = np.arange(15, 75.1, 0.5)
LONBINS = np.arange(-90, 30, 1)
DEPBINS = np.arange(-25, 25.1, 0.5)

REGIONS = ["S-W", "West", "S-E", "North", "East", "N-E"]

SMALLNAME = {
    "Geopotential": "z",
    "Wind": "s",
    "Temperature": "t",
    "Precipitation": "tp",
}  # Wind speed

PRETTIER_VARNAME = {
    "mean_lon": "Avg. longitude",
    "mean_lat": "Avg. latitude",
    "mean_lev": "Avg. level",
    "Lon": "Lon. of max. speed",
    "Lat": "Lat. of max. speed",
    "Spe": "Max. speed",
    "lon_ext": "Extent in lon.",
    "lat_ext": "Extent in lat.",
    "tilt": "Tilt",
    "sinuosity": "Sinuosity",
    "width": "Width",
    "int": "Integrated speed",
    "int_low": "Intd. speed low level",
    "int_over_europe": "Intd. speed over Eur.",
    "persistence": "Jet lifetime",
    "exists": "Exists",
    "int_ratio": "Ratio low / high ints",
}

UNITS = {
    "mean_lon": r"$~^{\circ} \mathrm{E}$",
    "mean_lat": r"$~^{\circ} \mathrm{N}$",
    "mean_lev": r"$\mathrm{hPa}$",
    "Lon": r"$~^{\circ} \mathrm{E}$",
    "Lat": r"$~^{\circ} \mathrm{N}$",
    "Spe": r"$\mathrm{m} \cdot \mathrm{s}^{-1}$",
    "lon_ext": r"$~^{\circ} \mathrm{E}$",
    "lat_ext": r"$~^{\circ} \mathrm{N}$",
    "tilt": r"$~^{\circ} \mathrm{N} / ~^{\circ} \mathrm{E}$",
    "sinuosity": r"$~$",
    "width": r"$~^{\circ} \mathrm{N}$",
    "int": r"$\mathrm{m}^2 \cdot \mathrm{s}^{-1}$",
    "int_low": r"$\mathrm{m}^2 \cdot \mathrm{s}^{-1}$",
    "int_over_europe": r"$\mathrm{m}^2 \cdot \mathrm{s}^{-1}$",
    "persistence": r"$\mathrm{day}$",
    "exists": r"$~$",
}

DEFAULT_VALUES = {
    "mean_lon": 0,
    "mean_lat": 45,
    "mean_lev": 250,
    "Lon": 0,
    "Lat": 45,
    "Spe": 0,
    "lon_ext": 0,
    "lat_ext": 0,
    "tilt": 0,
    "sinuosity": 0,
    "width": 0,
    "int": 0,
    "int_low": 0,
    "int_over_europe": 0,
    "persistence": 1,
    "exists": 0,
}

LATEXY_VARNAME = {
    "mean_lon": "$\overline{\lambda}$",
    "mean_lat": "$\overline{\phi}$",
    "mean_lev": "$\overline{p}$",
    "Lon": "$\lambda_{s^*}$",
    "Lat": "$\phi_{s^*}$",
    "Spe": "$s^*$",
    "lon_ext": "$\Delta \lambda$",
    "lat_ext": "$\Delta \phi$",
    "tilt": r"$\overline{\frac{\mathrm{d}\phi}{\mathrm{d}\lambda}}$",
    "sinuosity": r"$R^2$",
    "width": "$w$",
    "int": "$\int s \mathrm{d}\lambda$",
    "int_low": r"$\int_{700\text{ hPa}} s \mathrm{d}\lambda$",
    "int_over_europe": "$\int_{\mathrm{Eur.}} s \mathrm{d}\lambda$",
    "persistence": "$\Delta t$",
}

RADIUS = 6.371e6  # m
OMEGA = 7.2921e-5  # rad.s-1
KAPPA = 0.2854
R_SPECIFIC_AIR = 287.0500676


def degcos(x: float) -> float:
    return np.cos(x / 180 * np.pi)


def degsin(x: float) -> float:
    return np.sin(x / 180 * np.pi)


def load_pickle(filename: str | Path) -> Any:
    with open(filename, "rb") as handle:
        to_ret = pkl.load(handle)
    return to_ret


def to_zero_one(X):
    Xmin = X.min(axis=0)
    Xmax = X.max(axis=0)
    
    return (X - Xmin[None, :]) / (Xmax - Xmin)[None, :], Xmin, Xmax


def revert_zero_one(X, Xmin, Xmax):
    return Xmin[None, :] + (Xmax - Xmin)[None, :] * X


def save_pickle(to_save: Any, filename: str | Path) -> None:
    with open(filename, "wb") as handle:
        pkl.dump(to_save, handle)


def case_insensitive_equal(str1: str, str2: str) -> bool:
    """case-insensitive string equality check

    Args:
        str1 (str): first string
        str2 (str): second string

    Returns:
        bool: case insensitive string equality
    """
    return str1.casefold() == str2.casefold()


def infer_direction(to_plot: Any) -> int:
    max_ = np.nanmax(to_plot)
    min_ = np.nanmin(to_plot)
    try:
        max_ = max_.item()
        min_ = min_.item()
    except AttributeError:
        pass
    sym = np.sign(max_) == - np.sign(min_)
    sym = sym and np.abs(np.log10(np.abs(max_)) - np.log10(np.abs(min_))) <= 2
    if sym:
        return 0
    return 1 if np.abs(max_) > np.abs(min_) else -1    


def labels_to_mask(labels: xr.DataArray | NDArray) -> NDArray:
    if isinstance(labels, xr.DataArray):
        labels = labels.values
    unique_labels = np.unique(labels)
    return labels[:, None] == unique_labels[None, :]


def get_region(da: xr.DataArray | xr.Dataset) -> tuple:
    try:
        return (
            da.lon.min().item(),
            da.lon.max().item(),
            da.lat.min().item(),
            da.lat.max().item(),
        )
    except AttributeError:
        return (
            da.longitude.min().item(),
            da.longitude.max().item(),
            da.latitude.min().item(),
            da.latitude.max().item(),
        )
        
        
def slice_1d(da: xr.DataArray | xr.Dataset, indexers: list, dim: str = "points"):
    return da.loc[tuple(
        [xr.DataArray(indexer, dims=dim) for indexer in indexers]
    )]


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

@dataclass
class Timer:
    timers: ClassVar[Dict[str, float]] = {}
    name: Optional[str] = None
    text: str = "Elapsed time: {:0.4f} seconds"
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Add timer to dict of timers after initialization"""
        if self.name is not None:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            self.logger(self.text.format(elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time
    
    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()