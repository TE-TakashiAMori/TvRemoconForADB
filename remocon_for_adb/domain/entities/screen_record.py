"""
Screen Record エンティティ
画面録画を表現するドメインエンティティ
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RecordState(Enum):
    """録画状態の列挙型"""
    IDLE = "idle"
    RECORDING = "recording"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ScreenRecord:
    """画面録画のエンティティ"""

    duration: int  # 録画時間（秒）、0=手動停止モード
    format: str = "mp4"  # ファイル形式
    state: RecordState = RecordState.IDLE  # 現在の状態
    start_time: Optional[datetime] = None  # 録画開始時刻
    end_time: Optional[datetime] = None  # 録画終了時刻
    filepath: Optional[str] = None  # 保存先ファイルパス
    filesize: int = 0  # ファイルサイズ（バイト）
    error_message: Optional[str] = None  # エラーメッセージ

    # 定数
    MAX_DURATION = 180  # 最大録画時間（3分）
    MIN_DURATION = 0  # 最小録画時間（0=手動停止）
    DEFAULT_DURATION = 30  # デフォルト録画時間（30秒）

    def __post_init__(self) -> None:
        """初期化後の検証"""
        self._validate_duration()
        self._validate_format()

    def _validate_duration(self) -> None:
        """録画時間のバリデーション"""
        if self.duration < self.MIN_DURATION:
            raise ValueError(
                f"Duration must be >= {self.MIN_DURATION} seconds"
            )
        if self.duration > self.MAX_DURATION:
            raise ValueError(
                f"Duration must be <= {self.MAX_DURATION} seconds (3 minutes)"
            )

    def _validate_format(self) -> None:
        """ファイル形式のバリデーション"""
        valid_formats = ["mp4"]
        if self.format.lower() not in valid_formats:
            raise ValueError(
                f"Format must be one of {valid_formats}, got: {self.format}"
            )

    def start_recording(self, filepath: str) -> None:
        """録画を開始
        
        Args:
            filepath: 保存先ファイルパス
            
        Raises:
            ValueError: すでに録画中の場合
        """
        if self.state != RecordState.IDLE:
            raise ValueError(
                f"Cannot start recording in state: {self.state.value}"
            )
        
        self.state = RecordState.RECORDING
        self.start_time = datetime.now()
        self.filepath = filepath
        self.error_message = None

    def stop_recording(self) -> None:
        """録画を停止
        
        Raises:
            ValueError: 録画中でない場合
        """
        if self.state != RecordState.RECORDING:
            raise ValueError(
                f"Cannot stop recording in state: {self.state.value}"
            )
        
        self.state = RecordState.STOPPING
        self.end_time = datetime.now()

    def complete_recording(self, filesize: int) -> None:
        """録画を完了
        
        Args:
            filesize: ファイルサイズ（バイト）
            
        Raises:
            ValueError: 停止処理中でない場合
        """
        if self.state != RecordState.STOPPING:
            raise ValueError(
                f"Cannot complete recording in state: {self.state.value}"
            )
        
        self.state = RecordState.COMPLETED
        self.filesize = filesize

    def mark_error(self, error_message: str) -> None:
        """エラー状態にマーク
        
        Args:
            error_message: エラーメッセージ
        """
        self.state = RecordState.ERROR
        self.error_message = error_message
        if not self.end_time:
            self.end_time = datetime.now()

    def get_elapsed_time(self) -> float:
        """経過時間を取得（秒）
        
        Returns:
            float: 経過時間（秒）、録画前は0
        """
        if not self.start_time:
            return 0.0
        
        end = self.end_time if self.end_time else datetime.now()
        delta = end - self.start_time
        return delta.total_seconds()

    def get_remaining_time(self) -> Optional[float]:
        """残り時間を取得（秒）
        
        Returns:
            Optional[float]: 残り時間（秒）、手動停止モードはNone
        """
        if self.is_manual_mode():
            return None
        
        elapsed = self.get_elapsed_time()
        remaining = self.duration - elapsed
        return max(0.0, remaining)

    def is_manual_mode(self) -> bool:
        """手動停止モードかどうか
        
        Returns:
            bool: 手動停止モードの場合True
        """
        return self.duration == 0

    def is_recording(self) -> bool:
        """録画中かどうか
        
        Returns:
            bool: 録画中の場合True
        """
        return self.state == RecordState.RECORDING

    def is_completed(self) -> bool:
        """録画完了かどうか
        
        Returns:
            bool: 録画完了の場合True
        """
        return self.state == RecordState.COMPLETED

    def is_error(self) -> bool:
        """エラー状態かどうか
        
        Returns:
            bool: エラー状態の場合True
        """
        return self.state == RecordState.ERROR

    def should_auto_stop(self) -> bool:
        """自動停止すべきかどうか
        
        Returns:
            bool: 自動停止すべき場合True
        """
        if self.is_manual_mode():
            return False
        
        if not self.is_recording():
            return False
        
        elapsed = self.get_elapsed_time()
        return elapsed >= self.duration

    @classmethod
    def create_timed_recording(cls, duration: int) -> 'ScreenRecord':
        """時間指定録画を作成
        
        Args:
            duration: 録画時間（秒）
            
        Returns:
            ScreenRecord: 新しい録画エンティティ
        """
        return cls(duration=duration)

    @classmethod
    def create_manual_recording(cls) -> 'ScreenRecord':
        """手動停止録画を作成
        
        Returns:
            ScreenRecord: 新しい録画エンティティ
        """
        return cls(duration=0)

    def __str__(self) -> str:
        """文字列表現"""
        mode = "手動停止" if self.is_manual_mode() else f"{self.duration}秒"
        return f"ScreenRecord(mode={mode}, state={self.state.value})"

    def __repr__(self) -> str:
        """詳細な文字列表現"""
        return (
            f"ScreenRecord("
            f"duration={self.duration}, "
            f"format={self.format}, "
            f"state={self.state.value}, "
            f"elapsed={self.get_elapsed_time():.1f}s)"
        )
