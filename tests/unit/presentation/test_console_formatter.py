"""
ConsoleFormatterのテスト
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, Mock

from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.presentation.formatters.console_formatter import ConsoleFormatter
from datetime import datetime


class TestConsoleFormatter:
    """ConsoleFormatterのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のsetup"""
        self.formatter = ConsoleFormatter(use_colors=False)  # テスト用にカラー無効

    def test_init_with_colors(self):
        """カラー有効での初期化をテスト"""
        formatter = ConsoleFormatter(use_colors=True)
        assert formatter.use_colors in [True, False]  # 環境依存

    def test_init_without_colors(self):
        """カラー無効での初期化をテスト"""
        formatter = ConsoleFormatter(use_colors=False)
        assert formatter.use_colors is False

    def test_colorize_without_colors(self):
        """カラー無効時の_colorizeをテスト"""
        result = self.formatter._colorize("test", "RED")
        assert result == "test"

    def test_colorize_with_colors(self):
        """カラー有効時の_colorizeをテスト"""
        formatter = ConsoleFormatter(use_colors=True)
        formatter.use_colors = True  # 強制的に有効化
        result = formatter._colorize("test", "RED")
        assert "\033[31m" in result  # RED color code
        assert "\033[0m" in result   # RESET color code

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_success(self, mock_stdout):
        """成功メッセージ出力をテスト"""
        self.formatter.print_success("Success message")
        output = mock_stdout.getvalue()
        assert "✓ Success message" in output

    @patch('sys.stderr', new_callable=StringIO)
    def test_print_error(self, mock_stderr):
        """エラーメッセージ出力をテスト"""
        self.formatter.print_error("Error message")
        output = mock_stderr.getvalue()
        assert "✗ Error message" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_warning(self, mock_stdout):
        """警告メッセージ出力をテスト"""
        self.formatter.print_warning("Warning message")
        output = mock_stdout.getvalue()
        assert "⚠ Warning message" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_info(self, mock_stdout):
        """情報メッセージ出力をテスト"""
        self.formatter.print_info("Info message")
        output = mock_stdout.getvalue()
        assert "ℹ Info message" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_header(self, mock_stdout):
        """ヘッダー出力をテスト"""
        self.formatter.print_header("Test Header")
        output = mock_stdout.getvalue()
        assert "=== Test Header ===" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_device_list_empty(self, mock_stdout):
        """空のデバイス一覧出力をテスト"""
        self.formatter.print_device_list([])
        output = mock_stdout.getvalue()
        assert "接続されているデバイスが見つかりません" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_device_list_with_devices(self, mock_stdout):
        """デバイス一覧出力をテスト"""
        devices = [
            AndroidDevice(
                device_id="device1",
                device_name="Test Device 1",
                status=DeviceStatus.CONNECTED,
                last_seen=datetime(2023, 1, 1, 12, 0, 0)
            ),
            AndroidDevice(
                device_id="device2",
                device_name="Test Device 2",
                status=DeviceStatus.DISCONNECTED,
                last_seen=datetime(2023, 1, 1, 13, 0, 0)
            )
        ]
        
        self.formatter.print_device_list(devices)
        output = mock_stdout.getvalue()
        
        assert "接続デバイス (2台)" in output
        assert "device1" in output
        assert "device2" in output
        assert "Test Device 1" in output
        assert "Test Device 2" in output
        assert "CONNECTED" in output
        assert "DISCONNECTED" in output

    def test_get_status_color(self):
        """ステータス色取得をテスト"""
        assert self.formatter._get_status_color("connected") == "GREEN"
        assert self.formatter._get_status_color("disconnected") == "RED"
        assert self.formatter._get_status_color("unauthorized") == "YELLOW"
        assert self.formatter._get_status_color("offline") == "MAGENTA"
        assert self.formatter._get_status_color("unknown") == "WHITE"

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_command_result_success(self, mock_stdout):
        """成功コマンド結果出力をテスト"""
        self.formatter.print_command_result(True, "Command succeeded", 0.123)
        output = mock_stdout.getvalue()
        assert "✓ Command succeeded" in output
        assert "実行時間: 0.123秒" in output

    @patch('sys.stderr', new_callable=StringIO)
    def test_print_command_result_failure(self, mock_stderr):
        """失敗コマンド結果出力をテスト"""
        self.formatter.print_command_result(False, "Command failed")
        output = mock_stderr.getvalue()
        assert "✗ Command failed" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_screenshot_result_success(self, mock_stdout):
        """成功スクリーンショット結果出力をテスト"""
        self.formatter.print_screenshot_result(
            success=True,
            filepath="/tmp/screenshot.png",
            file_size=12345,
            execution_time=0.456
        )
        output = mock_stdout.getvalue()
        assert "✓ スクリーンショットを保存しました" in output
        assert "/tmp/screenshot.png" in output
        assert "12.1 KB" in output
        assert "実行時間: 0.456秒" in output

    @patch('sys.stderr', new_callable=StringIO)
    def test_print_screenshot_result_failure(self, mock_stderr):
        """失敗スクリーンショット結果出力をテスト"""
        self.formatter.print_screenshot_result(success=False)
        output = mock_stderr.getvalue()
        assert "✗ スクリーンショットの撮影に失敗しました" in output

    def test_format_file_size(self):
        """ファイルサイズフォーマットをテスト"""
        assert self.formatter._format_file_size(512) == "512 B"
        assert self.formatter._format_file_size(1536) == "1.5 KB"
        assert self.formatter._format_file_size(1572864) == "1.5 MB"

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_separator(self, mock_stdout):
        """区切り線出力をテスト"""
        self.formatter.print_separator()
        output = mock_stdout.getvalue()
        assert "-" * 50 in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_usage_tip(self, mock_stdout):
        """使用方法ヒント出力をテスト"""
        self.formatter.print_usage_tip("This is a tip")
        output = mock_stdout.getvalue()
        assert "💡 ヒント: This is a tip" in output

    @patch('builtins.input', return_value='y')
    def test_prompt_confirmation_yes(self, mock_input):
        """確認プロンプト（Yes）をテスト"""
        result = self.formatter.prompt_confirmation("Continue?")
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_prompt_confirmation_no(self, mock_input):
        """確認プロンプト（No）をテスト"""
        result = self.formatter.prompt_confirmation("Continue?")
        assert result is False

    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_prompt_confirmation_keyboard_interrupt(self, mock_input):
        """確認プロンプト（KeyboardInterrupt）をテスト"""
        result = self.formatter.prompt_confirmation("Continue?")
        assert result is False

    @patch('builtins.input', side_effect=EOFError)
    def test_prompt_confirmation_eof_error(self, mock_input):
        """確認プロンプト（EOFError）をテスト"""
        result = self.formatter.prompt_confirmation("Continue?")
        assert result is False
