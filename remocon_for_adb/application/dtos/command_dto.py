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
    is_long_press: bool = False  # 長押しフラグ
    duration_ms: Optional[int] = None  # 長押し時間（ミリ秒）※将来の拡張用
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
    directory: Optional[str] = None
    format: str = "png"
    quality: int = 95  # JPEG品質（1-100）
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


@dataclass
class ScreenRecordCommandDTO:
    """画面録画コマンドのDTO"""
    
    duration: int = 30  # 録画時間（秒）、0=手動停止モード
    filename: Optional[str] = None
    directory: Optional[str] = None
    format: str = "mp4"
    manual_mode: bool = False  # 手動停止モード
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScreenRecordResultDTO:
    """画面録画実行結果のDTO"""
    
    success: bool
    filepath: str
    filesize: int
    duration: float  # 実際の録画時間（秒）
    message: str
    execution_time: float  # コマンド実行時間（秒）
    timestamp: datetime = field(default_factory=datetime.now)
