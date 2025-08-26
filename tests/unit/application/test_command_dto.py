"""
Application DTOs のテスト
"""
import pytest
from datetime import datetime
from remocon_for_adb.application.dtos.command_dto import (
    RemoteCommandDTO,
    CommandResultDTO,
    ScreenshotCommandDTO,
    ScreenshotResultDTO
)


class TestRemoteCommandDTO:
    """RemoteCommandDTOのテストクラス"""

    def test_create_remote_command_dto(self):
        """RemoteCommandDTO作成のテスト"""
        # Arrange & Act
        dto = RemoteCommandDTO(
            command_type="direction",
            key="up"
        )
        
        # Assert
        assert dto.command_type == "direction"
        assert dto.key == "up"
        assert isinstance(dto.timestamp, datetime)

    def test_remote_command_dto_with_custom_timestamp(self):
        """カスタムタイムスタンプでのDTO作成テスト"""
        # Arrange
        custom_time = datetime(2025, 8, 25, 10, 30, 45)
        
        # Act
        dto = RemoteCommandDTO(
            command_type="button",
            key="home",
            timestamp=custom_time
        )
        
        # Assert
        assert dto.timestamp == custom_time

    def test_remote_command_dto_equality(self):
        """RemoteCommandDTOの同一性テスト"""
        # Arrange
        dto1 = RemoteCommandDTO("direction", "up")
        dto2 = RemoteCommandDTO("direction", "up")
        dto3 = RemoteCommandDTO("direction", "down")
        
        # Act & Assert
        assert dto1 == dto2
        assert dto1 != dto3


class TestCommandResultDTO:
    """CommandResultDTOのテストクラス"""

    def test_create_success_result(self):
        """成功結果DTOの作成テスト"""
        # Arrange & Act
        result = CommandResultDTO(
            success=True,
            message="Command executed successfully",
            execution_time=0.234
        )
        
        # Assert
        assert result.success is True
        assert result.message == "Command executed successfully"
        assert result.execution_time == 0.234
        assert isinstance(result.timestamp, datetime)

    def test_create_failure_result(self):
        """失敗結果DTOの作成テスト"""
        # Arrange & Act
        result = CommandResultDTO(
            success=False,
            message="Device not connected",
            execution_time=0.0
        )
        
        # Assert
        assert result.success is False
        assert result.message == "Device not connected"


class TestScreenshotCommandDTO:
    """ScreenshotCommandDTOのテストクラス"""

    def test_create_screenshot_command_with_filename(self):
        """ファイル名指定でのスクリーンショットコマンドDTO作成テスト"""
        # Arrange & Act
        dto = ScreenshotCommandDTO(filename="test_screenshot.png")
        
        # Assert
        assert dto.filename == "test_screenshot.png"
        assert isinstance(dto.timestamp, datetime)

    def test_create_screenshot_command_without_filename(self):
        """ファイル名なしでのスクリーンショットコマンドDTO作成テスト"""
        # Arrange & Act
        dto = ScreenshotCommandDTO()
        
        # Assert
        assert dto.filename is None
        assert isinstance(dto.timestamp, datetime)


class TestScreenshotResultDTO:
    """ScreenshotResultDTOのテストクラス"""

    def test_create_screenshot_success_result(self):
        """スクリーンショット成功結果DTOの作成テスト"""
        # Arrange & Act
        result = ScreenshotResultDTO(
            success=True,
            filepath="/path/to/screenshot.png",
            filesize=1024576,
            message="Screenshot captured successfully",
            execution_time=2.34
        )
        
        # Assert
        assert result.success is True
        assert result.filepath == "/path/to/screenshot.png"
        assert result.filesize == 1024576
        assert result.message == "Screenshot captured successfully"
        assert result.execution_time == 2.34
        assert isinstance(result.timestamp, datetime)

    def test_create_screenshot_failure_result(self):
        """スクリーンショット失敗結果DTOの作成テスト"""
        # Arrange & Act
        result = ScreenshotResultDTO(
            success=False,
            filepath="",
            filesize=0,
            message="Failed to capture screenshot",
            execution_time=0.0
        )
        
        # Assert
        assert result.success is False
        assert result.filepath == ""
        assert result.filesize == 0
