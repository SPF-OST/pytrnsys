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
import enum as _enum
import typing as _tp

import numpy as _np

from pytrnsys.utils import uncertainFloat as _uf

VALUES_RELATIVE_TOLERANCE = 1e-9
GROUPING_VARIABLE_VALUES_ROUND_TO_DIGITS = 2

Values = (
    _tp.Sequence[tuple[float, float]]
    | _tp.Mapping[str, _tp.Sequence[tuple[float, float]]]
    | _tp.Mapping[str, _tp.Mapping[str, _tp.Sequence[tuple[float, float]]]]
)


def createManySeriesOrManyChunksFromValues(  # pylint: disable=too-many-locals
    abscissaVariable: str,
    ordinateVariable: str,
    seriesVariable: str | None,
    chunkVariable: str | None,
    values: Values,
    shallPlotUncertainties,
) -> _tp.Union["ManySeries", "ManyChunks", None]:
    if not values:
        return None

    if not seriesVariable:
        valuesForSeries = values

        abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
            abscissaVariable, ordinateVariable, valuesForSeries
        )

        series = Series(
            index=None,
            groupingValue=None,
            abscissa=abscissaValues,
            ordinate=ordinateValues,
            shallPrintUncertainties=shallPlotUncertainties,
        )
        return ManySeries([series])

    assert isinstance(values, dict)

    if not chunkVariable:
        allSeries = list[Series]()
        sortedSeriesLabelsAndValues = _getSortedByLabel(values.items())
        for seriesLabel, valuesForSeries in sortedSeriesLabelsAndValues:
            i = len(allSeries) + 1
            seriesGroupingValue = GroupingValue(seriesVariable, seriesLabel)
            abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
                abscissaVariable, ordinateVariable, valuesForSeries
            )

            series = Series(i, seriesGroupingValue, abscissaValues, ordinateValues, shallPlotUncertainties)

            allSeries.append(series)

        return ManySeries(allSeries)

    chunks = list[Chunk]()
    sortedChunkLabelsAndValues = _getSortedByLabel(values.items())
    for chunkLabel, valuesForChunk in sortedChunkLabelsAndValues:
        allSeriesForChunk = []
        sortedSeriesLabelsAndValues = _getSortedByLabel(valuesForChunk.items())
        for seriesLabel, valuesForSeries in sortedSeriesLabelsAndValues:
            i = sum(len(c.allSeries) for c in chunks) + 1
            seriesGroupingValue = GroupingValue(seriesVariable, seriesLabel)

            abscissaValues, ordinateValues = _createAbscissaAndOrdinateAxisValues(
                abscissaVariable, ordinateVariable, valuesForSeries
            )

            series = Series(i, seriesGroupingValue, abscissaValues, ordinateValues, shallPlotUncertainties)
            allSeriesForChunk.append(series)

        chunkGroupingValue = GroupingValue(chunkVariable, chunkLabel)
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


def _getXAndYValuesAndErrorsOrderedByXValues(series) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray, _np.ndarray]:
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


_T = _tp.TypeVar("_T")


def _getSortedByLabel(groupingLabelAndValues: _tp.Iterable[tuple[str, _T]]) -> _tp.Sequence[tuple[str, _T]]:
    sortedGroupingLabelAndValues = sorted(groupingLabelAndValues, key=_getFirstItem)
    return sortedGroupingLabelAndValues


def _getFirstItem(pair: tuple[str, _T]) -> str:
    return pair[0]


@_dc.dataclass()
class ManyChunks:
    chunks: _tp.Sequence["Chunk"]

    def __post_init__(self) -> None:
        if not self.chunks:
            raise ValueError("Must be given at least one chunk.")

    @property
    def chunkLength(self) -> int:
        return max(len(c.allSeries) for c in self.chunks)


@_dc.dataclass()
class ManySeries:
    allSeries: _tp.Sequence["Series"]


@_dc.dataclass()
class Chunk:
    groupingValue: "GroupingValue"
    allSeries: _tp.Sequence["Series"]


@_dc.dataclass()
class Series:  # pylint: disable=too-many-instance-attributes
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
                f"{self.ordinate.name}{sign}({self._indexedAbscissaName},{self.groupingValue.label})" for sign in signs
            ]

        return [
            f"{self.ordinate.name}{sign}({self._indexedAbscissaName},"
            f"{self.groupingValue.label},{self.chunk.groupingValue.label})"
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
    label: str


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

        if len(shapes) != 1:  # /NOSONAR
            raise ValueError("`mins`, `means` and `maxs` must all be same length.")

        shape = list(shapes)[0]

        if len(shape) != 1:
            raise ValueError("`mins`, `means` and `maxs` must all be same one-dimensional arrays.")

    def __eq__(self, other: "AxisValues") -> bool:
        return _isClose(self.mins, other.mins) and _isClose(self.means, other.means) and _isClose(self.maxs, other.maxs)


def _isClose(x: _np.ndarray, y: _np.ndarray) -> bool:
    return _np.isclose(x, y, rtol=VALUES_RELATIVE_TOLERANCE).all()


def createManySeriesOrManyChunksFromResults(
    allResults: _tp.Sequence[_tp.Mapping[str, _tp.Any]],
    abscissaVariable: str,
    ordinateVariable: str,
    seriesVariable: str | None,
    chunkVariable: str | None,
    shallPlotUncertainties: bool,
):
    values = {} if seriesVariable else []
    for results in allResults:
        xAxis = _getValue(results, abscissaVariable)
        yAxis = _getValue(results, ordinateVariable)

        seriesValues = _getSeriesValues(values, seriesVariable, chunkVariable, results)

        seriesValues.append((xAxis, yAxis))

    manySeriesOrChunks = createManySeriesOrManyChunksFromValues(
        abscissaVariable, ordinateVariable, seriesVariable, chunkVariable, values, shallPlotUncertainties
    )

    return manySeriesOrChunks


_SeriesValues = list[tuple[float, float]]
_WritableValues = (
    _SeriesValues  # one series
    | dict[str, _SeriesValues]  # many series
    | dict[str, dict[str, _SeriesValues]]  # many chunks of series
)


def _getSeriesValues(
    values: _WritableValues,
    seriesVariable: str | None,
    chunkVariable: str | None,
    results: _tp.Mapping[str, _tp.Any],
) -> _SeriesValues:
    if not seriesVariable:
        seriesValues = values
        return seriesValues

    seriesLabel = _getLabel(seriesVariable, results, _VariableType.SERIES)

    if not chunkVariable:
        if seriesLabel not in values:
            values[seriesLabel] = []

        seriesValues = values[seriesLabel]

        return seriesValues

    chunkLabel = _getLabel(chunkVariable, results, _VariableType.CHUNK)

    assert isinstance(values, dict)

    if chunkLabel not in values:
        values[chunkLabel] = {}

    chunkValues = values[chunkLabel]

    if seriesLabel not in chunkValues:
        chunkValues[seriesLabel] = []

    seriesValues = values[chunkLabel][seriesLabel]

    return seriesValues


class _VariableType(_enum.Enum):
    SERIES = "series"
    CHUNK = "chunk"


def _getLabel(
    variableName: str,
    results: _tp.Mapping[str, str | float | dict],
    variableType: _VariableType,
) -> str:
    variableValue = results[variableName]
    if not isinstance(variableValue, (float, str)):
        raise ValueError(f"The {variableType.name} variable must have a scalar value.")

    if isinstance(variableValue, str):
        label = variableValue
        return label

    formatSpecifier = f".{GROUPING_VARIABLE_VALUES_ROUND_TO_DIGITS}f"
    label = format(variableValue, formatSpecifier)

    return label


def _getValue(resultsDict, variable):
    if "[" not in variable:
        yAxis = resultsDict[variable]
    else:
        name, index = str(variable).split("[")
        index = int(index.replace("]", ""))
        yAxis = resultsDict[name][index]
    return yAxis
