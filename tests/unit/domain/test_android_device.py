"""
Android Device エンティティのテスト
"""
import pytest
from datetime import datetime
from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus


class TestAndroidDevice:
    """AndroidDeviceエンティティのテストクラス"""

    def test_create_device_with_valid_data(self):
        """正常なデバイス作成のテスト"""
        # Arrange
        device_id = "192.168.1.100:5555"
        device_name = "Android TV"
        
        # Act
        device = AndroidDevice(
            device_id=device_id,
            device_name=device_name,
            status=DeviceStatus.CONNECTED
        )
        
        # Assert
        assert device.device_id == device_id
        assert device.device_name == device_name
        assert device.status == DeviceStatus.CONNECTED
        assert isinstance(device.last_seen, datetime)

    def test_device_status_enum_values(self):
        """DeviceStatusの列挙値テスト"""
        # Act & Assert
        assert DeviceStatus.CONNECTED.value == "connected"
        assert DeviceStatus.DISCONNECTED.value == "disconnected"
        assert DeviceStatus.UNAUTHORIZED.value == "unauthorized"
        assert DeviceStatus.OFFLINE.value == "offline"

    def test_device_equality(self):
        """デバイスの同一性テスト"""
        # Arrange
        device_id = "192.168.1.100:5555"
        device1 = AndroidDevice(
            device_id=device_id,
            device_name="TV1",
            status=DeviceStatus.CONNECTED
        )
        device2 = AndroidDevice(
            device_id=device_id,
            device_name="TV2",  # 名前が違っても
            status=DeviceStatus.OFFLINE  # ステータスが違っても
        )
        device3 = AndroidDevice(
            device_id="192.168.1.101:5555",  # IDが違う
            device_name="TV1",
            status=DeviceStatus.CONNECTED
        )
        
        # Act & Assert
        assert device1 == device2  # 同じIDなら同じデバイス
        assert device1 != device3  # 違うIDなら違うデバイス

    def test_update_status(self):
        """ステータス更新のテスト"""
        # Arrange
        device = AndroidDevice(
            device_id="test:5555",
            device_name="Test Device",
            status=DeviceStatus.CONNECTED
        )
        old_last_seen = device.last_seen
        
        # Act
        device.update_status(DeviceStatus.OFFLINE)
        
        # Assert
        assert device.status == DeviceStatus.OFFLINE
        assert device.last_seen > old_last_seen

    def test_is_available(self):
        """デバイス利用可能性チェックのテスト"""
        # Arrange & Act & Assert
        connected_device = AndroidDevice(
            device_id="test:5555",
            device_name="Test",
            status=DeviceStatus.CONNECTED
        )
        assert connected_device.is_available() is True
        
        offline_device = AndroidDevice(
            device_id="test:5555",
            device_name="Test",
            status=DeviceStatus.OFFLINE
        )
        assert offline_device.is_available() is False
        
        unauthorized_device = AndroidDevice(
            device_id="test:5555",
            device_name="Test",
            status=DeviceStatus.UNAUTHORIZED
        )
        assert unauthorized_device.is_available() is False

    def test_device_id_validation(self):
        """デバイスID検証のテスト"""
        # Valid cases
        valid_ids = [
            "192.168.1.100:5555",
            "localhost:5555",
            "emulator-5554",
            "SERIAL123456"
        ]
        
        for device_id in valid_ids:
            device = AndroidDevice(
                device_id=device_id,
                device_name="Test",
                status=DeviceStatus.CONNECTED
            )
            assert device.device_id == device_id

        # Invalid cases
        invalid_ids = ["", "   ", None]
        
        for device_id in invalid_ids:
            with pytest.raises(ValueError):
                AndroidDevice(
                    device_id=device_id,
                    device_name="Test",
                    status=DeviceStatus.CONNECTED
                )
