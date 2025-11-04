"""
Remote Control Use Case
リモコン操作機能のユースケース実装
"""
import time
from typing import List
from remocon_for_adb.application.dtos.command_dto import RemoteCommandDTO, CommandResultDTO
from remocon_for_adb.domain.entities.android_device import AndroidDevice
from remocon_for_adb.domain.entities.remote_command import DirectionKey, ButtonKey, RemoteCommand
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class InvalidCommandException(Exception):
    """無効なコマンド例外"""
    pass


class DeviceNotAvailableException(Exception):
    """デバイス利用不可例外"""
    pass


class RemoteControlUseCase:
    """リモコン操作ユースケース"""

    def __init__(self, device_repository: DeviceRepository):
        """初期化
        
        Args:
            device_repository: デバイスリポジトリ
        """
        self._device_repository = device_repository
        
        # 有効なキーの定義（Android TV必須キーのみ）
        self._valid_direction_keys = ["up", "down", "left", "right"]
        self._valid_button_keys = ["select", "back", "home"]

    def execute_direction_key(self, command: RemoteCommandDTO) -> CommandResultDTO:
        """方向キーの操作を実行
        
        Args:
            command: リモートコマンドDTO
            
        Returns:
            CommandResultDTO: 実行結果
            
        Raises:
            InvalidCommandException: 無効なコマンド
            DeviceNotAvailableException: デバイス利用不可
        """
        start_time = time.time()
        
        try:
            # コマンドバリデーション
            self._validate_direction_key(command.key)
            
            # プライマリデバイス取得
            device = self._get_primary_device()
            
            # リモートコマンド作成
            remote_command = RemoteCommand.from_string(command.key)
            
            # ADBコマンド実行
            success = self._device_repository.execute_command(
                device.device_id,
                remote_command
            )
            
            execution_time = time.time() - start_time
            
            if success:
                return CommandResultDTO(
                    success=True,
                    message=f"Direction key '{command.key}' executed successfully",
                    execution_time=execution_time
                )
            else:
                return CommandResultDTO(
                    success=False,
                    message=f"Failed to execute direction key '{command.key}'",
                    execution_time=execution_time
                )
                
        except (DeviceNotFoundError, DeviceConnectionError) as e:
            execution_time = time.time() - start_time
            return CommandResultDTO(
                success=False,
                message=f"Device connection failed: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            import traceback
            return CommandResultDTO(
                success=False,
                message=f"Unexpected error: {str(e)}\nTraceback: {traceback.format_exc()}",
                execution_time=execution_time
            )

    def execute_button(self, command: RemoteCommandDTO) -> CommandResultDTO:
        """ボタン操作を実行
        
        Args:
            command: リモートコマンドDTO
            
        Returns:
            CommandResultDTO: 実行結果
            
        Raises:
            InvalidCommandException: 無効なコマンド
            DeviceNotAvailableException: デバイス利用不可
        """
        start_time = time.time()
        
        try:
            # コマンドバリデーション
            self._validate_button_key(command.key)
            
            # プライマリデバイス取得
            device = self._get_primary_device()
            
            # リモートコマンド作成
            remote_command = RemoteCommand.from_string(command.key)
            
            # ADBコマンド実行
            success = self._device_repository.execute_command(
                device.device_id,
                remote_command
            )
            
            execution_time = time.time() - start_time
            
            if success:
                return CommandResultDTO(
                    success=True,
                    message=f"Button '{command.key}' executed successfully",
                    execution_time=execution_time
                )
            else:
                return CommandResultDTO(
                    success=False,
                    message=f"Failed to execute button '{command.key}'",
                    execution_time=execution_time
                )
                
        except (DeviceNotFoundError, DeviceConnectionError) as e:
            execution_time = time.time() - start_time
            return CommandResultDTO(
                success=False,
                message=f"Device connection failed: {str(e)}",
                execution_time=execution_time
            )

    def _validate_direction_key(self, key: str) -> None:
        """方向キーの妥当性検証
        
        Args:
            key: キー名
            
        Raises:
            InvalidCommandException: 無効なキー
        """
        if key not in self._valid_direction_keys:
            raise InvalidCommandException(f"Invalid direction key: {key}")

    def _validate_button_key(self, key: str) -> None:
        """ボタンキーの妥当性検証
        
        Args:
            key: キー名
            
        Raises:
            InvalidCommandException: 無効なキー
        """
        if key not in self._valid_button_keys:
            raise InvalidCommandException(f"Invalid button key: {key}")

    def _get_primary_device(self) -> AndroidDevice:
        """プライマリデバイスの取得
        
        Returns:
            AndroidDevice: プライマリデバイス
            
        Raises:
            DeviceNotAvailableException: デバイス利用不可
        """
        devices = self._device_repository.get_connected_devices()
        
        if not devices:
            raise DeviceNotAvailableException("No devices connected")
        
        # 最初の接続デバイスをプライマリとする
        return devices[0]
