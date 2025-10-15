"""
Screenshot Widget
スクリーンショット撮影・プレビューウィジェット
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
from pathlib import Path
from typing import Optional, Callable

from remocon_for_adb.application.use_cases.screenshot_use_case import ScreenshotUseCase
from remocon_for_adb.application.dtos.command_dto import ScreenshotCommandDTO
from remocon_for_adb.presentation.gui.styles.theme import (
    COLORS, FONTS, BUTTON_STYLE, PRIMARY_BUTTON_STYLE, LABEL_STYLE, 
    FRAME_STYLE, apply_button_hover_effects
)


class ScreenshotWidget(tk.Frame):
    """スクリーンショットウィジェット"""

    def __init__(self, parent, screenshot_use_case: ScreenshotUseCase,
                 status_callback: Optional[Callable[[str, bool, float], None]] = None):
        """スクリーンショットウィジェットを初期化
        
        Args:
            parent: 親ウィジェット
            screenshot_use_case: スクリーンショットユースケース
            status_callback: ステータス更新コールバック
        """
        super().__init__(parent, **FRAME_STYLE)
        self.screenshot_use_case = screenshot_use_case
        self.status_callback = status_callback
        self.preview_window: Optional[tk.Toplevel] = None
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """ウィジェットを作成"""
        # タイトル
        self.title_label = tk.Label(
            self,
            text="📸 スクリーンショット",
            font=FONTS['title'],
            fg=COLORS['text'],
            bg=COLORS['background']
        )
        
        # 撮影ボタンフレーム
        self.capture_frame = tk.Frame(self, **FRAME_STYLE)
        
        # 撮影ボタン
        self.capture_button = tk.Button(
            self.capture_frame,
            text="撮影",
            command=self._capture_screenshot,
            **PRIMARY_BUTTON_STYLE,
            width=12,
            height=2
        )
        
        # プレビューボタン
        self.preview_button = tk.Button(
            self.capture_frame,
            text="プレビュー",
            command=self._show_preview,
            **BUTTON_STYLE,
            width=12,
            state=tk.DISABLED
        )
        
        # 設定フレーム
        self.settings_frame = tk.Frame(self, **FRAME_STYLE)
        
        # ファイル名設定
        self.filename_label = tk.Label(
            self.settings_frame,
            text="ファイル名:",
            **LABEL_STYLE
        )
        
        self.filename_var = tk.StringVar()
        self.filename_entry = tk.Entry(
            self.settings_frame,
            textvariable=self.filename_var,
            width=20,
            font=FONTS['default'],
            bg=COLORS['surface'],
            fg=COLORS['text'],
            insertbackground=COLORS['text']
        )
        
        # 形式選択
        self.format_label = tk.Label(
            self.settings_frame,
            text="形式:",
            **LABEL_STYLE
        )
        
        self.format_var = tk.StringVar(value="png")
        self.format_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.format_var,
            values=["png", "jpg"],
            state="readonly",
            width=8,
            font=FONTS['default']
        )
        
        # 保存先フレーム
        self.path_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.path_label = tk.Label(
            self.path_frame,
            text="保存先:",
            **LABEL_STYLE
        )
        
        self.path_var = tk.StringVar(value=str(Path.home() / "remocon_screenshots"))
        self.path_entry = tk.Entry(
            self.path_frame,
            textvariable=self.path_var,
            width=25,
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text'],
            insertbackground=COLORS['text']
        )
        
        self.browse_button = tk.Button(
            self.path_frame,
            text="参照",
            command=self._browse_directory,
            **BUTTON_STYLE,
            width=6
        )
        
        # 最後の撮影情報
        self.info_frame = tk.Frame(self, **FRAME_STYLE)
        
        self.last_screenshot_label = tk.Label(
            self.info_frame,
            text="最後の撮影: なし",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        
        # ホバー効果適用
        self._apply_hover_effects()

    def _apply_hover_effects(self) -> None:
        """ボタンにホバー効果を適用"""
        # 撮影ボタン（プライマリ）
        apply_button_hover_effects(
            self.capture_button,
            COLORS['primary'],
            COLORS['primary_dark'],
            COLORS['primary_dark']
        )
        
        # 他のボタン
        for button in [self.preview_button, self.browse_button]:
            apply_button_hover_effects(
                button,
                COLORS['button_normal'],
                COLORS['button_hover'],
                COLORS['button_pressed']
            )

    def _setup_layout(self) -> None:
        """レイアウトを設定"""
        # タイトル
        self.title_label.pack(pady=(0, 10))
        
        # 撮影ボタン
        self.capture_frame.pack(pady=(0, 10))
        self.capture_button.pack(side=tk.LEFT, padx=(0, 10))
        self.preview_button.pack(side=tk.LEFT)
        
        # 設定
        self.settings_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.filename_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filename_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)
        
        self.format_label.grid(row=0, column=2, sticky=tk.W, pady=2)
        self.format_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 保存先
        self.path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_label.pack(side=tk.LEFT)
        self.path_entry.pack(side=tk.LEFT, padx=(5, 5), expand=True, fill=tk.X)
        self.browse_button.pack(side=tk.RIGHT)
        
        # 最後の撮影情報
        self.info_frame.pack(fill=tk.X)
        self.last_screenshot_label.pack()

    def _capture_screenshot(self) -> None:
        """スクリーンショットを撮影"""
        def capture():
            try:
                # UIを無効化
                self.after(0, lambda: self._set_loading(True))
                
                # ファイル名を取得（空の場合は自動生成）
                filename = self.filename_var.get().strip()
                if filename and not filename.endswith(f".{self.format_var.get()}"):
                    filename += f".{self.format_var.get()}"
                
                # DTOを作成
                command_dto = ScreenshotCommandDTO(
                    filename=filename if filename else None,
                    directory=self.path_var.get().strip(),
                    format=self.format_var.get()
                )
                
                # スクリーンショット実行
                result = self.screenshot_use_case.capture_screenshot(command_dto)
                
                # UIスレッドで結果処理
                self.after(0, lambda: self._handle_capture_result(result))
                
            except Exception as e:
                # UIスレッドでエラーを表示
                self.after(0, lambda: self._handle_error(f"撮影エラー: {str(e)}"))
            finally:
                # UIを有効化
                self.after(0, lambda: self._set_loading(False))
        
        # 別スレッドで実行
        thread = threading.Thread(target=capture, daemon=True)
        thread.start()

    def _handle_capture_result(self, result) -> None:
        """撮影結果を処理
        
        Args:
            result: ScreenshotResultDTO
        """
        if result.success:
            # 成功時の処理
            filename = Path(result.filepath).name
            filesize_mb = result.filesize / (1024 * 1024)
            
            info_text = f"最後の撮影: {filename} ({filesize_mb:.2f}MB)"
            self.last_screenshot_label.config(text=info_text, fg=COLORS['success'])
            
            # プレビューボタンを有効化
            self.preview_button.config(state=tk.NORMAL)
            self.last_filepath = result.filepath
            
            # ステータスコールバック
            if self.status_callback:
                self.status_callback("screenshot", True, result.execution_time)
            
            # 成功メッセージ
            messagebox.showinfo("撮影完了", f"スクリーンショットを保存しました\\n{filename}")
            
        else:
            # 失敗時の処理
            self.last_screenshot_label.config(
                text=f"撮影失敗: {result.message}",
                fg=COLORS['error']
            )
            
            # ステータスコールバック
            if self.status_callback:
                self.status_callback("screenshot", False, result.execution_time)
            
            # エラーメッセージ
            messagebox.showerror("撮影失敗", result.message)

    def _show_preview(self) -> None:
        """プレビューウィンドウを表示"""
        if not hasattr(self, 'last_filepath') or not Path(self.last_filepath).exists():
            messagebox.showerror("エラー", "プレビューする画像が見つかりません")
            return
        
        # 既存のプレビューウィンドウを閉じる
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        # 新しいプレビューウィンドウを作成
        self.preview_window = tk.Toplevel(self)
        self.preview_window.title("スクリーンショット プレビュー")
        self.preview_window.configure(bg=COLORS['background'])
        
        try:
            # 画像を読み込んでリサイズ
            image = Image.open(self.last_filepath)
            
            # アスペクト比を保持してリサイズ（最大600x400）
            max_width, max_height = 600, 400
            ratio = min(max_width/image.width, max_height/image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            image_resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_resized)
            
            # ラベルに画像を表示
            image_label = tk.Label(self.preview_window, image=photo, bg=COLORS['background'])
            image_label.image = photo  # 参照を保持
            image_label.pack(padx=10, pady=10)
            
            # 画像情報を表示
            info_text = f"サイズ: {image.width}x{image.height} | ファイル: {Path(self.last_filepath).name}"
            info_label = tk.Label(
                self.preview_window,
                text=info_text,
                font=FONTS['small'],
                fg=COLORS['text_secondary'],
                bg=COLORS['background']
            )
            info_label.pack(pady=(0, 10))
            
            # ウィンドウサイズを調整
            self.preview_window.update_idletasks()
            width = new_width + 20
            height = new_height + 60
            self.preview_window.geometry(f"{width}x{height}")
            
            # ウィンドウを中央に配置
            self.preview_window.transient(self.winfo_toplevel())
            self.preview_window.grab_set()
            
        except Exception as e:
            messagebox.showerror("プレビューエラー", f"画像の読み込みに失敗しました: {str(e)}")
            if self.preview_window:
                self.preview_window.destroy()

    def _browse_directory(self) -> None:
        """保存先ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="保存先ディレクトリを選択",
            initialdir=self.path_var.get()
        )
        if directory:
            self.path_var.set(directory)

    def _set_loading(self, loading: bool) -> None:
        """ローディング状態を設定
        
        Args:
            loading: ローディング中の場合True
        """
        state = tk.DISABLED if loading else tk.NORMAL
        
        self.capture_button.config(
            state=state,
            text="撮影中..." if loading else "撮影"
        )
        self.filename_entry.config(state=state)
        self.format_combo.config(state="disabled" if loading else "readonly")
        self.path_entry.config(state=state)
        self.browse_button.config(state=state)

    def _handle_error(self, error_message: str) -> None:
        """エラーハンドリング
        
        Args:
            error_message: エラーメッセージ
        """
        self.last_screenshot_label.config(
            text=f"エラー: {error_message}",
            fg=COLORS['error']
        )
        messagebox.showerror("エラー", error_message)

    def set_enabled(self, enabled: bool) -> None:
        """ウィジェットの有効/無効を設定
        
        Args:
            enabled: 有効にする場合True
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        combo_state = "readonly" if enabled else "disabled"
        
        self.capture_button.config(state=state)
        self.preview_button.config(state=state if hasattr(self, 'last_filepath') else tk.DISABLED)
        self.filename_entry.config(state=state)
        self.format_combo.config(state=combo_state)
        self.path_entry.config(state=state)
        self.browse_button.config(state=state)