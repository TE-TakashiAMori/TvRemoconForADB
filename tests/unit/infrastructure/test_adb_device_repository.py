"""AdbDeviceRepositoryのテスト

AdbGatewayを使用したDeviceRepositoryの具象実装をテストします。
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from typing import List

from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.domain.entities.remote_command import RemoteCommand, DirectionKey
from remocon_for_adb.domain.repositories.device_repository import DeviceConnectionError
from remocon_for_adb.infrastructure.gateways.adb_gateway import (
    AdbGateway,
    AdbResult,
    DeviceNotConnectedException,
)
from remocon_for_adb.infrastructure.repositories.adb_device_repository import (
    AdbDeviceRepository,
)


class TestAdbDeviceRepository:
    """AdbDeviceRepositoryのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の setup"""
        self.mock_adb_gateway = Mock(spec=AdbGateway)
        self.repository = AdbDeviceRepository(self.mock_adb_gateway)

    def test_init_repository(self):
        """リポジトリの初期化をテスト"""
        repository = AdbDeviceRepository(self.mock_adb_gateway)
        assert repository._adb_gateway == self.mock_adb_gateway
        assert repository._devices == []

    def test_get_connected_devices_success(self):
        """接続デバイス取得の成功ケースをテスト"""
        # Arrange
        device_ids = ["device1", "device2"]
        self.mock_adb_gateway.get_connected_devices.return_value = device_ids

        # Act
        devices = self.repository.get_connected_devices()

        # Assert
        assert len(devices) == 2
        assert devices[0].device_id == "device1"
        assert devices[0].device_name == "Android Device (device1)"
        assert devices[0].status == DeviceStatus.CONNECTED
        assert devices[1].device_id == "device2"
        assert devices[1].device_name == "Android Device (device2)"
        assert devices[1].status == DeviceStatus.CONNECTED
        
        # 内部リストも更新されていることを確認
        assert len(self.repository._devices) == 2

    def test_get_connected_devices_empty(self):
        """接続デバイスが空の場合をテスト"""
        # Arrange
        self.mock_adb_gateway.get_connected_devices.return_value = []

        # Act
        devices = self.repository.get_connected_devices()

        # Assert
        assert devices == []
        assert self.repository._devices == []

    def test_get_connected_devices_gateway_error(self):
        """AdbGatewayでエラーが発生した場合をテスト"""
        # Arrange
        self.mock_adb_gateway.get_connected_devices.side_effect = DeviceNotConnectedException(
            "ADB接続エラー"
        )

        # Act & Assert
        with pytest.raises(DeviceConnectionError) as exc_info:
            self.repository.get_connected_devices()
        
        assert "デバイス一覧の取得に失敗しました: ADB接続エラー" in str(exc_info.value)

    def test_get_device_by_id_found_in_cache(self):
        """内部キャッシュからデバイスを取得するテスト"""
        # Arrange
        device = AndroidDevice(
            device_id="device1",
            device_name="Test Device",
            status=DeviceStatus.CONNECTED,
            last_seen=datetime.now(),
        )
        self.repository._devices = [device]

        # Act
        result = self.repository.get_device_by_id("device1")

        # Assert
        assert result == device
        # get_connected_devicesは呼ばれないことを確認
        self.mock_adb_gateway.get_connected_devices.assert_not_called()

    def test_get_device_by_id_not_found_in_cache_search_again(self):
        """キャッシュになく、再検索で見つかる場合をテスト"""
        # Arrange
        self.repository._devices = []
        self.mock_adb_gateway.get_connected_devices.return_value = ["device1"]

        # Act
        result = self.repository.get_device_by_id("device1")

        # Assert
        assert result is not None
        assert result.device_id == "device1"
        self.mock_adb_gateway.get_connected_devices.assert_called_once()

    def test_get_device_by_id_not_found(self):
        """デバイスが見つからない場合をテスト"""
        # Arrange
        self.repository._devices = []
        self.mock_adb_gateway.get_connected_devices.return_value = ["device2"]

        # Act
        result = self.repository.get_device_by_id("device1")

        # Assert
        assert result is None

    def test_get_device_by_id_search_error(self):
        """再検索でエラーが発生した場合をテスト"""
        # Arrange
        self.repository._devices = []
        self.mock_adb_gateway.get_connected_devices.side_effect = DeviceNotConnectedException(
            "接続エラー"
        )

        # Act
        result = self.repository.get_device_by_id("device1")

        # Assert
        assert result is None

    def test_is_device_available_true(self):
        """デバイスが利用可能な場合をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = True

        # Act
        result = self.repository.is_device_available("device1")

        # Assert
        assert result is True
        self.mock_adb_gateway.is_device_connected.assert_called_once_with("device1")

    def test_is_device_available_false(self):
        """デバイスが利用不可能な場合をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = False

        # Act
        result = self.repository.is_device_available("device1")

        # Assert
        assert result is False

    def test_is_device_available_gateway_error(self):
        """is_device_connectedでエラーが発生した場合をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.side_effect = DeviceNotConnectedException(
            "接続エラー"
        )

        # Act
        result = self.repository.is_device_available("device1")

        # Assert
        assert result is False

    def test_update_device_status(self):
        """デバイスステータス更新をテスト"""
        # Arrange
        device = AndroidDevice(
            device_id="device1",
            device_name="Test Device",
            status=DeviceStatus.CONNECTED,
            last_seen=datetime.now(),
        )
        self.repository._devices = [device]

        # Act
        self.repository.update_device_status("device1", DeviceStatus.DISCONNECTED)

        # Assert
        assert device.status == DeviceStatus.DISCONNECTED

    def test_update_device_status_device_not_found(self):
        """存在しないデバイスのステータス更新をテスト"""
        # Arrange
        self.repository._devices = []

        # Act & Assert (例外が発生しないことを確認)
        self.repository.update_device_status("device1", DeviceStatus.DISCONNECTED)

    def test_refresh_device_list_success(self):
        """デバイス一覧の再取得成功をテスト"""
        # Arrange
        self.mock_adb_gateway.get_connected_devices.return_value = ["device1"]

        # Act
        self.repository.refresh_device_list()

        # Assert
        assert len(self.repository._devices) == 1
        assert self.repository._devices[0].device_id == "device1"

    def test_refresh_device_list_error(self):
        """デバイス一覧の再取得エラーをテスト"""
        # Arrange
        self.repository._devices = [
            AndroidDevice(
                device_id="device1",
                device_name="Test Device",
                status=DeviceStatus.CONNECTED,
                last_seen=datetime.now(),
            )
        ]
        self.mock_adb_gateway.get_connected_devices.side_effect = DeviceNotConnectedException(
            "接続エラー"
        )

        # Act
        self.repository.refresh_device_list()

        # Assert
        assert self.repository._devices == []

    def test_execute_command_success(self):
        """コマンド実行成功をテスト"""
        # Arrange
        command = RemoteCommand.create_direction_command(DirectionKey.UP)
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.execute_input_command.return_value = AdbResult(
            success=True,
            stdout="",
            stderr="",
            return_code=0,
            execution_time=0.1,
            command="input keyevent KEYCODE_DPAD_UP",
        )

        # Act
        result = self.repository.execute_command("device1", command)

        # Assert
        assert result is True
        self.mock_adb_gateway.is_device_connected.assert_called_once_with("device1")
        self.mock_adb_gateway.execute_input_command.assert_called_once_with(
            "device1", "input keyevent KEYCODE_DPAD_UP"
        )

    def test_execute_command_device_not_available(self):
        """デバイスが利用不可能な場合のコマンド実行をテスト"""
        # Arrange
        command = RemoteCommand.create_direction_command(DirectionKey.UP)
        self.mock_adb_gateway.is_device_connected.return_value = False

        # Act & Assert
        with pytest.raises(DeviceConnectionError) as exc_info:
            self.repository.execute_command("device1", command)
        
        assert "デバイス device1 は利用できません" in str(exc_info.value)

    def test_execute_command_gateway_error(self):
        """AdbGatewayでエラーが発生した場合のコマンド実行をテスト"""
        # Arrange
        command = RemoteCommand.create_direction_command(DirectionKey.UP)
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.execute_input_command.side_effect = DeviceNotConnectedException(
            "コマンド実行エラー"
        )

        # Act & Assert
        with pytest.raises(DeviceConnectionError) as exc_info:
            self.repository.execute_command("device1", command)
        
        assert "コマンド実行に失敗しました: コマンド実行エラー" in str(exc_info.value)

    def test_execute_command_failure(self):
        """コマンド実行が失敗した場合をテスト"""
        # Arrange
        command = RemoteCommand.create_direction_command(DirectionKey.UP)
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.execute_input_command.return_value = AdbResult(
            success=False,
            stdout="",
            stderr="失敗",
            return_code=1,
            execution_time=0.1,
            command="input keyevent KEYCODE_DPAD_UP",
        )

        # Act
        result = self.repository.execute_command("device1", command)

        # Assert
        assert result is False

    def test_capture_screenshot_success(self):
        """スクリーンショット撮影成功をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.capture_screenshot.return_value = AdbResult(
            success=True,
            stdout="",
            stderr="",
            return_code=0,
            execution_time=0.1,
            command="screencap -p /sdcard/screenshot.png",
        )

        # Act
        result = self.repository.capture_screenshot("device1", "/tmp/screenshot.png")

        # Assert
        assert result is True
        self.mock_adb_gateway.is_device_connected.assert_called_once_with("device1")
        self.mock_adb_gateway.capture_screenshot.assert_called_once_with(
            "device1", "/tmp/screenshot.png"
        )

    def test_capture_screenshot_device_not_available(self):
        """デバイスが利用不可能な場合のスクリーンショット撮影をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = False

        # Act & Assert
        with pytest.raises(DeviceConnectionError) as exc_info:
            self.repository.capture_screenshot("device1", "/tmp/screenshot.png")
        
        assert "デバイス device1 は利用できません" in str(exc_info.value)

    def test_capture_screenshot_gateway_error(self):
        """AdbGatewayでエラーが発生した場合のスクリーンショット撮影をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.capture_screenshot.side_effect = DeviceNotConnectedException(
            "撮影エラー"
        )

        # Act & Assert
        with pytest.raises(DeviceConnectionError) as exc_info:
            self.repository.capture_screenshot("device1", "/tmp/screenshot.png")
        
        assert "スクリーンショット撮影に失敗しました: 撮影エラー" in str(exc_info.value)

    def test_capture_screenshot_failure(self):
        """スクリーンショット撮影が失敗した場合をテスト"""
        # Arrange
        self.mock_adb_gateway.is_device_connected.return_value = True
        self.mock_adb_gateway.capture_screenshot.return_value = AdbResult(
            success=False,
            stdout="",
            stderr="撮影失敗",
            return_code=1,
            execution_time=0.1,
            command="screencap -p /sdcard/screenshot.png",
        )

        # Act
        result = self.repository.capture_screenshot("device1", "/tmp/screenshot.png")

        # Assert
        assert result is False
