"""
Main Window for Android TV Remote GUI
Android TV リモコンのメインウィンドウ
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from remocon_for_adb.infrastructure.gateways.adb_gateway import AdbGateway
from remocon_for_adb.infrastructure.repositories.adb_device_repository import AdbDeviceRepository
from remocon_for_adb.application.use_cases.remote_control_use_case import RemoteControlUseCase
from remocon_for_adb.application.use_cases.screenshot_use_case import ScreenshotUseCase
from remocon_for_adb.presentation.gui.widgets.remote_control_widget import RemoteControlWidget
from remocon_for_adb.presentation.gui.widgets.device_manager_widget import DeviceManagerWidget
from remocon_for_adb.presentation.gui.widgets.status_widget import StatusWidget
from remocon_for_adb.presentation.gui.styles.theme import (
    COLORS, FONTS, SIZES, MAIN_FRAME_STYLE, FRAME_STYLE
)


class MainWindow:
    """Android TV リモコン メインウィンドウ"""

    def __init__(self):
        """メインウィンドウを初期化"""
        # Infrastructure層の初期化
        self.adb_gateway = AdbGateway()
        self.device_repository = AdbDeviceRepository(self.adb_gateway)
        
        # Application層の初期化
        self.remote_control_use_case = RemoteControlUseCase(self.device_repository)
        self.screenshot_use_case = ScreenshotUseCase(self.device_repository)
        
        # GUIの初期化
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._setup_keyboard_bindings()

    def _setup_window(self) -> None:
        """ウィンドウの基本設定"""
        self.root = tk.Tk()
        self.root.title("Android TV Remote Controller")
        self.root.geometry(f"{SIZES['window_width']}x{SIZES['window_height']}")
        self.root.configure(bg=COLORS['background'])
        self.root.resizable(False, False)
        
        # ウィンドウを画面中央に配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (SIZES['window_width'] // 2)
        y = (self.root.winfo_screenheight() // 2) - (SIZES['window_height'] // 2)
        self.root.geometry(f"{SIZES['window_width']}x{SIZES['window_height']}+{x}+{y}")

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインコンテナ
        self.main_frame = tk.Frame(self.root, **MAIN_FRAME_STYLE)
        
        # タイトルラベル
        self.title_label = tk.Label(
            self.main_frame,
            text="Android TV Remote",
            font=FONTS['title'],
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        
        # デバイス管理ウィジェット
        self.device_manager = DeviceManagerWidget(
            self.main_frame,
            self.device_repository,
            self._on_device_changed
        )
        
        # リモコンウィジェット
        self.remote_control = RemoteControlWidget(
            self.main_frame,
            self.remote_control_use_case,
            self._on_command_executed
        )
        
        # ステータスウィジェット
        self.status_widget = StatusWidget(self.main_frame)

    def _setup_layout(self) -> None:
        """レイアウトを設定"""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        self.title_label.pack(pady=(0, 20))
        
        # デバイス管理
        self.device_manager.pack(fill=tk.X, pady=(0, 20))
        
        # リモコン
        self.remote_control.pack(pady=(0, 20))
        
        # ステータス
        self.status_widget.pack(fill=tk.X)

    def _setup_keyboard_bindings(self) -> None:
        """キーボードショートカットを設定"""
        self.root.bind('<Up>', lambda e: self.remote_control.send_direction('up'))
        self.root.bind('<Down>', lambda e: self.remote_control.send_direction('down'))
        self.root.bind('<Left>', lambda e: self.remote_control.send_direction('left'))
        self.root.bind('<Right>', lambda e: self.remote_control.send_direction('right'))
        self.root.bind('<Return>', lambda e: self.remote_control.send_button('select'))
        self.root.bind('<Escape>', lambda e: self.remote_control.send_button('back'))
        self.root.bind('<F1>', lambda e: self.remote_control.send_button('home'))
        
        # フォーカスを設定してキーボードイベントを受信できるようにする
        self.root.focus_set()

    def _on_device_changed(self, device_id: Optional[str]) -> None:
        """デバイス変更時のコールバック"""
        if device_id:
            self.status_widget.update_device_status(f"デバイス選択: {device_id}")
        else:
            self.status_widget.update_device_status("デバイス未選択")

    def _on_command_executed(self, command: str, success: bool, execution_time: float) -> None:
        """コマンド実行時のコールバック"""
        self.status_widget.update_last_command(command, success, execution_time)

    def run(self) -> None:
        """GUIアプリケーションを開始"""
        try:
            # 初期デバイス検索
            self._refresh_devices_async()
            
            # メインループ開始
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("エラー", f"アプリケーションの起動に失敗しました: {e}")

    def _refresh_devices_async(self) -> None:
        """非同期でデバイス一覧を更新"""
        def refresh():
            try:
                self.device_manager.refresh_devices()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("エラー", f"デバイス検索に失敗しました: {e}"))
        
        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()

    def close(self) -> None:
        """アプリケーションを終了"""
        self.root.quit()
        self.root.destroy()


def main() -> None:
    """GUIアプリケーションのメイン関数"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\\nアプリケーションが中断されました")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
