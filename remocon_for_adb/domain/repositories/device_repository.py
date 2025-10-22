"""
Device Repository Interface
デバイス操作の抽象化インターフェース
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus


class DeviceNotFoundError(Exception):
    """デバイス未発見例外"""
    pass


class DeviceConnectionError(Exception):
    """デバイス接続例外"""
    pass


class DeviceRepository(ABC):
    """デバイス操作リポジトリのインターフェース"""

    @abstractmethod
    def get_connected_devices(self) -> List[AndroidDevice]:
        """接続中のデバイス一覧を取得"""
        pass

    @abstractmethod
    def get_device_by_id(self, device_id: str) -> AndroidDevice:
        """指定されたIDのデバイスを取得
        
        Args:
            device_id: デバイスID
            
        Returns:
            AndroidDevice: 指定されたデバイス
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
        """
        pass

    @abstractmethod
    def is_device_available(self, device_id: str) -> bool:
        """デバイスが利用可能かチェック
        
        Args:
            device_id: デバイスID
            
        Returns:
            bool: 利用可能な場合True
        """
        pass

    @abstractmethod
    def update_device_status(self, device_id: str, status: DeviceStatus) -> None:
        """デバイスのステータスを更新
        
        Args:
            device_id: デバイスID
            status: 新しいステータス
        """
        pass

    @abstractmethod
    def refresh_device_list(self) -> None:
        """デバイスリストを更新"""
        pass

    @abstractmethod
    def execute_command(self, device_id: str, command: str) -> bool:
        """デバイスでコマンドを実行
        
        Args:
            device_id: デバイスID
            command: 実行するコマンド
            
        Returns:
            bool: 実行成功の場合True
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            DeviceConnectionError: 接続エラーの場合
        """
        pass

    @abstractmethod
    def capture_screenshot(self, device_id: str, local_path: str) -> bool:
        """スクリーンショットを取得
        
        Args:
            device_id: デバイスID
            local_path: 保存先パス
            
        Returns:
            bool: 取得成功の場合True
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            DeviceConnectionError: 接続エラーの場合
        """
        pass

    @abstractmethod
    def start_screen_record(self, device_id: str, local_path: str, duration: int = 0) -> bool:
        """画面録画を開始
        
        Args:
            device_id: デバイスID
            local_path: 保存先パス
            duration: 録画時間（秒）、0=手動停止モード
            
        Returns:
            bool: 開始成功の場合True
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            DeviceConnectionError: 接続エラーの場合
        """
        pass

    @abstractmethod
    def stop_screen_record(self, device_id: str, local_path: str) -> bool:
        """画面録画を停止
        
        Args:
            device_id: デバイスID
            local_path: 保存先パス
            
        Returns:
            bool: 停止成功の場合True
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
            DeviceConnectionError: 接続エラーの場合
        """
        pass

    @abstractmethod
    def is_screen_recording(self, device_id: str) -> bool:
        """画面録画中かどうかを確認
        
        Args:
            device_id: デバイスID
            
        Returns:
            bool: 録画中の場合True
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
        """
        pass
