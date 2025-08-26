"""
Screenshot Use Case のテスト
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
from pathlib import Path
from remocon_for_adb.application.use_cases.screenshot_use_case import (
    ScreenshotUseCase,
    ScreenshotFailedException,
    FileOperationException
)
from remocon_for_adb.application.dtos.command_dto import ScreenshotCommandDTO, ScreenshotResultDTO
from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class TestScreenshotUseCase:
    """ScreenshotUseCaseのテストクラス"""

    def setup_method(self):
        """各テストの前処理"""
        self.mock_device_repo = Mock(spec=DeviceRepository)
        self.use_case = ScreenshotUseCase(self.mock_device_repo)

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.path.getsize')
    def test_capture_screenshot_success_with_filename(self, mock_getsize, mock_makedirs, mock_exists):
        """ファイル名指定でのスクリーンショット取得成功テスト"""
        # Arrange
        command_dto = ScreenshotCommandDTO(filename="test_screenshot.png")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.capture_screenshot.return_value = True
        mock_exists.return_value = True
        mock_getsize.return_value = 1024576
        
        # Act
        result = self.use_case.capture_screenshot(command_dto)
        
        # Assert
        assert result.success is True
        assert "test_screenshot.png" in result.filepath
        assert result.filesize == 1024576
        assert "successfully" in result.message.lower()
        self.mock_device_repo.capture_screenshot.assert_called_once()

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.path.getsize')
    def test_capture_screenshot_success_auto_filename(self, mock_getsize, mock_makedirs, mock_exists):
        """自動ファイル名でのスクリーンショット取得成功テスト"""
        # Arrange
        command_dto = ScreenshotCommandDTO()  # ファイル名なし
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.capture_screenshot.return_value = True
        mock_exists.return_value = True
        mock_getsize.return_value = 512000
        
        # Act
        with patch('remocon_for_adb.application.use_cases.screenshot_use_case.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 25, 10, 30, 45)
            mock_datetime.strftime = datetime.strftime
            result = self.use_case.capture_screenshot(command_dto)
        
        # Assert
        assert result.success is True
        assert "screenshot_20250825_103045.png" in result.filepath
        assert result.filesize == 512000

    def test_capture_screenshot_no_device(self):
        """デバイス未接続時のスクリーンショット取得テスト"""
        # Arrange
        command_dto = ScreenshotCommandDTO(filename="test.png")
        self.mock_device_repo.get_connected_devices.return_value = []
        
        # Act
        result = self.use_case.capture_screenshot(command_dto)
        
        # Assert
        assert result.success is False
        assert "no devices connected" in result.message.lower()

    def test_capture_screenshot_device_error(self):
        """デバイスエラー時のスクリーンショット取得テスト"""
        # Arrange
        command_dto = ScreenshotCommandDTO(filename="test.png")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.capture_screenshot.side_effect = DeviceConnectionError("Connection failed")
        
        # Act
        result = self.use_case.capture_screenshot(command_dto)
        
        # Assert
        assert result.success is False
        assert "connection failed" in result.message.lower()

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_capture_screenshot_file_not_created(self, mock_makedirs, mock_exists):
        """スクリーンショットファイル作成失敗のテスト"""
        # Arrange
        command_dto = ScreenshotCommandDTO(filename="test.png")
        self.mock_device_repo.get_connected_devices.return_value = [
            AndroidDevice("device1", "TV1", DeviceStatus.CONNECTED)
        ]
        self.mock_device_repo.capture_screenshot.return_value = True
        mock_exists.return_value = False  # ファイルが作成されない
        
        # Act
        result = self.use_case.capture_screenshot(command_dto)
        
        # Assert
        assert result.success is False
        assert "failed to create" in result.message.lower()

    def test_generate_filename(self):
        """ファイル名自動生成のテスト"""
        # Act
        with patch('remocon_for_adb.application.use_cases.screenshot_use_case.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 25, 14, 15, 30)
            mock_datetime.strftime = datetime.strftime
            filename = self.use_case._generate_filename()
        
        # Assert
        assert filename == "screenshot_20250825_141530.png"

    @patch('pathlib.Path.home')
    def test_get_screenshot_directory(self, mock_home):
        """スクリーンショット保存ディレクトリ取得のテスト"""
        # Arrange
        mock_home.return_value = Path("/home/user")
        
        # Act
        directory = self.use_case._get_screenshot_directory()
        
        # Assert
        assert str(directory) == "/home/user/remocon_screenshots"

    def test_create_filepath(self):
        """ファイルパス作成のテスト"""
        # Act
        with patch.object(self.use_case, '_get_screenshot_directory') as mock_get_dir:
            mock_get_dir.return_value = Path("/home/user/screenshots")
            filepath = self.use_case._create_filepath("test.png")
        
        # Assert
        assert str(filepath) == "/home/user/screenshots/test.png"

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_directory_exists_create_new(self, mock_exists, mock_makedirs):
        """ディレクトリ作成のテスト"""
        # Arrange
        mock_exists.return_value = False
        directory = Path("/new/directory")
        
        # Act
        self.use_case._ensure_directory_exists(directory)
        
        # Assert
        mock_makedirs.assert_called_once_with(directory, exist_ok=True)

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_directory_exists_already_exists(self, mock_exists, mock_makedirs):
        """既存ディレクトリのテスト"""
        # Arrange
        mock_exists.return_value = True
        directory = Path("/existing/directory")
        
        # Act
        self.use_case._ensure_directory_exists(directory)
        
        # Assert
        mock_makedirs.assert_not_called()

    @patch('os.path.getsize')
    def test_get_file_info_success(self, mock_getsize):
        """ファイル情報取得成功のテスト"""
        # Arrange
        mock_getsize.return_value = 2048000
        filepath = Path("/path/to/file.png")
        
        # Act
        size = self.use_case._get_file_info(filepath)
        
        # Assert
        assert size == 2048000

    @patch('os.path.getsize')
    def test_get_file_info_file_not_found(self, mock_getsize):
        """ファイル情報取得失敗のテスト"""
        # Arrange
        mock_getsize.side_effect = FileNotFoundError()
        filepath = Path("/nonexistent/file.png")
        
        # Act & Assert
        with pytest.raises(FileOperationException):
            self.use_case._get_file_info(filepath)
