"""
コンソール出力フォーマッター
CLI出力の整形とカラー表示を担当
"""

import sys
from datetime import datetime
from typing import List, Optional

from remocon_for_adb.domain.entities.android_device import AndroidDevice


class ConsoleFormatter:
    """コンソール出力のフォーマッター"""

    # ANSI カラーコード
    COLORS = {
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BOLD': '\033[1m',
        'RESET': '\033[0m'
    }

    def __init__(self, use_colors: bool = True):
        """フォーマッターを初期化
        
        Args:
            use_colors: カラー出力を使用するかどうか
        """
        self.use_colors = use_colors and self._supports_color()

    def _supports_color(self) -> bool:
        """端末がカラー出力をサポートしているかチェック"""
        # 基本的な検査（環境変数やstdoutの種類をチェック）
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _colorize(self, text: str, color: str) -> str:
        """テキストに色を付ける
        
        Args:
            text: 対象テキスト
            color: カラーコード
            
        Returns:
            カラー化されたテキスト
        """
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['RESET']}"

    def print_success(self, message: str) -> None:
        """成功メッセージを出力"""
        print(self._colorize(f"✓ {message}", 'GREEN'))

    def print_error(self, message: str) -> None:
        """エラーメッセージを出力"""
        print(self._colorize(f"✗ {message}", 'RED'), file=sys.stderr)

    def print_warning(self, message: str) -> None:
        """警告メッセージを出力"""
        print(self._colorize(f"⚠ {message}", 'YELLOW'))

    def print_info(self, message: str) -> None:
        """情報メッセージを出力"""
        print(self._colorize(f"ℹ {message}", 'BLUE'))

    def print_header(self, title: str) -> None:
        """ヘッダーを出力"""
        print()
        print(self._colorize(f"=== {title} ===", 'BOLD'))
        print()

    def print_device_list(self, devices: List[AndroidDevice]) -> None:
        """デバイス一覧を整形して出力
        
        Args:
            devices: デバイス一覧
        """
        if not devices:
            self.print_warning("接続されているデバイスが見つかりません")
            return

        self.print_header(f"接続デバイス ({len(devices)}台)")
        
        for i, device in enumerate(devices, 1):
            status_color = self._get_status_color(device.status.value)
            status_text = self._colorize(device.status.value.upper(), status_color)
            
            print(f"{i:2d}. {self._colorize(device.device_id, 'CYAN')} ")
            print(f"     名前: {device.device_name}")
            print(f"     状態: {status_text}")
            
            if device.last_seen:
                time_str = device.last_seen.strftime("%Y-%m-%d %H:%M:%S")
                print(f"     最終確認: {time_str}")
            print()

    def _get_status_color(self, status: str) -> str:
        """ステータスに応じた色を取得"""
        status_colors = {
            'connected': 'GREEN',
            'disconnected': 'RED',
            'unauthorized': 'YELLOW',
            'offline': 'MAGENTA'
        }
        return status_colors.get(status.lower(), 'WHITE')

    def print_command_result(self, success: bool, message: str, execution_time: Optional[float] = None) -> None:
        """コマンド実行結果を出力
        
        Args:
            success: 実行成功フラグ
            message: メッセージ
            execution_time: 実行時間（秒）
        """
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
            
        if execution_time is not None:
            time_text = f"実行時間: {execution_time:.3f}秒"
            print(self._colorize(time_text, 'CYAN'))

    def print_screenshot_result(self, success: bool, filepath: str = "", 
                              file_size: int = 0, execution_time: float = 0.0, prefix: str = "") -> None:
        """スクリーンショット結果を出力
        
        Args:
            success: 撮影成功フラグ
            filepath: 保存先ファイルパス
            file_size: ファイルサイズ（バイト）
            execution_time: 実行時間（秒）
        """
        if success and filepath:
            self.print_success(f"{prefix}スクリーンショットを保存しました")
            print(f"{prefix}ファイル: {self._colorize(filepath, 'CYAN')}")
            
            if file_size is not None:
                size_text = self._format_file_size(file_size)
                print(f"{prefix}サイズ: {size_text}")
                
            if execution_time is not None:
                time_text = f"実行時間: {execution_time:.3f}秒"
                print(f"{prefix}{self._colorize(time_text, 'CYAN')}")
        else:
            self.print_error(f"{prefix}スクリーンショットの撮影に失敗しました")

    def _format_file_size(self, size_bytes: int) -> str:
        """ファイルサイズを読みやすい形式にフォーマット
        
        Args:
            size_bytes: サイズ（バイト）
            
        Returns:
            フォーマットされたサイズ文字列
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def print_separator(self) -> None:
        """区切り線を出力"""
        print(self._colorize("-" * 50, 'CYAN'))

    def print_usage_tip(self, tip: str) -> None:
        """使用方法のヒントを出力"""
        print()
        print(self._colorize(f"💡 ヒント: {tip}", 'YELLOW'))

    def prompt_confirmation(self, message: str) -> bool:
        """確認プロンプトを表示
        
        Args:
            message: 確認メッセージ
            
        Returns:
            ユーザーの選択（True=Yes, False=No）
        """
        prompt = f"{message} (y/N): "
        try:
            response = input(self._colorize(prompt, 'YELLOW')).strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False
