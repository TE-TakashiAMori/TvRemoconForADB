"""
ADB Gateway のテスト
"""
import pytest
from unittest.mock import Mock, patch, call
from remocon_for_adb.infrastructure.gateways.adb_gateway import (
    AdbGateway, 
    AdbResult, 
    AdbNotInstalledException,
    DeviceNotConnectedException,
    AdbCommandTimeoutException
)


class TestAdbGateway:
    """AdbGatewayのテストクラス"""

    def setup_method(self):
        """各テストの前処理"""
        self.adb_gateway = AdbGateway()

    @patch('subprocess.run')
    def test_is_device_connected_success(self, mock_run):
        """デバイス接続確認の成功テスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\n192.168.1.100:5555\tdevice\n"
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.is_device_connected()
        
        # Assert
        assert result is True
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_is_device_connected_no_devices(self, mock_run):
        """デバイス未接続時のテスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\n\n"
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.is_device_connected()
        
        # Assert
        assert result is False

    @patch('subprocess.run')
    def test_get_connected_devices(self, mock_run):
        """接続デバイス一覧取得のテスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = (
            "List of devices attached\n"
            "192.168.1.100:5555\tdevice\n"
            "emulator-5554\tdevice\n"
        )
        mock_run.return_value.stderr = ""
        
        # Act
        devices = self.adb_gateway.get_connected_devices()
        
        # Assert
        assert len(devices) == 2
        assert "192.168.1.100:5555" in devices
        assert "emulator-5554" in devices

    @patch('subprocess.run')
    def test_execute_input_command_success(self, mock_run):
        """入力コマンド実行の成功テスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.execute_input_command("KEYCODE_DPAD_UP")
        
        # Assert
        assert result.success is True
        assert result.return_code == 0
        assert "KEYCODE_DPAD_UP" in result.command

    @patch('subprocess.run')
    def test_capture_screenshot_success(self, mock_run):
        """スクリーンショット取得の成功テスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.capture_screenshot("/sdcard/test.png")
        
        # Assert
        assert result.success is True
        assert "screencap" in result.command

    @patch('subprocess.run')
    def test_pull_file_success(self, mock_run):
        """ファイルプルの成功テスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.pull_file("/sdcard/test.png", "./test.png")
        
        # Assert
        assert result.success is True
        assert "pull" in result.command

    @patch('subprocess.run')
    def test_remove_file_success(self, mock_run):
        """ファイル削除の成功テスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.remove_file("/sdcard/test.png")
        
        # Assert
        assert result.success is True
        assert "rm" in result.command

    @patch('subprocess.run')
    def test_adb_command_failure(self, mock_run):
        """ADBコマンド失敗時のテスト"""
        # Arrange
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "error: device not found"
        
        # Act
        result = self.adb_gateway.execute_input_command("KEYCODE_DPAD_UP")
        
        # Assert
        assert result.success is False
        assert result.return_code == 1
        assert "device not found" in result.stderr

    @patch('subprocess.run')
    def test_device_not_connected_exception(self, mock_run):
        """デバイス未接続例外のテスト"""
        # Arrange
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "error: no devices/emulators found"
        
        # Act & Assert
        with pytest.raises(DeviceNotConnectedException):
            self.adb_gateway.execute_input_command("KEYCODE_DPAD_UP")

    @patch('remocon_for_adb.infrastructure.gateways.adb_gateway.subprocess.run')
    def test_adb_not_installed_exception(self, mock_run):
        """ADB未インストール例外のテスト"""
        # Arrange
        mock_run.side_effect = FileNotFoundError("adb command not found")
        
        # Act & Assert
        with pytest.raises(AdbNotInstalledException):
            self.adb_gateway.is_device_connected()

    @patch('subprocess.run')
    def test_command_timeout_exception(self, mock_run):
        """コマンドタイムアウト例外のテスト"""
        # Arrange
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("adb", 30)
        
        # Act & Assert
        with pytest.raises(AdbCommandTimeoutException):
            self.adb_gateway.execute_input_command("KEYCODE_DPAD_UP")

    def test_adb_result_dataclass(self):
        """AdbResultデータクラスのテスト"""
        # Arrange & Act
        result = AdbResult(
            success=True,
            stdout="output",
            stderr="",
            return_code=0,
            execution_time=1.23,
            command="adb shell input keyevent KEYCODE_DPAD_UP"
        )
        
        # Assert
        assert result.success is True
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.return_code == 0
        assert result.execution_time == 1.23
        assert "KEYCODE_DPAD_UP" in result.command

    @patch('subprocess.run')
    def test_execute_shell_command(self, mock_run):
        """シェルコマンド実行のテスト"""
        # Arrange
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test output"
        mock_run.return_value.stderr = ""
        
        # Act
        result = self.adb_gateway.execute_shell_command("echo 'test'")
        
        # Assert
        assert result.success is True
        assert "test output" in result.stdout
        mock_run.assert_called_once()

    def test_custom_adb_path(self):
        """カスタムADBパスの設定テスト"""
        # Arrange & Act
        gateway = AdbGateway(adb_path="/custom/path/adb")
        
        # Assert
        assert gateway.adb_path == "/custom/path/adb"

    @patch('subprocess.run')
    def test_retry_mechanism(self, mock_run):
        """リトライ機構のテスト"""
        # Arrange
        mock_run.side_effect = [
            # 1回目失敗
            Mock(returncode=1, stderr="error: device offline"),
            # 2回目成功
            Mock(returncode=0, stdout="", stderr="")
        ]
        
        # Act
        result = self.adb_gateway.execute_input_command("KEYCODE_DPAD_UP")
        
        # Assert
        assert result.success is True
        assert mock_run.call_count == 2
