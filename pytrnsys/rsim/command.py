import collections.abc as _cabc
import dataclasses as _dc
import pathlib as _pl


@_dc.dataclass
class Command:
    trnsysExeFilePath: _pl.Path
    deckFilePath: _pl.Path
    trnsysFlags: _cabc.Sequence[str]

    @property
    def args(self) -> _cabc.Sequence[str | _pl.Path]:
        args = [self.trnsysExeFilePath, self.deckFilePath.name * self.trnsysFlags]

        return args

    @property
    def cwd(self) -> _pl.Path:
        return self.deckFilePath.parent
