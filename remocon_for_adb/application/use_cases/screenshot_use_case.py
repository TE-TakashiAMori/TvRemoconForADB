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
        self._last_screenshot_path: Optional[str] = None

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
            filename = command.filename if command.filename else self._generate_filename(command.format)
            
            # ファイルパス作成
            filepath = self._create_filepath(filename, command.directory)
            
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
            
            # 最後のスクリーンショットパスを保存
            self._last_screenshot_path = str(filepath)
            
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

    def _generate_filename(self, format: str = "png") -> str:
        """自動ファイル名生成
        
        Args:
            format: ファイル形式（png、jpg）
            
        Returns:
            str: 生成されたファイル名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"screenshot_{timestamp}.{format}"

    def _get_screenshot_directory(self) -> Path:
        """スクリーンショット保存ディレクトリの取得
        
        Returns:
            Path: 保存ディレクトリパス
        """
        return Path.home() / "remocon_screenshots"

    def _create_filepath(self, filename: str, custom_directory: Optional[str] = None) -> Path:
        """ファイルパスの作成
        
        Args:
            filename: ファイル名
            custom_directory: カスタムディレクトリ（Noneの場合はデフォルト）
            
        Returns:
            Path: 完全なファイルパス
        """
        if custom_directory:
            directory = Path(custom_directory)
        else:
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

    def get_last_screenshot_path(self) -> Optional[str]:
        """最後に撮影したスクリーンショットのパスを取得
        
        Returns:
            Optional[str]: ファイルパス、またはNone
        """
        return self._last_screenshot_path

    def capture_burst_screenshots(self, command: ScreenshotCommandDTO, count: int = 3, 
                                interval: float = 1.0) -> list:
        """バースト撮影（連続撮影）
        
        Args:
            command: スクリーンショットコマンドDTO
            count: 撮影枚数
            interval: 撮影間隔（秒）
            
        Returns:
            list[ScreenshotResultDTO]: 撮影結果のリスト
        """
        results = []
        
        for i in range(count):
            # ファイル名に連番を追加
            if command.filename:
                base_name = Path(command.filename).stem
                extension = Path(command.filename).suffix or f".{command.format}"
                burst_filename = f"{base_name}_{i+1:03d}{extension}"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                burst_filename = f"burst_{timestamp}_{i+1:03d}.{command.format}"
            
            # 新しいコマンドDTOを作成
            burst_command = ScreenshotCommandDTO(
                filename=burst_filename,
                directory=command.directory,
                format=command.format,
                quality=command.quality
            )
            
            # 撮影実行
            result = self.capture_screenshot(burst_command)
            results.append(result)
            
            # 最後以外はインターバル待機
            if i < count - 1:
                time.sleep(interval)
        
        return results

    def get_screenshot_directory_info(self, directory: Optional[str] = None) -> dict:
        """スクリーンショットディレクトリの情報を取得
        
        Args:
            directory: チェックするディレクトリ（Noneの場合はデフォルト）
            
        Returns:
            dict: ディレクトリ情報
        """
        if directory:
            target_dir = Path(directory)
        else:
            target_dir = self._get_screenshot_directory()
        
        try:
            if not target_dir.exists():
                return {
                    'exists': False,
                    'writable': False,
                    'file_count': 0,
                    'total_size': 0,
                    'path': str(target_dir)
                }
            
            # ディレクトリ内のスクリーンショットファイルを検索
            screenshot_files = []
            for pattern in ['*.png', '*.jpg', '*.jpeg']:
                screenshot_files.extend(target_dir.glob(pattern))
            
            total_size = sum(f.stat().st_size for f in screenshot_files if f.is_file())
            
            return {
                'exists': True,
                'writable': os.access(target_dir, os.W_OK),
                'file_count': len(screenshot_files),
                'total_size': total_size,
                'path': str(target_dir)
            }
            
        except Exception as e:
            return {
                'exists': False,
                'writable': False,
                'file_count': 0,
                'total_size': 0,
                'path': str(target_dir),
                'error': str(e)
            }
