"""
CLI コマンドハンドラー
各サブコマンドの処理を担当
"""

import argparse
from typing import Optional

from remocon_for_adb.application.dtos.command_dto import RemoteCommandDTO
from remocon_for_adb.application.dtos.command_dto import ScreenshotCommandDTO
from remocon_for_adb.application.use_cases.remote_control_use_case import RemoteControlUseCase
from remocon_for_adb.application.use_cases.screenshot_use_case import ScreenshotUseCase
from remocon_for_adb.domain.repositories.device_repository import DeviceRepository, DeviceConnectionError
from remocon_for_adb.presentation.formatters.console_formatter import ConsoleFormatter


class BaseCommand:
    """コマンドハンドラーの基底クラス"""

    def __init__(self, formatter: ConsoleFormatter):
        """基底コマンドを初期化
        
        Args:
            formatter: コンソール出力フォーマッター
        """
        self.formatter = formatter

    def execute(self, args: argparse.Namespace) -> int:
        """コマンドを実行
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード（0=成功、1=エラー）
        """
        raise NotImplementedError


class DeviceCommand(BaseCommand):
    """デバイス一覧表示コマンド"""

    def __init__(self, device_repository: DeviceRepository, formatter: ConsoleFormatter):
        """デバイスコマンドを初期化
        
        Args:
            device_repository: デバイスリポジトリ
            formatter: コンソール出力フォーマッター
        """
        super().__init__(formatter)
        self.device_repository = device_repository

    def execute(self, args: argparse.Namespace) -> int:
        """デバイス一覧を表示
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード
        """
        try:
            if args.refresh:
                self.formatter.print_info("デバイス一覧を再取得しています...")
                self.device_repository.refresh_device_list()

            devices = self.device_repository.get_connected_devices()
            self.formatter.print_device_list(devices)
            
            if devices:
                self.formatter.print_usage_tip(
                    "デバイスIDを指定してコマンド実行: remocon-adb direction up -d DEVICE_ID"
                )
            else:
                self.formatter.print_usage_tip(
                    "ADBデバッグが有効で、USBまたはネットワーク経由で接続されているか確認してください"
                )
            
            return 0

        except DeviceConnectionError as e:
            self.formatter.print_error(f"デバイス取得エラー: {e}")
            return 1
        except Exception as e:
            self.formatter.print_error(f"予期しないエラー: {e}")
            return 1


class DirectionCommand(BaseCommand):
    """方向キーコマンド"""

    def __init__(self, remote_control_use_case: RemoteControlUseCase, formatter: ConsoleFormatter):
        """方向キーコマンドを初期化
        
        Args:
            remote_control_use_case: リモコン制御ユースケース
            formatter: コンソール出力フォーマッター
        """
        super().__init__(formatter)
        self.remote_control_use_case = remote_control_use_case

    def execute(self, args: argparse.Namespace) -> int:
        """方向キーコマンドを実行
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード
        """
        try:
            # コマンドDTOを作成
            command_dto = RemoteCommandDTO(
                command_type="direction",
                key=args.key
            )

            # ユースケースを実行
            result = self.remote_control_use_case.execute_direction_key(command_dto)

            # 結果を表示
            if result.success:
                message = f"方向キー '{args.key}' を送信しました"
                self.formatter.print_command_result(True, message, result.execution_time)
            else:
                self.formatter.print_command_result(False, result.message or "コマンド実行に失敗しました")

            return 0 if result.success else 1

        except Exception as e:
            self.formatter.print_error(f"方向キーコマンドエラー: {e}")
            return 1


class ButtonCommand(BaseCommand):
    """ボタンコマンド"""

    def __init__(self, remote_control_use_case: RemoteControlUseCase, formatter: ConsoleFormatter):
        """ボタンコマンドを初期化
        
        Args:
            remote_control_use_case: リモコン制御ユースケース
            formatter: コンソール出力フォーマッター
        """
        super().__init__(formatter)
        self.remote_control_use_case = remote_control_use_case

    def execute(self, args: argparse.Namespace) -> int:
        """ボタンコマンドを実行
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード
        """
        try:
            # コマンドDTOを作成
            command_dto = RemoteCommandDTO(
                command_type="button",
                key=args.key
            )

            # ユースケースを実行
            result = self.remote_control_use_case.execute_button(command_dto)

            # 結果を表示
            if result.success:
                message = f"ボタン '{args.key}' を送信しました"
                self.formatter.print_command_result(True, message, result.execution_time)
            else:
                self.formatter.print_command_result(False, result.message or "コマンド実行に失敗しました")

            return 0 if result.success else 1

        except Exception as e:
            self.formatter.print_error(f"ボタンコマンドエラー: {e}")
            return 1


class ScreenshotCommand(BaseCommand):
    """スクリーンショットコマンド"""

    def __init__(self, screenshot_use_case: ScreenshotUseCase, formatter: ConsoleFormatter):
        """スクリーンショットコマンドを初期化
        
        Args:
            screenshot_use_case: スクリーンショットユースケース
            formatter: コンソール出力フォーマッター
        """
        super().__init__(formatter)
        self.screenshot_use_case = screenshot_use_case

    def execute(self, args: argparse.Namespace) -> int:
        """スクリーンショットコマンドを実行
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード
        """
        try:
            # コマンドDTOを作成
            command_dto = ScreenshotCommandDTO(
                filename=args.filename
            )

            # ユースケースを実行
            self.formatter.print_info("スクリーンショットを撮影しています...")
            result = self.screenshot_use_case.capture_screenshot(command_dto)

            # 結果を表示
            if result.success:
                self.formatter.print_screenshot_result(
                    success=True,
                    filepath=result.filepath,
                    file_size=result.file_size,
                    execution_time=result.execution_time
                )
            else:
                self.formatter.print_screenshot_result(success=False)
                if result.message:
                    self.formatter.print_error(result.message)

            return 0 if result.success else 1

        except Exception as e:
            self.formatter.print_error(f"スクリーンショットコマンドエラー: {e}")
            return 1
