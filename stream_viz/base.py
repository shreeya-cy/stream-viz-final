from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from stream_viz.utils.drifts_types import AllDriftType, get_all_drift_types_keys


@dataclass
class DataEncoder(ABC):
    def __init__(self):
        self._original_data: pd.DataFrame = pd.DataFrame()
        self._encoded_data: pd.DataFrame = pd.DataFrame()

    def read_csv_data(self, *args, **kwargs) -> None:
        data = pd.read_csv(*args, **kwargs)
        if data is None or data.empty:
            raise ValueError("Unable to read data")
        self.original_data = data

    @abstractmethod  # Enforces that method must be implemented by any subclass
    def encode_data(self, *args, **kwargs):
        pass

    @property
    def original_data(self) -> pd.DataFrame:
        if self._original_data is None or self._original_data.empty:
            raise ValueError(
                "Original Data is empty. Please call `read_csv_data` method"
            )
        return self._original_data

    @original_data.setter
    def original_data(self, value: pd.DataFrame):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("original_data must be a pandas DataFrame")
        self._original_data = value

    @property
    def encoded_data(self) -> pd.DataFrame:
        if self._encoded_data is None or self._encoded_data.empty:
            raise ValueError("Encoded Data is empty. Please call `encode_data` method")
        return self._encoded_data

    @encoded_data.setter
    def encoded_data(self, value: pd.DataFrame):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("encoded_data must be a pandas DataFrame")
        self._encoded_data = value


class DriftDetector(ABC):
    def __init__(self):
        self._drift_records: List[AllDriftType] = []
        self._valid_keys: set[str] = get_all_drift_types_keys()

    @abstractmethod
    def update(self, x_i: Dict, y_i: int, tpt: int):
        pass

    @abstractmethod
    def detect_drift(self, tpt: int, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def plot_drift(self, start_tpt: int, end_tpt: int, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def drift_records(self) -> List[AllDriftType]:
        """Getter for drift records"""
        pass

    @drift_records.setter
    @abstractmethod
    def drift_records(self, drift_record: AllDriftType) -> None:
        """Setter for drift records - adds a new drift to the list"""
        pass

    def _validate_drift(self, drift: AllDriftType) -> bool:
        """Validates the drift record"""
        if not any(key in drift for key in self._valid_keys):
            return False
        for key in self._valid_keys:
            if key in drift:
                if "start_tp" in drift[key] and "end_tp" in drift[key]:
                    return True
        return False


class Streamer(ABC):
    def __init__(
        self,
        rcd_detector_obj: Optional[DriftDetector] = None,
        fd_detector_obj: Optional[DriftDetector] = None,
    ):
        self.rcd_detector_obj: Optional[DriftDetector] = rcd_detector_obj
        self.fd_detector_obj: Optional[DriftDetector] = fd_detector_obj

    @abstractmethod
    def stream_data(self, X_df: pd.DataFrame, y_df: pd.Series) -> None:
        pass


class Velocity(ABC):
    @abstractmethod
    def plot_velocity(self, *args, **kwargs):
        pass


class StrategyPlot(ABC):
    @abstractmethod
    def plot_graph(self, *args, **kwargs):
        pass


class Binning(ABC):
    def __init__(self, **kwargs):
        self._bin_thresholds: List[float] = []
        self._binned_data_X: pd.DataFrame = pd.DataFrame()
        # regex pattern for the columns name that needs to binned
        self._col_name_regex = kwargs.get("col_name_regex", r"^n")
        # New name for the columns to be binned
        self._bin_col_names = kwargs.get("bin_col_names", r"bin_idx_")

    @abstractmethod
    def perform_binning(self, *args, **kwargs):
        pass

    @property
    def bin_thresholds(self) -> List[float]:
        if self._bin_thresholds is None:
            raise ValueError("bin_thresholds is empty")
        return self._bin_thresholds

    @bin_thresholds.setter
    def bin_thresholds(self, value: List[float]):
        if not isinstance(value, list):
            raise ValueError("bin_thresholds must be a List")
        self._bin_thresholds = value

    @property
    def binned_data_X(self) -> pd.DataFrame:
        if self._binned_data_X is None or self._binned_data_X.empty:
            raise ValueError("Binned Data is empty.")
        return self._binned_data_X

    @binned_data_X.setter
    def binned_data_X(self, value: pd.DataFrame):
        if not isinstance(value, pd.DataFrame):
            raise ValueError("Input must be a Dataframe")
        self._binned_data_X = value
