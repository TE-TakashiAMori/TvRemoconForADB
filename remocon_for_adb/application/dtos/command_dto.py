"""
Command DTOs
アプリケーション層で使用するデータ転送オブジェクト
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RemoteCommandDTO:
    """リモートコマンドのDTO"""
    
    command_type: str  # 'direction', 'button'
    key: str          # 'up', 'down', 'left', 'right', 'select', 'back', 'home'
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __eq__(self, other: object) -> bool:
        """同一性判定（タイムスタンプ以外で比較）"""
        if not isinstance(other, RemoteCommandDTO):
            return False
        return (
            self.command_type == other.command_type and
            self.key == other.key
        )


@dataclass
class CommandResultDTO:
    """コマンド実行結果のDTO"""
    
    success: bool
    message: str
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScreenshotCommandDTO:
    """スクリーンショットコマンドのDTO"""
    
    filename: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScreenshotResultDTO:
    """スクリーンショット実行結果のDTO"""
    
    success: bool
    filepath: str
    filesize: int
    message: str
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
