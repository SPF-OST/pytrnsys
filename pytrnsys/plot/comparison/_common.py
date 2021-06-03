# pylint: skip-file
# type: ignore

__all__ = [
    "createManySeriesOrManyChunksFromValues",
    "ManySeries",
    "ManyChunks",
    "Series",
    "Chunk",
    "GroupingValue",
    "AxisValues",
]

import dataclasses as _dc
import typing as _tp

import numpy as _np

from pytrnsys.utils import uncertainFloat as _uf


def createManySeriesOrManyChunksFromValues(
    abscissaVariable, ordinateVariable, seriesVariable, chunkVariable, values, shallPrintUncertainties
) -> _tp.Union["ManySeries", "ManyChunks", None]:
    if not values:
        return None

    if not seriesVariable:
        valuesForSeries = values[None][None]

        abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
            abscissaVariable, ordinateVariable, valuesForSeries
        )

        series = Series(
            index=None,
            groupingValue=None,
            abscissa=abscissaValues,
            ordinate=ordinateValues,
            shallPrintUncertainties=shallPrintUncertainties,
        )
        return ManySeries([series])

    if not chunkVariable:
        allSeries = []
        for seriesValue, valuesForSeries in values[None].items():
            i = len(allSeries) + 1
            seriesGroupingValue = GroupingValue(seriesVariable, seriesValue)
            abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
                abscissaVariable, ordinateVariable, valuesForSeries
            )

            series = Series(i, seriesGroupingValue, abscissaValues, ordinateValues, shallPrintUncertainties)

            allSeries.append(series)

        return ManySeries(allSeries)

    chunks = []
    for chunkValue, chunkGroupingValue in values.items():
        allSeriesForChunk = []
        for seriesValue, valuesForSeries in chunkGroupingValue.items():
            i = sum(len(c.allSeries) for c in chunks) + 1
            seriesGroupingValue = GroupingValue(seriesVariable, seriesValue)

            abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
                abscissaVariable, ordinateVariable, valuesForSeries
            )

            series = Series(i, seriesGroupingValue, abscissaValues, ordinateValues, shallPrintUncertainties)
            allSeriesForChunk.append(series)

        chunkGroupingValue = GroupingValue(chunkVariable, chunkValue)
        chunk = Chunk(chunkGroupingValue, allSeriesForChunk)
        chunks.append(chunk)

        for series in allSeriesForChunk:
            series.chunk = chunk

    return ManyChunks(chunks)


def _createAbscissaAndOrdinateAxisValues(abscissaVariable, ordinateVariable, valuesForSeries):
    xs, xerrors, ys, yerrors = _getXAndYValuesAndErrorsOrderedByXValues(valuesForSeries)

    xAxisValues = _createAxisValues(abscissaVariable, xs, xerrors)
    yAxisValues = _createAxisValues(ordinateVariable, ys, yerrors)

    return xAxisValues, yAxisValues


def _getXAndYValuesAndErrorsOrderedByXValues(series) -> _tp.Tuple[_np.ndarray, _np.ndarray, _np.ndarray, _np.ndarray]:
    xs, ys = zip(*series)

    xValues, xErrors = _getValuesAndErrors(xs)
    yValues, yErrors = _getValuesAndErrors(ys)

    indices = _np.argsort(xValues)

    return xValues[indices], xErrors[indices], yValues[indices], yErrors[indices]


def _getValuesAndErrors(us):
    if not _haveValuesErrors(us):
        errors = [(0, 0) for _ in us]
        return _np.array(us), _np.array(errors)

    us = [_uf.UncertainFloat.from_dict(u) for u in us]

    values = [u.mean for u in us]
    errors = [(-u.toLowerBound, u.toUpperBound) for u in us]

    return _np.array(values), _np.array(errors)


def _haveValuesErrors(us):
    return any(isinstance(u, dict) for u in us)


def _createAxisValues(variableName, means, errors):
    xAxisValues = AxisValues(variableName, mins=means - errors[:, 0], means=means, maxs=means + errors[:, 1])
    return xAxisValues


@_dc.dataclass()
class ManyChunks:
    chunks: _tp.Sequence["Chunk"]


@_dc.dataclass()
class ManySeries:
    allSeries: _tp.Sequence["Series"]


@_dc.dataclass()
class Chunk:
    groupingValue: "GroupingValue"
    allSeries: _tp.Sequence["Series"]


@_dc.dataclass(eq=False)
class Series:
    index: _tp.Optional[int]
    groupingValue: _tp.Optional["GroupingValue"]

    abscissa: "AxisValues"
    ordinate: "AxisValues"

    shallPrintUncertainties: bool

    def __post_init__(self):
        if self.abscissa.length != self.ordinate.length:
            raise ValueError("`abscissaValues` and `ordinateValues` must be the same length.")
        self.length = self.abscissa.length

        if self.groupingValue and self.index is None:
            raise ValueError("If you specify a `groupingValue` you also need to provide an `index`.")

        self.chunk: _tp.Optional[Chunk] = None

        self._indexedAbscissaName = f"{self.abscissa.name}_{self.index}"

    def getAbscissaHeader(self, shallPrintUncertainties: bool):
        parts = self._getAbscissaHeaderParts(shallPrintUncertainties)
        return "\t".join(parts)

    def getOrdinateHeader(self, shallPrintUncertainties: bool):
        parts = self._getOrdinateHeaderParts(shallPrintUncertainties)
        return "\t".join(parts)

    def _getAbscissaHeaderParts(self, shallPrintUncertainties: bool) -> _tp.Sequence[str]:
        signs = self._getSigns(shallPrintUncertainties)

        if not self.groupingValue:
            return [f"{self.abscissa.name}{sign}" for sign in signs]

        return [f"{self._indexedAbscissaName}{sign}" for sign in signs]

    def _getOrdinateHeaderParts(self, shallPrintUncertainties: bool) -> _tp.Sequence[str]:
        signs = self._getSigns(shallPrintUncertainties)

        if not self.groupingValue:
            return [f"{self.ordinate.name}{sign}({self.abscissa.name})" for sign in signs]

        if not self.chunk:
            return [
                f"{self.ordinate.name}{sign}({self._indexedAbscissaName},{self.groupingValue.value})"
                for sign in signs
            ]

        return [
            f"{self.ordinate.name}{sign}({self._indexedAbscissaName},"
            f"{self.groupingValue.value},{self.chunk.groupingValue.value})"
            for sign in signs
        ]

    @staticmethod
    def _getSigns(shallPrintUncertainties):
        if not shallPrintUncertainties:
            return [""]

        return ["-", "=", "+"]


@_dc.dataclass()
class GroupingValue:
    name: str
    value: float


@_dc.dataclass()
class AxisValues:
    name: str
    mins: _np.ndarray
    means: _np.ndarray
    maxs: _np.ndarray

    def __post_init__(self):
        self._ensureAlLengthsEqualOrValueError()

        self.length = len(self.means)

        toLowerBound = self.means - self.mins
        toUpperBound = self.maxs - self.means
        self.errors = _np.vstack([toLowerBound, toUpperBound])

    def _ensureAlLengthsEqualOrValueError(self):
        shapes = {self.mins.shape, self.means.shape, self.maxs.shape}

        if len(shapes) != 1:
            raise ValueError("`mins`, `means` and `maxs` must all be same length.")
        shape = list(shapes)[0]

        if len(shape) != 1:
            raise ValueError("`mins`, `means` and `maxs` must all be same one-dimensional arrays.")
