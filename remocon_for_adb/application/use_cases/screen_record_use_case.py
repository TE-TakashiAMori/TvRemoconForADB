"""
Screen Record Use Case
画面録画機能のユースケース実装
"""
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from remocon_for_adb.application.dtos.command_dto import (
    ScreenRecordCommandDTO,
    ScreenRecordResultDTO
)
from remocon_for_adb.domain.entities.android_device import AndroidDevice
from remocon_for_adb.domain.entities.screen_record import ScreenRecord
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceNotFoundError,
    DeviceConnectionError
)


class ScreenRecordFailedException(Exception):
    """画面録画失敗例外"""
    pass


class RecordingInProgressException(Exception):
    """録画中例外"""
    pass


class ScreenRecordUseCase:
    """画面録画ユースケース"""

    def __init__(self, device_repository: DeviceRepository):
        """初期化
        
        Args:
            device_repository: デバイスリポジトリ
        """
        self._device_repository = device_repository
        self._current_recording: Optional[ScreenRecord] = None
        self._last_record_path: Optional[str] = None

    def start_recording(self, command: ScreenRecordCommandDTO) -> ScreenRecordResultDTO:
        """画面録画を開始
        
        Args:
            command: 録画コマンドDTO
            
        Returns:
            ScreenRecordResultDTO: 実行結果
            
        Raises:
            RecordingInProgressException: すでに録画中の場合
        """
        start_time = time.time()
        
        try:
            # 録画中チェック
            if self._current_recording and self._current_recording.is_recording():
                raise RecordingInProgressException("Recording is already in progress")
            
            # プライマリデバイス取得
            device = self._get_primary_device()
            
            # 録画時間の決定
            duration = 0 if command.manual_mode else command.duration
            
            # ScreenRecordエンティティ作成
            if command.manual_mode or duration == 0:
                record = ScreenRecord.create_manual_recording()
            else:
                record = ScreenRecord.create_timed_recording(duration)
            
            # ファイル名生成
            filename = command.filename if command.filename else self._generate_filename()
            
            # ファイルパス作成
            filepath = self._create_filepath(filename, command.directory)
            
            # ディレクトリ確保
            self._ensure_directory_exists(filepath.parent)
            
            # 録画開始
            record.start_recording(str(filepath))
            
            # デバイスで録画開始
            success = self._device_repository.start_screen_record(
                device.device_id,
                str(filepath),
                duration
            )
            
            if not success:
                record.mark_error("Failed to start recording on device")
                execution_time = time.time() - start_time
                return ScreenRecordResultDTO(
                    success=False,
                    filepath="",
                    filesize=0,
                    duration=0.0,
                    message="Failed to start recording",
                    execution_time=execution_time
                )
            
            # 現在の録画として保存
            self._current_recording = record
            
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=True,
                filepath=str(filepath),
                filesize=0,  # 録画中はサイズ不明
                duration=0.0,  # 録画中
                message=f"Recording started: {filename}",
                execution_time=execution_time
            )
            
        except (DeviceNotFoundError, DeviceConnectionError) as e:
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=False,
                filepath="",
                filesize=0,
                duration=0.0,
                message=f"Device connection failed: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=False,
                filepath="",
                filesize=0,
                duration=0.0,
                message=f"Unexpected error: {str(e)}",
                execution_time=execution_time
            )

    def stop_recording(self) -> ScreenRecordResultDTO:
        """画面録画を停止
        
        Returns:
            ScreenRecordResultDTO: 実行結果
            
        Raises:
            ScreenRecordFailedException: 録画中でない場合
        """
        start_time = time.time()
        
        try:
            # 録画中チェック
            if not self._current_recording or not self._current_recording.is_recording():
                raise ScreenRecordFailedException("No recording in progress")
            
            # プライマリデバイス取得
            device = self._get_primary_device()
            
            # 録画停止
            self._current_recording.stop_recording()
            
            # ファイルパス取得
            filepath = self._current_recording.filepath
            if not filepath:
                self._current_recording.mark_error("Recording filepath not set")
                execution_time = time.time() - start_time
                return ScreenRecordResultDTO(
                    success=False,
                    filepath="",
                    filesize=0,
                    duration=0.0,
                    message="Recording filepath not set",
                    execution_time=execution_time
                )
            
            # デバイスで録画停止してファイルをプル
            success = self._device_repository.stop_screen_record(device.device_id, str(filepath))
            
            if not success:
                self._current_recording.mark_error("Failed to stop recording on device")
                execution_time = time.time() - start_time
                return ScreenRecordResultDTO(
                    success=False,
                    filepath="",
                    filesize=0,
                    duration=0.0,
                    message="Failed to stop recording",
                    execution_time=execution_time
                )
            
            # ファイルダウンロード待機（少し待つ）
            time.sleep(0.5)
            if not filepath or not os.path.exists(filepath):
                self._current_recording.mark_error("Recording file not found")
                execution_time = time.time() - start_time
                return ScreenRecordResultDTO(
                    success=False,
                    filepath=filepath or "",
                    filesize=0,
                    duration=self._current_recording.get_elapsed_time(),
                    message="Recording file not found",
                    execution_time=execution_time
                )
            
            filesize = self._get_file_info(Path(filepath))
            duration = self._current_recording.get_elapsed_time()
            
            # 録画完了
            self._current_recording.complete_recording(filesize)
            
            # 最後の録画パスを保存
            self._last_record_path = filepath
            
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=True,
                filepath=filepath,
                filesize=filesize,
                duration=duration,
                message=f"Recording completed: {Path(filepath).name}",
                execution_time=execution_time
            )
            
        except (DeviceNotFoundError, DeviceConnectionError) as e:
            if self._current_recording:
                self._current_recording.mark_error(str(e))
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=False,
                filepath="",
                filesize=0,
                duration=0.0,
                message=f"Device connection failed: {str(e)}",
                execution_time=execution_time
            )
        except Exception as e:
            if self._current_recording:
                self._current_recording.mark_error(str(e))
            execution_time = time.time() - start_time
            return ScreenRecordResultDTO(
                success=False,
                filepath="",
                filesize=0,
                duration=0.0,
                message=f"Unexpected error: {str(e)}",
                execution_time=execution_time
            )

    def record_with_duration(self, command: ScreenRecordCommandDTO) -> ScreenRecordResultDTO:
        """時間指定で録画（開始→待機→停止）
        
        Args:
            command: 録画コマンドDTO
            
        Returns:
            ScreenRecordResultDTO: 実行結果
        """
        # 録画開始
        start_result = self.start_recording(command)
        if not start_result.success:
            return start_result
        
        # 指定時間待機
        time.sleep(command.duration)
        
        # 録画停止
        return self.stop_recording()

    def is_recording(self) -> bool:
        """録画中かどうか
        
        Returns:
            bool: 録画中の場合True
        """
        return (
            self._current_recording is not None and
            self._current_recording.is_recording()
        )

    def get_current_recording(self) -> Optional[ScreenRecord]:
        """現在の録画を取得
        
        Returns:
            Optional[ScreenRecord]: 現在の録画、ない場合はNone
        """
        return self._current_recording

    def get_last_record_path(self) -> Optional[str]:
        """最後に録画した動画のパスを取得
        
        Returns:
            Optional[str]: ファイルパス、またはNone
        """
        return self._last_record_path

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
        return f"screenrecord_{timestamp}.mp4"

    def _get_record_directory(self) -> Path:
        """録画保存ディレクトリの取得
        
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
            directory = self._get_record_directory()
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
        """
        try:
            return os.path.getsize(filepath)
        except (FileNotFoundError, OSError):
            return 0
