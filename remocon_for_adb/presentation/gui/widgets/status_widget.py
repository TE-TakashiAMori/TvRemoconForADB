"""
Status Widget
ステータス表示ウィジェット - 最後のコマンドと実行結果を表示
"""
import tkinter as tk
from datetime import datetime
from typing import Optional

from remocon_for_adb.presentation.gui.styles.theme import (
    COLORS, FONTS, LABEL_STYLE, STATUS_LABEL_STYLE, FRAME_STYLE
)


class StatusWidget(tk.Frame):
    """ステータス表示ウィジェット"""

    def __init__(self, parent):
        """ステータスウィジェットを初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent, **FRAME_STYLE)
        self._create_widgets()
        self._setup_layout()
        self._initialize_status()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # ステータスタイトル
        self.title_label = tk.Label(
            self,
            text="--- ステータス ---",
            font=FONTS['title'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        
        # デバイス状態フレーム
        self.device_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.device_status_label = tk.Label(
            self.device_frame,
            text="デバイス:",
            **STATUS_LABEL_STYLE
        )
        
        self.device_value_label = tk.Label(
            self.device_frame,
            text="未選択",
            font=FONTS['default'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # 最後のコマンドフレーム
        self.command_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.command_status_label = tk.Label(
            self.command_frame,
            text="最後のコマンド:",
            **STATUS_LABEL_STYLE
        )
        
        self.command_value_label = tk.Label(
            self.command_frame,
            text="なし",
            font=FONTS['default'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # 実行時間フレーム
        self.time_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.time_status_label = tk.Label(
            self.time_frame,
            text="実行時間:",
            **STATUS_LABEL_STYLE
        )
        
        self.time_value_label = tk.Label(
            self.time_frame,
            text="--",
            font=FONTS['default'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # 結果フレーム
        self.result_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.result_status_label = tk.Label(
            self.result_frame,
            text="結果:",
            **STATUS_LABEL_STYLE
        )
        
        self.result_value_label = tk.Label(
            self.result_frame,
            text="--",
            font=FONTS['default'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # タイムスタンプフレーム
        self.timestamp_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.timestamp_label = tk.Label(
            self.timestamp_frame,
            text="",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )

    def _setup_layout(self) -> None:
        """レイアウトを設定"""
        # タイトル
        self.title_label.pack(pady=(0, 10))
        
        # デバイス状態
        self.device_frame.pack(fill=tk.X, pady=2)
        self.device_status_label.pack(side=tk.LEFT)
        self.device_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 最後のコマンド
        self.command_frame.pack(fill=tk.X, pady=2)
        self.command_status_label.pack(side=tk.LEFT)
        self.command_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 実行時間
        self.time_frame.pack(fill=tk.X, pady=2)
        self.time_status_label.pack(side=tk.LEFT)
        self.time_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 結果
        self.result_frame.pack(fill=tk.X, pady=2)
        self.result_status_label.pack(side=tk.LEFT)
        self.result_value_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # タイムスタンプ
        self.timestamp_frame.pack(fill=tk.X, pady=(10, 0))
        self.timestamp_label.pack()

    def _initialize_status(self) -> None:
        """初期ステータスを設定"""
        self.update_device_status("デバイス未選択")
        self._update_timestamp()

    def update_device_status(self, status: str) -> None:
        """デバイス状態を更新
        
        Args:
            status: デバイス状態メッセージ
        """
        self.device_value_label.config(text=status)
        self._update_timestamp()

    def update_last_command(self, command: str, success: bool, execution_time: float) -> None:
        """最後のコマンド情報を更新
        
        Args:
            command: 実行したコマンド
            success: 成功フラグ
            execution_time: 実行時間（秒）
        """
        # コマンド名を日本語に変換
        command_text = self._format_command_text(command)
        self.command_value_label.config(text=command_text)
        
        # 実行時間を表示
        time_text = f"{execution_time:.3f}秒"
        self.time_value_label.config(text=time_text)
        
        # 結果を表示
        if success:
            result_text = "成功"
            result_color = COLORS['success']
        else:
            result_text = "失敗"
            result_color = COLORS['error']
        
        self.result_value_label.config(text=result_text, fg=result_color)
        
        # タイムスタンプを更新
        self._update_timestamp()

    def _format_command_text(self, command: str) -> str:
        """コマンドテキストを日本語に変換
        
        Args:
            command: コマンド文字列 (例: "direction:up")
            
        Returns:
            日本語のコマンド名
        """
        command_map = {
            'direction:up': '上方向キー',
            'direction:down': '下方向キー',
            'direction:left': '左方向キー',
            'direction:right': '右方向キー',
            'button:select': '選択ボタン',
            'button:back': '戻るボタン',
            'button:home': 'ホームボタン'
        }
        
        return command_map.get(command, command)

    def _update_timestamp(self) -> None:
        """タイムスタンプを更新"""
        now = datetime.now()
        timestamp_text = f"最終更新: {now.strftime('%H:%M:%S')}"
        self.timestamp_label.config(text=timestamp_text)

    def clear_status(self) -> None:
        """ステータスをクリア"""
        self.command_value_label.config(text="なし")
        self.time_value_label.config(text="--")
        self.result_value_label.config(text="--", fg=COLORS['text_secondary'])
        self._update_timestamp()

    def show_error(self, error_message: str) -> None:
        """エラーメッセージを表示
        
        Args:
            error_message: エラーメッセージ
        """
        self.command_value_label.config(text="エラー")
        self.time_value_label.config(text="--")
        self.result_value_label.config(text=error_message, fg=COLORS['error'])
        self._update_timestamp()

    def show_loading(self, message: str = "実行中...") -> None:
        """ローディング状態を表示
        
        Args:
            message: ローディングメッセージ
        """
        self.result_value_label.config(text=message, fg=COLORS['warning'])
        self._update_timestamp()
