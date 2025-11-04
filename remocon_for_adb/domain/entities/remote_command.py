"""
Remote Command エンティティ
リモコン操作コマンドを表現するドメインエンティティ
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class CommandType(Enum):
    """コマンドタイプの列挙型"""
    DIRECTION = "direction"
    BUTTON = "button"
    CUSTOM = "custom"


class DirectionKey(Enum):
    """方向キーの列挙型"""
    UP = "KEYCODE_DPAD_UP"
    DOWN = "KEYCODE_DPAD_DOWN"
    LEFT = "KEYCODE_DPAD_LEFT"
    RIGHT = "KEYCODE_DPAD_RIGHT"


class ButtonKey(Enum):
    """ボタンキーの列挙型（Android TV必須キーのみ）"""
    SELECT = "KEYCODE_DPAD_CENTER"
    BACK = "KEYCODE_BACK"
    HOME = "KEYCODE_HOME"


@dataclass
class RemoteCommand:
    """リモコンコマンドのエンティティ"""

    command_type: CommandType
    key_code: str
    raw_command: str
    timestamp: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """初期化後の処理"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @classmethod
    def create_direction_command(cls, direction: DirectionKey) -> 'RemoteCommand':
        """方向キーコマンドを作成"""
        return cls(
            command_type=CommandType.DIRECTION,
            key_code=direction.value,
            raw_command=f"input keyevent {direction.value}"
        )
    
    @classmethod
    def create_button_command(cls, button: ButtonKey) -> 'RemoteCommand':
        """ボタンコマンドを作成"""
        return cls(
            command_type=CommandType.BUTTON,
            key_code=button.value,
            raw_command=f"input keyevent {button.value}"
        )
    
    @classmethod
    def create_custom_command(cls, keycode: str) -> 'RemoteCommand':
        """カスタムコマンドを作成"""
        return cls(
            command_type=CommandType.CUSTOM,
            key_code=keycode,
            raw_command=f"input keyevent {keycode}"
        )
    
    @classmethod
    def from_string(cls, command_str: str) -> 'RemoteCommand':
        """文字列からコマンドを作成"""
        command_str = command_str.lower().strip()
        
        # 方向キーマッピング
        direction_mapping = {
            'up': DirectionKey.UP,
            'down': DirectionKey.DOWN,
            'left': DirectionKey.LEFT,
            'right': DirectionKey.RIGHT
        }
        
        # ボタンマッピング
        button_mapping = {
            'select': ButtonKey.SELECT,
            'back': ButtonKey.BACK,
            'home': ButtonKey.HOME,
            'menu': ButtonKey.MENU
        }
        
        # 方向キーチェック
        if command_str in direction_mapping:
            return cls.create_direction_command(direction_mapping[command_str])
        
        # ボタンキーチェック
        if command_str in button_mapping:
            return cls.create_button_command(button_mapping[command_str])
        
        # 無効な文字列の場合
        raise ValueError(f"Invalid command string: {command_str}")
    
    def __eq__(self, other: object) -> bool:
        """コマンドの同一性判定（キーコードで判定）"""
        if not isinstance(other, RemoteCommand):
            return False
        return self.key_code == other.key_code
    
    def __hash__(self) -> int:
        """ハッシュ値（キーコードベース）"""
        return hash(self.key_code)
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"RemoteCommand(type={self.command_type.value}, key={self.key_code})"
    
    def is_direction_command(self) -> bool:
        """方向キーコマンドかどうか"""
        return self.command_type == CommandType.DIRECTION
    
    def is_button_command(self) -> bool:
        """ボタンコマンドかどうか"""
        return self.command_type == CommandType.BUTTON
