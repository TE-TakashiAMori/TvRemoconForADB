"""
Remote Control Widget
リモコンパネルウィジェット - 方向キーとボタンを提供
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
import threading

from remocon_for_adb.application.use_cases.remote_control_use_case import RemoteControlUseCase
from remocon_for_adb.application.dtos.command_dto import RemoteCommandDTO
from remocon_for_adb.presentation.gui.styles.theme import (
    COLORS, FONTS, DIRECTION_BUTTON_STYLE, ACTION_BUTTON_STYLE, 
    PRIMARY_BUTTON_STYLE, FRAME_STYLE, apply_button_hover_effects
)


class RemoteControlWidget(tk.Frame):
    """リモコンパネルウィジェット"""

    def __init__(self, parent, remote_control_use_case: RemoteControlUseCase, 
                 command_callback: Optional[Callable[[str, bool, float], None]] = None):
        """リモコンウィジェットを初期化
        
        Args:
            parent: 親ウィジェット
            remote_control_use_case: リモコン制御ユースケース
            command_callback: コマンド実行時のコールバック
        """
        super().__init__(parent, **FRAME_STYLE)
        self.remote_control_use_case = remote_control_use_case
        self.command_callback = command_callback
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # 方向キーフレーム
        self.direction_frame = tk.Frame(self, **FRAME_STYLE)
        
        # 方向キーボタン
        self.btn_up = tk.Button(
            self.direction_frame,
            text="▲",
            command=lambda: self.send_direction('up'),
            **DIRECTION_BUTTON_STYLE
        )
        
        self.btn_down = tk.Button(
            self.direction_frame,
            text="▼", 
            command=lambda: self.send_direction('down'),
            **DIRECTION_BUTTON_STYLE
        )
        
        self.btn_left = tk.Button(
            self.direction_frame,
            text="◀",
            command=lambda: self.send_direction('left'),
            **DIRECTION_BUTTON_STYLE
        )
        
        self.btn_right = tk.Button(
            self.direction_frame,
            text="▶",
            command=lambda: self.send_direction('right'),
            **DIRECTION_BUTTON_STYLE
        )
        
        # 選択ボタン（中央）
        self.btn_select = tk.Button(
            self.direction_frame,
            text="OK",
            command=lambda: self.send_button('select'),
            **PRIMARY_BUTTON_STYLE,
            width=6,
            height=2
        )
        
        # アクションボタンフレーム
        self.action_frame = tk.Frame(self, **FRAME_STYLE)
        
        # アクションボタン
        self.btn_back = tk.Button(
            self.action_frame,
            text="戻る",
            command=lambda: self.send_button('back'),
            **ACTION_BUTTON_STYLE
        )
        
        self.btn_home = tk.Button(
            self.action_frame,
            text="ホーム",
            command=lambda: self.send_button('home'),
            **ACTION_BUTTON_STYLE
        )
        
        # ホバー効果を適用
        self._apply_hover_effects()

    def _apply_hover_effects(self) -> None:
        """ボタンにホバー効果を適用"""
        buttons = [
            self.btn_up, self.btn_down, self.btn_left, self.btn_right,
            self.btn_back, self.btn_home
        ]
        
        for button in buttons:
            apply_button_hover_effects(
                button,
                COLORS['button_normal'],
                COLORS['button_hover'],
                COLORS['button_pressed']
            )
        
        # 選択ボタンは特別なスタイル
        apply_button_hover_effects(
            self.btn_select,
            COLORS['primary'],
            COLORS['primary_dark'],
            COLORS['primary_dark']
        )

    def _setup_layout(self) -> None:
        """レイアウトを設定"""
        # 方向キーフレーム
        self.direction_frame.pack(pady=(0, 20))
        
        # 方向キーレイアウト（十字型）
        self.btn_up.grid(row=0, column=1, padx=2, pady=2)
        self.btn_left.grid(row=1, column=0, padx=2, pady=2)
        self.btn_select.grid(row=1, column=1, padx=2, pady=2)
        self.btn_right.grid(row=1, column=2, padx=2, pady=2)
        self.btn_down.grid(row=2, column=1, padx=2, pady=2)
        
        # アクションボタンフレーム
        self.action_frame.pack()
        
        # アクションボタンレイアウト（縦並び）
        self.btn_back.pack(pady=5)
        self.btn_home.pack(pady=5)

    def send_direction(self, direction: str) -> None:
        """方向キーコマンドを送信
        
        Args:
            direction: 方向（up, down, left, right）
        """
        self._send_command_async('direction', direction)

    def send_button(self, button: str) -> None:
        """ボタンコマンドを送信
        
        Args:
            button: ボタン（select, back, home）
        """
        self._send_command_async('button', button)

    def _send_command_async(self, command_type: str, key: str) -> None:
        """非同期でコマンドを送信"""
        def execute_command():
            try:
                # DTOを作成
                command_dto = RemoteCommandDTO(
                    command_type=command_type,
                    key=key
                )
                
                # コマンドを実行
                if command_type == 'direction':
                    result = self.remote_control_use_case.execute_direction_key(command_dto)
                else:  # button
                    result = self.remote_control_use_case.execute_button(command_dto)
                
                # UIスレッドでコールバックを実行
                if self.command_callback:
                    self.after(0, lambda: self.command_callback(
                        f"{command_type}:{key}",
                        result.success,
                        result.execution_time
                    ))
                
                # エラーの場合はメッセージを表示
                if not result.success:
                    self.after(0, lambda: messagebox.showerror(
                        "エラー", 
                        f"コマンドの実行に失敗しました\\n{result.message}"
                    ))
                    
            except Exception as e:
                # UIスレッドでエラーを表示
                self.after(0, lambda: messagebox.showerror(
                    "エラー", 
                    f"予期しないエラーが発生しました\\n{str(e)}"
                ))
        
        # 別スレッドでコマンドを実行（UIをブロックしないため）
        thread = threading.Thread(target=execute_command, daemon=True)
        thread.start()

    def set_enabled(self, enabled: bool) -> None:
        """ウィジェットの有効/無効を設定
        
        Args:
            enabled: 有効にする場合True
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        
        buttons = [
            self.btn_up, self.btn_down, self.btn_left, self.btn_right,
            self.btn_select, self.btn_back, self.btn_home
        ]
        
        for button in buttons:
            button.config(state=state)
