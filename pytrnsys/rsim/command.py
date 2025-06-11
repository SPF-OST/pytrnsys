import pathlib as _pl
import dataclasses as _dc
import collections.abc as _cabc


@_dc.dataclass
class Command:
    trnsysExeFilePath: _pl.Path
    deckFilePath: _pl.Path
    trnsysFlags: _cabc.Sequence[str]

    @property
    def args(self) -> _cabc.Sequence[str | _pl.Path]:
        args = [
            self.trnsysExeFilePath,
            self.deckFilePath.name
            *self.trnsysFlags
        ]
        
        return args
    
    @property
    def cwd(self) -> _pl.Path:
        return self.deckFilePath.parent
