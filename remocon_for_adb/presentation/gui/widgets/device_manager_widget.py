"""
Device Manager Widget
デバイス管理ウィジェット - デバイス一覧表示と選択機能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable
import threading

from remocon_for_adb.infrastructure.repositories.adb_device_repository import AdbDeviceRepository
from remocon_for_adb.domain.entities.android_device import AndroidDevice
from remocon_for_adb.presentation.gui.styles.theme import (
    COLORS, FONTS, BUTTON_STYLE, LABEL_STYLE, FRAME_STYLE, apply_button_hover_effects
)


class DeviceManagerWidget(tk.Frame):
    """デバイス管理ウィジェット"""

    def __init__(self, parent, device_repository: AdbDeviceRepository,
                 device_callback: Optional[Callable[[Optional[str]], None]] = None):
        """デバイス管理ウィジェットを初期化
        
        Args:
            parent: 親ウィジェット
            device_repository: デバイスリポジトリ
            device_callback: デバイス変更時のコールバック
        """
        super().__init__(parent, **FRAME_STYLE)
        self.device_repository = device_repository
        self.device_callback = device_callback
        self.devices: List[AndroidDevice] = []
        self.selected_device: Optional[AndroidDevice] = None
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # デバイス選択フレーム
        self.device_frame = tk.Frame(self, **FRAME_STYLE)
        
        # ラベル
        self.device_label = tk.Label(
            self.device_frame,
            text="接続デバイス:",
            **LABEL_STYLE
        )
        
        # デバイス選択コンボボックス
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            self.device_frame,
            textvariable=self.device_var,
            state="readonly",
            width=25,
            font=FONTS['default']
        )
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_selected)
        
        # 更新ボタン
        self.refresh_button = tk.Button(
            self.device_frame,
            text="更新",
            command=self.refresh_devices,
            **BUTTON_STYLE,
            width=8
        )
        
        # ステータスフレーム
        self.status_frame = tk.Frame(self, **FRAME_STYLE)
        
        # 接続状態インジケーター
        self.status_canvas = tk.Canvas(
            self.status_frame,
            width=20,
            height=20,
            bg=COLORS['background'],
            highlightthickness=0
        )
        self.status_indicator = self.status_canvas.create_oval(
            5, 5, 15, 15,
            fill=COLORS['error'],
            outline=COLORS['text']
        )
        
        # ステータステキスト
        self.status_label = tk.Label(
            self.status_frame,
            text="デバイス未接続",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # ホバー効果を適用
        apply_button_hover_effects(
            self.refresh_button,
            COLORS['button_normal'],
            COLORS['button_hover'],
            COLORS['button_pressed']
        )

    def _setup_layout(self) -> None:
        """レイアウトを設定"""
        # デバイス選択フレーム
        self.device_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.device_label.pack(side=tk.LEFT)
        self.device_combo.pack(side=tk.LEFT, padx=(10, 5), expand=True, fill=tk.X)
        self.refresh_button.pack(side=tk.RIGHT)
        
        # ステータスフレーム
        self.status_frame.pack(fill=tk.X)
        
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 5))
        self.status_label.pack(side=tk.LEFT)

    def refresh_devices(self) -> None:
        """デバイス一覧を更新"""
        def refresh():
            try:
                # UIを無効化
                self.after(0, lambda: self._set_loading(True))
                
                # デバイス一覧を取得
                devices = self.device_repository.get_connected_devices()
                
                # UIスレッドで更新
                self.after(0, lambda: self._update_device_list(devices))
                
            except Exception as e:
                # UIスレッドでエラーを表示
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._handle_error(f"デバイス検索エラー: {msg}"))
            finally:
                # UIを有効化
                self.after(0, lambda: self._set_loading(False))
        
        # 別スレッドで実行
        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()

    def _update_device_list(self, devices: List[AndroidDevice]) -> None:
        """デバイス一覧を更新
        
        Args:
            devices: デバイス一覧
        """
        self.devices = devices
        
        # コンボボックスを更新
        device_names = []
        for device in devices:
            name = f"{device.device_id}"
            if device.device_name and device.device_name != device.device_id:
                name = f"{device.device_name} ({device.device_id})"
            device_names.append(name)
        
        self.device_combo['values'] = device_names
        
        if devices:
            # 最初のデバイスを選択
            self.device_combo.current(0)
            self.selected_device = devices[0]
            self._update_status(True, f"{len(devices)}台のデバイスが接続中")
            
            # コールバックを呼び出し
            if self.device_callback:
                self.device_callback(self.selected_device.device_id)
        else:
            # デバイスなし
            self.device_combo.set("")
            self.selected_device = None
            self._update_status(False, "デバイスが見つかりません")
            
            # コールバックを呼び出し
            if self.device_callback:
                self.device_callback(None)

    def _on_device_selected(self, event) -> None:
        """デバイス選択時のイベントハンドラ"""
        selection = self.device_combo.current()
        if 0 <= selection < len(self.devices):
            self.selected_device = self.devices[selection]
            self._update_status(True, f"デバイス選択: {self.selected_device.device_id}")
            
            # コールバックを呼び出し
            if self.device_callback:
                self.device_callback(self.selected_device.device_id)

    def _update_status(self, connected: bool, message: str) -> None:
        """ステータス表示を更新
        
        Args:
            connected: 接続状態
            message: ステータスメッセージ
        """
        # インジケーターの色を変更
        color = COLORS['success'] if connected else COLORS['error']
        self.status_canvas.itemconfig(self.status_indicator, fill=color)
        
        # ステータステキストを更新
        self.status_label.config(text=message)

    def _set_loading(self, loading: bool) -> None:
        """ローディング状態を設定
        
        Args:
            loading: ローディング中の場合True
        """
        state = tk.DISABLED if loading else tk.NORMAL
        self.device_combo.config(state="disabled" if loading else "readonly")
        self.refresh_button.config(state=state)
        
        if loading:
            self._update_status(False, "デバイスを検索中...")
            # インジケーターを黄色に
            self.status_canvas.itemconfig(self.status_indicator, fill=COLORS['warning'])

    def _handle_error(self, error_message: str) -> None:
        """エラーハンドリング
        
        Args:
            error_message: エラーメッセージ
        """
        self._update_status(False, "エラーが発生しました")
        messagebox.showerror("デバイス管理エラー", error_message)

    def get_selected_device(self) -> Optional[AndroidDevice]:
        """選択中のデバイスを取得
        
        Returns:
            選択中のデバイス、または None
        """
        return self.selected_device

    def set_enabled(self, enabled: bool) -> None:
        """ウィジェットの有効/無効を設定
        
        Args:
            enabled: 有効にする場合True
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        combo_state = "readonly" if enabled else "disabled"
        
        self.device_combo.config(state=combo_state)
        self.refresh_button.config(state=state)
