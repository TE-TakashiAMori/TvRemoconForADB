"""
Device Repository Interface のテスト
"""
import pytest
from abc import ABC
from typing import List, Optional
from unittest.mock import Mock
from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class TestDeviceRepository:
    """DeviceRepositoryインターフェースのテストクラス"""

    def setup_method(self):
        """各テストの前処理"""
        # モック実装を作成
        self.mock_repository = Mock(spec=DeviceRepository)

    def test_device_repository_is_abstract(self):
        """DeviceRepositoryが抽象クラスであることのテスト"""
        # Act & Assert
        assert issubclass(DeviceRepository, ABC)

    def test_get_connected_devices_interface(self):
        """接続デバイス取得インターフェースのテスト"""
        # Arrange
        expected_devices = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED),
            AndroidDevice("device2", "TV2", DeviceStatus.CONNECTED)
        ]
        self.mock_repository.get_connected_devices.return_value = expected_devices
        
        # Act
        result = self.mock_repository.get_connected_devices()
        
        # Assert
        assert result == expected_devices
        self.mock_repository.get_connected_devices.assert_called_once()

    def test_get_device_by_id_interface(self):
        """ID指定デバイス取得インターフェースのテスト"""
        # Arrange
        device_id = "test_device"
        expected_device = AndroidDevice(device_id, "Test TV", DeviceStatus.CONNECTED)
        self.mock_repository.get_device_by_id.return_value = expected_device
        
        # Act
        result = self.mock_repository.get_device_by_id(device_id)
        
        # Assert
        assert result == expected_device
        self.mock_repository.get_device_by_id.assert_called_once_with(device_id)

    def test_get_device_by_id_not_found(self):
        """存在しないデバイス取得のテスト"""
        # Arrange
        self.mock_repository.get_device_by_id.side_effect = DeviceNotFoundError("Device not found")
        
        # Act & Assert
        with pytest.raises(DeviceNotFoundError):
            self.mock_repository.get_device_by_id("nonexistent")

    def test_is_device_available_interface(self):
        """デバイス利用可能性チェックインターフェースのテスト"""
        # Arrange
        device_id = "test_device"
        self.mock_repository.is_device_available.return_value = True
        
        # Act
        result = self.mock_repository.is_device_available(device_id)
        
        # Assert
        assert result is True
        self.mock_repository.is_device_available.assert_called_once_with(device_id)

    def test_update_device_status_interface(self):
        """デバイスステータス更新インターフェースのテスト"""
        # Arrange
        device_id = "test_device"
        new_status = DeviceStatus.OFFLINE
        
        # Act
        self.mock_repository.update_device_status(device_id, new_status)
        
        # Assert
        self.mock_repository.update_device_status.assert_called_once_with(device_id, new_status)

    def test_refresh_device_list_interface(self):
        """デバイスリスト更新インターフェースのテスト"""
        # Act
        self.mock_repository.refresh_device_list()
        
        # Assert
        self.mock_repository.refresh_device_list.assert_called_once()

    def test_device_connection_error(self):
        """デバイス接続エラーのテスト"""
        # Arrange
        self.mock_repository.get_connected_devices.side_effect = DeviceConnectionError("Connection failed")
        
        # Act & Assert
        with pytest.raises(DeviceConnectionError):
            self.mock_repository.get_connected_devices()

    def test_execute_command_interface(self):
        """コマンド実行インターフェースのテスト"""
        # Arrange
        device_id = "test_device"
        command = "input keyevent KEYCODE_DPAD_UP"
        expected_result = True
        self.mock_repository.execute_command.return_value = expected_result
        
        # Act
        result = self.mock_repository.execute_command(device_id, command)
        
        # Assert
        assert result == expected_result
        self.mock_repository.execute_command.assert_called_once_with(device_id, command)

    def test_capture_screenshot_interface(self):
        """スクリーンショット取得インターフェースのテスト"""
        # Arrange
        device_id = "test_device"
        local_path = "/tmp/screenshot.png"
        expected_result = True
        self.mock_repository.capture_screenshot.return_value = expected_result
        
        # Act
        result = self.mock_repository.capture_screenshot(device_id, local_path)
        
        # Assert
        assert result == expected_result
        self.mock_repository.capture_screenshot.assert_called_once_with(device_id, local_path)
