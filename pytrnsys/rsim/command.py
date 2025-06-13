import collections.abc as _cabc
import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import shortpath83 as _sp83


@_dc.dataclass
class Command:
    MAX_DECK_FILE_PATH_LENGTH: _tp.ClassVar[int] = 260

    trnsysExeFilePath: _pl.Path
    deckFilePath: _pl.Path
    trnsysFlags: _cabc.Sequence[str]

    @property
    def truncatedDeckFilePath(self) -> _pl.Path:
        deckFilePathString = str(self.deckFilePath)

        pathLength = len(deckFilePathString)
        if pathLength < self.MAX_DECK_FILE_PATH_LENGTH:
            return self.deckFilePath

        truncatedDeckFilePathString = _sp83.get_short_path_name(deckFilePathString)
        truncatedDeckFilePath = _pl.Path(truncatedDeckFilePathString)
        return truncatedDeckFilePath

    @property
    def args(self) -> _cabc.Sequence[str | _pl.Path]:
        args: _cabc.Sequence[str | _pl.Path] = [self.trnsysExeFilePath, self.truncatedDeckFilePath, *self.trnsysFlags]

        return args

    @property
    def cwd(self) -> _pl.Path:
        return self.deckFilePath.parent
