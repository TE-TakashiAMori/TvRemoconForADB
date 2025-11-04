"""
CLI メインエントリーポイント
Android TV リモコンアプリケーションのコマンドラインインターフェース
"""

import argparse
import sys
from typing import Optional

from remocon_for_adb.application.use_cases.remote_control_use_case import RemoteControlUseCase
from remocon_for_adb.application.use_cases.screenshot_use_case import ScreenshotUseCase
from remocon_for_adb.application.use_cases.screen_record_use_case import ScreenRecordUseCase
from remocon_for_adb.infrastructure.gateways.adb_gateway import AdbGateway
from remocon_for_adb.infrastructure.repositories.adb_device_repository import AdbDeviceRepository
from remocon_for_adb.presentation.cli.commands import (
    DirectionCommand,
    ButtonCommand,
    ScreenshotCommand,
    RecordCommand,
    DeviceCommand,
)
from remocon_for_adb.presentation.formatters.console_formatter import ConsoleFormatter


class RemoconCLI:
    """Android TV リモコン CLI アプリケーション"""

    def __init__(self):
        """CLIアプリケーションを初期化"""
        # Infrastructure層の初期化
        self.adb_gateway = AdbGateway()
        self.device_repository = AdbDeviceRepository(self.adb_gateway)
        
        # Application層の初期化
        self.remote_control_use_case = RemoteControlUseCase(self.device_repository)
        self.screenshot_use_case = ScreenshotUseCase(self.device_repository)
        self.screen_record_use_case = ScreenRecordUseCase(self.device_repository)
        
        # Presentation層の初期化
        self.formatter = ConsoleFormatter()
        self.direction_command = DirectionCommand(self.remote_control_use_case, self.formatter)
        self.button_command = ButtonCommand(self.remote_control_use_case, self.formatter)
        self.screenshot_command = ScreenshotCommand(self.screenshot_use_case, self.formatter)
        self.record_command = RecordCommand(self.screen_record_use_case, self.formatter)
        self.device_command = DeviceCommand(self.device_repository, self.formatter)

    def create_parser(self) -> argparse.ArgumentParser:
        """コマンドライン引数パーサーを作成"""
        parser = argparse.ArgumentParser(
            prog="remocon-adb",
            description="Android TV リモコン操作ツール (ADB経由)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用例:
  remocon-adb devices                    # 接続デバイス一覧表示
  remocon-adb up                         # 上方向キー
  remocon-adb down                       # 下方向キー
  remocon-adb left                       # 左方向キー
  remocon-adb right                      # 右方向キー
  remocon-adb select                     # 選択ボタン
  remocon-adb back                       # 戻るボタン
  remocon-adb home                       # ホームボタン
  remocon-adb screenshot                 # スクリーンショット撮影
  remocon-adb screenshot -f my_screen.png # ファイル名指定でスクリーンショット
  remocon-adb record                     # 画面録画（30秒）
  remocon-adb record -d 60               # 60秒間録画
  remocon-adb record --manual            # 手動停止モード録画
            """
        )

        # サブコマンドを追加
        subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

        # devices サブコマンド
        devices_parser = subparsers.add_parser("devices", help="接続デバイス一覧表示")
        devices_parser.add_argument(
            "--refresh", "-r",
            action="store_true",
            help="デバイス一覧を強制的に再取得"
        )

        # 方向キーコマンド（直接指定）
        up_parser = subparsers.add_parser("up", help="上方向キー")
        up_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )
        
        down_parser = subparsers.add_parser("down", help="下方向キー")
        down_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )
        
        left_parser = subparsers.add_parser("left", help="左方向キー")
        left_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )
        
        right_parser = subparsers.add_parser("right", help="右方向キー")
        right_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )

        # ボタンコマンド（直接指定）
        select_parser = subparsers.add_parser("select", help="選択ボタン")
        select_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )
        
        back_parser = subparsers.add_parser("back", help="戻るボタン")
        back_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )
        
        home_parser = subparsers.add_parser("home", help="ホームボタン")
        home_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )

        # screenshot サブコマンド
        screenshot_parser = subparsers.add_parser("screenshot", help="スクリーンショット撮影")
        screenshot_parser.add_argument(
            "--filename", "-f",
            help="出力ファイル名（未指定時は自動生成）"
        )
        screenshot_parser.add_argument(
            "--directory", "-dir",
            help="保存ディレクトリ（未指定時はデフォルト）"
        )
        screenshot_parser.add_argument(
            "--format", "-fmt",
            choices=["png", "jpg"],
            default="png",
            help="画像形式（デフォルト: png）"
        )
        screenshot_parser.add_argument(
            "--quality", "-q",
            type=int,
            default=95,
            help="JPEG品質 1-100（デフォルト: 95）"
        )
        screenshot_parser.add_argument(
            "--burst", "-b",
            type=int,
            help="バースト撮影の枚数"
        )
        screenshot_parser.add_argument(
            "--interval", "-i",
            type=float,
            default=1.0,
            help="バースト撮影の間隔（秒、デフォルト: 1.0）"
        )
        screenshot_parser.add_argument(
            "--device", "-d",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )

        # record サブコマンド
        record_parser = subparsers.add_parser("record", help="画面録画")
        record_parser.add_argument(
            "--duration", "-d",
            type=int,
            default=30,
            help="録画時間（秒、0=手動停止、デフォルト: 30）"
        )
        record_parser.add_argument(
            "--filename", "-f",
            help="出力ファイル名（未指定時は自動生成）"
        )
        record_parser.add_argument(
            "--directory", "-dir",
            help="保存ディレクトリ（未指定時はデフォルト）"
        )
        record_parser.add_argument(
            "--manual", "-m",
            action="store_true",
            help="手動停止モード（Ctrl+Cで停止）"
        )
        record_parser.add_argument(
            "--device", "-dev",
            help="対象デバイスID（未指定時は最初のデバイス）"
        )

        return parser

    def run(self, args: Optional[list] = None) -> int:
        """CLIアプリケーションを実行
        
        Args:
            args: コマンドライン引数（テスト用）
            
        Returns:
            終了コード（0=成功、1=エラー）
        """
        parser = self.create_parser()
        
        # 引数がない場合はヘルプを表示
        if args is None:
            args = sys.argv[1:]
        
        if not args:
            parser.print_help()
            return 0
            
        parsed_args = parser.parse_args(args)
        
        try:
            # サブコマンドに応じて処理を実行
            if parsed_args.command == "devices":
                return self.device_command.execute(parsed_args)
            elif parsed_args.command in ["up", "down", "left", "right"]:
                # 方向キーコマンドの場合、argsにkeyを設定
                parsed_args.key = parsed_args.command
                return self.direction_command.execute(parsed_args)
            elif parsed_args.command in ["select", "back", "home"]:
                # ボタンコマンドの場合、argsにkeyを設定（Android TV必須キーのみ）
                parsed_args.key = parsed_args.command
                return self.button_command.execute(parsed_args)
            elif parsed_args.command == "screenshot":
                return self.screenshot_command.execute(parsed_args)
            elif parsed_args.command == "record":
                return self.record_command.execute(parsed_args)
            else:
                parser.print_help()
                return 0
                
        except KeyboardInterrupt:
            self.formatter.print_error("操作がキャンセルされました")
            return 1
        except Exception as e:
            self.formatter.print_error(f"予期しないエラーが発生しました: {e}")
            return 1


def main() -> int:
    """メイン関数"""
    cli = RemoconCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
