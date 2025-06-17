import collections.abc as _cabc
import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import shortpath83 as _sp83


@_dc.dataclass
class Command:
    """
    This class represents a simulation that we are going to run in a separate
    process with TRNSYS using `subprocess.Popen`.
    """

    MAX_DECK_FILE_PATH_LENGTH: _tp.ClassVar[int] = 260

    trnsysExeFilePath: _pl.Path
    deckFilePath: _pl.Path
    trnsysFlags: _cabc.Sequence[str]

    def __post_init__(self) -> None:
        if not self.deckFilePath.is_absolute():
            raise ValueError("Deck file path must be absolute.", self.deckFilePath)

    @property
    def truncatedDeckFilePath(self) -> _pl.Path:
        # For more details see here:
        # https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry#enable-long-paths-in-windows-10-version-1607-and-later
        drive = self.deckFilePath.drive
        root = self.deckFilePath.root
        deckFilePathString = str(self.deckFilePath)
        pathLength = len(deckFilePathString) - len(drive) - len(root)

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
        return self.truncatedDeckFilePath.parent
