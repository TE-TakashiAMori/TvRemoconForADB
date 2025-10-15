"""
CLIメインのテスト
"""

import pytest
from unittest.mock import Mock, patch
from argparse import Namespace

from remocon_for_adb.presentation.cli.main import RemoconCLI


class TestRemoconCLI:
    """RemoconCLIのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のsetup"""
        self.cli = RemoconCLI()

    def test_init(self):
        """CLIの初期化をテスト"""
        assert self.cli.adb_gateway is not None
        assert self.cli.device_repository is not None
        assert self.cli.remote_control_use_case is not None
        assert self.cli.screenshot_use_case is not None
        assert self.cli.formatter is not None
        assert self.cli.direction_command is not None
        assert self.cli.button_command is not None
        assert self.cli.screenshot_command is not None
        assert self.cli.device_command is not None

    def test_create_parser(self):
        """パーサー作成をテスト"""
        parser = self.cli.create_parser()
        assert parser.prog == "remocon-adb"
        assert "Android TV リモコン操作ツール" in parser.description

    def test_run_no_args(self):
        """引数なしでの実行をテスト"""
        result = self.cli.run([])
        assert result == 0

    @patch.object(RemoconCLI, 'device_command')
    def test_run_devices_command(self, mock_device_command):
        """devicesコマンド実行をテスト"""
        mock_device_command.execute.return_value = 0
        result = self.cli.run(["devices"])
        assert result == 0
        mock_device_command.execute.assert_called_once()

    @patch.object(RemoconCLI, 'direction_command')
    def test_run_direction_command(self, mock_direction_command):
        """directionコマンド実行をテスト"""
        mock_direction_command.execute.return_value = 0
        result = self.cli.run(["up"])
        assert result == 0
        mock_direction_command.execute.assert_called_once()

    @patch.object(RemoconCLI, 'button_command')
    def test_run_button_command(self, mock_button_command):
        """buttonコマンド実行をテスト"""
        mock_button_command.execute.return_value = 0
        result = self.cli.run(["select"])
        assert result == 0
        mock_button_command.execute.assert_called_once()
        
    @patch('remocon_for_adb.presentation.cli.main.ButtonCommand')
    def test_run_menu_command(self, mock_button_command_class):
        """menuコマンド実行をテスト"""
        mock_button_instance = Mock()
        mock_button_instance.execute.return_value = 0
        mock_button_command_class.return_value = mock_button_instance
        
        cli = RemoconCLI()
        result = cli.run(["menu"])
        assert result == 0
        mock_button_instance.execute.assert_called_once()

    @patch.object(RemoconCLI, 'screenshot_command')
    def test_run_screenshot_command(self, mock_screenshot_command):
        """screenshotコマンド実行をテスト"""
        mock_screenshot_command.execute.return_value = 0
        result = self.cli.run(["screenshot"])
        assert result == 0
        mock_screenshot_command.execute.assert_called_once()

    def test_run_keyboard_interrupt(self):
        """KeyboardInterrupt処理をテスト"""
        with patch.object(self.cli, 'device_command') as mock_device_command:
            mock_device_command.execute.side_effect = KeyboardInterrupt()
            result = self.cli.run(["devices"])
            assert result == 1

    def test_run_unexpected_error(self):
        """予期しないエラー処理をテスト"""
        with patch.object(self.cli, 'device_command') as mock_device_command:
            mock_device_command.execute.side_effect = Exception("Test error")
            result = self.cli.run(["devices"])
            assert result == 1

    def test_main_function(self):
        """main関数をテスト"""
        from remocon_for_adb.presentation.cli.main import main
        with patch('remocon_for_adb.presentation.cli.main.RemoconCLI') as mock_cli:
            mock_instance = Mock()
            mock_instance.run.return_value = 0
            mock_cli.return_value = mock_instance
            
            result = main()
            assert result == 0
            mock_instance.run.assert_called_once()
