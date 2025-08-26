"""
Screenshot Use Case
スクリーンショット取得機能のユースケース実装
"""
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from remocon_for_adb.application.dtos.command_dto import ScreenshotCommandDTO, ScreenshotResultDTO
from remocon_for_adb.domain.entities.android_device import AndroidDevice
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class ScreenshotFailedException(Exception):
    """スクリーンショット取得失敗例外"""
    pass


class FileOperationException(Exception):
    """ファイル操作失敗例外"""
    pass


class ScreenshotUseCase:
    """スクリーンショット取得ユースケース"""

    def __init__(self, device_repository: DeviceRepository):
        """初期化
        
        Args:
            device_repository: デバイスリポジトリ
        """
        self._device_repository = device_repository

    def capture_screenshot(self, command: ScreenshotCommandDTO) -> ScreenshotResultDTO:
        """スクリーンショットを取得して保存
        
        Args:
            command: スクリーンショットコマンドDTO
            
        Returns:
            ScreenshotResultDTO: 実行結果
        """
        start_time = time.time()
        
        try:
            # プライマリデバイス取得
            device = self._get_primary_device()
            
            # ファイル名生成
            filename = command.filename if command.filename else self._generate_filename()
            
            # ファイルパス作成
            filepath = self._create_filepath(filename)
            
            # ディレクトリ確保
            self._ensure_directory_exists(filepath.parent)
            
            # スクリーンショット取得
            success = self._device_repository.capture_screenshot(
                device.device_id,
                str(filepath)
            )
            
            execution_time = time.time() - start_time
            
            if not success:
                return ScreenshotResultDTO(
                    success=False,
                    filepath="",
                    filesize=0,
                    message="Failed to capture screenshot",
                    execution_time=execution_time
                )
            
            # ファイル作成確認
            if not os.path.exists(filepath):
                return ScreenshotResultDTO(
                    success=False,
                    filepath="",
                    filesize=0,
                    message="Failed to create screenshot file",
                    execution_time=execution_time
                )
            
            # ファイル情報取得
            filesize = self._get_file_info(filepath)
            
            return ScreenshotResultDTO(
                success=True,
                filepath=str(filepath),
                filesize=filesize,
                message=f"Screenshot saved successfully: {filename}",
                execution_time=execution_time
            )
            
        except (DeviceNotFoundError, DeviceConnectionError) as e:
            execution_time = time.time() - start_time
            return ScreenshotResultDTO(
                success=False,
                filepath="",
                filesize=0,
                message=f"Device connection failed: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ScreenshotResultDTO(
                success=False,
                filepath="",
                filesize=0,
                message=f"Unexpected error: {str(e)}",
                execution_time=execution_time
            )

    def _get_primary_device(self) -> AndroidDevice:
        """プライマリデバイスの取得
        
        Returns:
            AndroidDevice: プライマリデバイス
            
        Raises:
            DeviceNotFoundError: デバイスが見つからない場合
        """
        devices = self._device_repository.get_connected_devices()
        
        if not devices:
            raise DeviceNotFoundError("No devices connected")
        
        return devices[0]

    def _generate_filename(self) -> str:
        """自動ファイル名生成
        
        Returns:
            str: 生成されたファイル名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"screenshot_{timestamp}.png"

    def _get_screenshot_directory(self) -> Path:
        """スクリーンショット保存ディレクトリの取得
        
        Returns:
            Path: 保存ディレクトリパス
        """
        return Path.home() / "remocon_screenshots"

    def _create_filepath(self, filename: str) -> Path:
        """ファイルパスの作成
        
        Args:
            filename: ファイル名
            
        Returns:
            Path: 完全なファイルパス
        """
        directory = self._get_screenshot_directory()
        return directory / filename

    def _ensure_directory_exists(self, directory: Path) -> None:
        """ディレクトリの存在確保
        
        Args:
            directory: ディレクトリパス
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _get_file_info(self, filepath: Path) -> int:
        """ファイル情報の取得
        
        Args:
            filepath: ファイルパス
            
        Returns:
            int: ファイルサイズ（バイト）
            
        Raises:
            FileOperationException: ファイル操作エラー
        """
        try:
            return os.path.getsize(filepath)
        except (FileNotFoundError, OSError) as e:
            raise FileOperationException(f"Failed to get file info: {str(e)}")
