"""
Android Device エンティティ
Android TVデバイスを表現するドメインエンティティ
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DeviceStatus(Enum):
    """デバイスの接続状態を表す列挙型"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNAUTHORIZED = "unauthorized"
    OFFLINE = "offline"


@dataclass
class AndroidDevice:
    """Android TVデバイスのエンティティ"""

    device_id: str
    device_name: str
    status: DeviceStatus
    last_seen: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """初期化後の処理"""
        if self.last_seen is None:
            self.last_seen = datetime.now()

        # バリデーション
        self._validate_device_id()
    
    def _validate_device_id(self) -> None:
        """デバイスIDの検証"""
        if not self.device_id or not self.device_id.strip():
            raise ValueError("Device ID cannot be empty or whitespace")
    
    def __eq__(self, other: object) -> bool:
        """デバイスの同一性判定（IDで判定）"""
        if not isinstance(other, AndroidDevice):
            return False
        return self.device_id == other.device_id
    
    def __hash__(self) -> int:
        """ハッシュ値（IDベース）"""
        return hash(self.device_id)
    
    def update_status(self, new_status: DeviceStatus) -> None:
        """ステータスの更新"""
        self.status = new_status
        self.last_seen = datetime.now()
    
    def is_available(self) -> bool:
        """デバイスが操作可能かどうか"""
        return self.status == DeviceStatus.CONNECTED
