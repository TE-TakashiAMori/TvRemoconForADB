"""
Remote Control Use Case のテスト
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from remocon_for_adb.application.use_cases.remote_control_use_case import (
    RemoteControlUseCase,
    InvalidCommandException,
    DeviceNotAvailableException
)
from remocon_for_adb.application.dtos.command_dto import RemoteCommandDTO, CommandResultDTO
from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class TestRemoteControlUseCase:
    """RemoteControlUseCaseのテストクラス"""

    def setup_method(self):
        """各テストの前処理"""
        self.mock_device_repo = Mock(spec=DeviceRepository)
        self.use_case = RemoteControlUseCase(self.mock_device_repo)

    def test_execute_direction_command_success(self):
        """方向キーコマンド実行成功のテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="direction", key="up")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.execute_command.return_value = True
        
        # Act
        result = self.use_case.execute_direction_key(command_dto)
        
        # Assert
        assert result.success is True
        assert "successfully" in result.message.lower()
        assert result.execution_time > 0
        self.mock_device_repo.execute_command.assert_called_once()

    def test_execute_direction_command_invalid_key(self):
        """無効な方向キーコマンドのテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="direction", key="invalid")
        
        # Act & Assert
        with pytest.raises(InvalidCommandException):
            self.use_case.execute_direction_key(command_dto)

    def test_execute_button_command_success(self):
        """ボタンコマンド実行成功のテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="button", key="home")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.execute_command.return_value = True
        
        # Act
        result = self.use_case.execute_button(command_dto)
        
        # Assert
        assert result.success is True
        assert "successfully" in result.message.lower()
        self.mock_device_repo.execute_command.assert_called_once()

    def test_execute_button_command_invalid_key(self):
        """無効なボタンコマンドのテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="button", key="invalid")
        
        # Act & Assert
        with pytest.raises(InvalidCommandException):
            self.use_case.execute_button(command_dto)

    def test_execute_command_no_device_connected(self):
        """デバイス未接続時のテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="direction", key="up")
        self.mock_device_repo.get_connected_devices.return_value = []
        
        # Act & Assert
        with pytest.raises(DeviceNotAvailableException):
            self.use_case.execute_direction_key(command_dto)

    def test_execute_command_device_connection_error(self):
        """デバイス接続エラーのテスト"""
        # Arrange
        command_dto = RemoteCommandDTO(command_type="direction", key="up")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.execute_command.side_effect = DeviceConnectionError("Connection failed")
        
        # Act
        result = self.use_case.execute_direction_key(command_dto)
        
        # Assert
        assert result.success is False
        assert "connection failed" in result.message.lower()

    def test_validate_direction_key_valid_keys(self):
        """有効な方向キーの検証テスト"""
        # Arrange
        valid_keys = ["up", "down", "left", "right"]
        
        # Act & Assert
        for key in valid_keys:
            # 例外が発生しないことを確認
            self.use_case._validate_direction_key(key)

    def test_validate_direction_key_invalid_key(self):
        """無効な方向キーの検証テスト"""
        # Act & Assert
        with pytest.raises(InvalidCommandException):
            self.use_case._validate_direction_key("invalid")

    def test_validate_button_key_valid_keys(self):
        """有効なボタンキーの検証テスト"""
        # Arrange
        valid_keys = ["select", "back", "home"]
        
        # Act & Assert
        for key in valid_keys:
            # 例外が発生しないことを確認
            self.use_case._validate_button_key(key)

    def test_validate_button_key_invalid_key(self):
        """無効なボタンキーの検証テスト"""
        # Act & Assert
        with pytest.raises(InvalidCommandException):
            self.use_case._validate_button_key("invalid")

    def test_get_primary_device_success(self):
        """プライマリデバイス取得成功のテスト"""
        # Arrange
        expected_device = AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        self.mock_device_repo.get_connected_devices.return_value = [expected_device]
        
        # Act
        result = self.use_case._get_primary_device()
        
        # Assert
        assert result == expected_device

    def test_get_primary_device_no_devices(self):
        """プライマリデバイス取得失敗（デバイスなし）のテスト"""
        # Arrange
        self.mock_device_repo.get_connected_devices.return_value = []
        
        # Act & Assert
        with pytest.raises(DeviceNotAvailableException):
            self.use_case._get_primary_device()

    @patch('time.time')
    def test_execution_time_measurement(self, mock_time):
        """実行時間測定のテスト"""
        # Arrange
        mock_time.side_effect = [100.0, 100.5]  # 0.5秒の実行時間
        command_dto = RemoteCommandDTO(command_type="direction", key="up")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.execute_command.return_value = True
        
        # Act
        result = self.use_case.execute_direction_key(command_dto)
        
        # Assert
        assert result.execution_time == 0.5
