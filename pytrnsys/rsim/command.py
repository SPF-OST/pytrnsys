import collections.abc as _cabc
import dataclasses as _dc
import pathlib as _pl

import shortpath83 as _sp83


@_dc.dataclass
class Command:
    trnsysExeFilePath: _pl.Path
    deckFilePath: _pl.Path
    trnsysFlags: _cabc.Sequence[str]

    @property
    def args(self) -> _cabc.Sequence[str | _pl.Path]:
        shortTrnsysExeFilePath = _sp83.get_short_path_name(str(self.trnsysExeFilePath))
        shortDeckFilePath = _sp83.get_short_path_name(str(self.deckFilePath))

        args: _cabc.Sequence[str | _pl.Path] = [shortTrnsysExeFilePath, shortDeckFilePath, *self.trnsysFlags]

        return args

    @property
    def cwd(self) -> _pl.Path:
        return self.deckFilePath.parent
