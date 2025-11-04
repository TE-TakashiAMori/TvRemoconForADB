"""
CLI コマンドハンドラー
各サブコマンドの処理を担当
"""

import argparse
import time
import signal
import sys
from typing import Optional

from remocon_for_adb.application.dtos.command_dto import RemoteCommandDTO
from remocon_for_adb.application.dtos.command_dto import ScreenshotCommandDTO
from remocon_for_adb.application.dtos.command_dto import ScreenRecordCommandDTO
from remocon_for_adb.application.use_cases.remote_control_use_case import RemoteControlUseCase
from remocon_for_adb.application.use_cases.screenshot_use_case import ScreenshotUseCase
from remocon_for_adb.application.use_cases.screen_record_use_case import ScreenRecordUseCase
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
            # コマンドDTOを作成（長押し対応）
            command_dto = RemoteCommandDTO(
                command_type="direction",
                key=args.key,
                is_long_press=getattr(args, 'long_press', False)
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
            # コマンドDTOを作成（長押し対応）
            command_dto = RemoteCommandDTO(
                command_type="button",
                key=args.key,
                is_long_press=getattr(args, 'long_press', False)
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
                filename=args.filename,
                directory=getattr(args, 'directory', None),
                format=getattr(args, 'format', 'png'),
                quality=getattr(args, 'quality', 95)
            )

            # バースト撮影かどうか判定
            if hasattr(args, 'burst') and args.burst and args.burst > 1:
                # バースト撮影
                self.formatter.print_info(f"バースト撮影を開始します ({args.burst}枚)...")
                results = self.screenshot_use_case.capture_burst_screenshots(
                    command_dto, 
                    count=args.burst,
                    interval=getattr(args, 'interval', 1.0)
                )
                
                # 結果を表示
                success_count = sum(1 for r in results if r.success)
                self.formatter.print_info(f"バースト撮影完了: {success_count}/{len(results)}枚成功")
                
                for i, result in enumerate(results, 1):
                    if result.success:
                        self.formatter.print_screenshot_result(
                            success=True,
                            filepath=result.filepath,
                            file_size=result.filesize,
                            execution_time=result.execution_time,
                            prefix=f"[{i}] "
                        )
                    else:
                        self.formatter.print_error(f"[{i}] 撮影失敗: {result.message}")
                
                return 0 if success_count > 0 else 1
            else:
                # 通常撮影
                self.formatter.print_info("スクリーンショットを撮影しています...")
                result = self.screenshot_use_case.capture_screenshot(command_dto)

            # 結果を表示
            if result.success:
                self.formatter.print_screenshot_result(
                    success=True,
                    filepath=result.filepath,
                    file_size=result.filesize,
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


class RecordCommand(BaseCommand):
    """画面録画コマンド"""

    def __init__(self, screen_record_use_case: ScreenRecordUseCase, formatter: ConsoleFormatter):
        """画面録画コマンドを初期化
        
        Args:
            screen_record_use_case: 画面録画ユースケース
            formatter: コンソール出力フォーマッター
        """
        super().__init__(formatter)
        self.screen_record_use_case = screen_record_use_case
        self.stop_requested = False

    def execute(self, args: argparse.Namespace) -> int:
        """画面録画コマンドを実行
        
        Args:
            args: 解析済みコマンドライン引数
            
        Returns:
            終了コード
        """
        try:
            # 手動停止モードの判定
            manual_mode = getattr(args, 'manual', False) or args.duration == 0
            
            # コマンドDTOを作成
            command_dto = ScreenRecordCommandDTO(
                duration=args.duration if not manual_mode else 0,
                filename=getattr(args, 'filename', None),
                directory=getattr(args, 'directory', None),
                format='mp4',
                manual_mode=manual_mode
            )

            if manual_mode:
                # 手動停止モード
                return self._execute_manual_mode(command_dto)
            else:
                # 時間指定モード
                return self._execute_timed_mode(command_dto)

        except Exception as e:
            self.formatter.print_error(f"画面録画コマンドエラー: {e}")
            return 1

    def _execute_manual_mode(self, command_dto: ScreenRecordCommandDTO) -> int:
        """手動停止モードで録画
        
        Args:
            command_dto: 録画コマンドDTO
            
        Returns:
            終了コード
        """
        self.formatter.print_info("手動停止モードで録画を開始します（Ctrl+C で停止）...")
        
        # Ctrl+Cハンドラー設定
        def signal_handler(sig, frame):
            self.stop_requested = True
            self.formatter.print_info("\n録画停止を受け付けました...")
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # 録画開始
        start_result = self.screen_record_use_case.start_recording(command_dto)
        
        if not start_result.success:
            self.formatter.print_error(f"録画開始に失敗しました: {start_result.message}")
            return 1
        
        self.formatter.print_success("録画を開始しました")
        
        # 停止待機（タイマー表示付き）
        start_time = time.time()
        try:
            while not self.stop_requested:
                elapsed = time.time() - start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                
                # 経過時間表示（180秒=3分制限）
                remaining = 180 - int(elapsed)
                if remaining <= 0:
                    self.formatter.print_warning("\n最大録画時間（3分）に達しました")
                    break
                
                # 進捗表示
                sys.stdout.write(f"\r録画中... {minutes:02d}:{seconds:02d} / 03:00")
                sys.stdout.flush()
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            pass
        
        # 録画停止
        self.formatter.print_info("\n録画を停止しています...")
        stop_result = self.screen_record_use_case.stop_recording()
        
        if stop_result.success:
            self.formatter.print_success(f"録画完了: {stop_result.filepath}")
            self.formatter.print_info(
                f"録画時間: {stop_result.duration:.1f}秒 / "
                f"ファイルサイズ: {stop_result.filesize / (1024*1024):.2f}MB"
            )
            return 0
        else:
            self.formatter.print_error(f"録画停止に失敗しました: {stop_result.message}")
            return 1

    def _execute_timed_mode(self, command_dto: ScreenRecordCommandDTO) -> int:
        """時間指定モードで録画
        
        Args:
            command_dto: 録画コマンドDTO
            
        Returns:
            終了コード
        """
        duration = command_dto.duration
        self.formatter.print_info(f"{duration}秒間の録画を開始します...")
        
        # 録画開始
        start_result = self.screen_record_use_case.start_recording(command_dto)
        
        if not start_result.success:
            self.formatter.print_error(f"録画開始に失敗しました: {start_result.message}")
            return 1
        
        self.formatter.print_success("録画を開始しました")
        
        # 待機（進捗表示付き）
        for elapsed in range(duration + 1):
            if elapsed <= duration:
                remaining = duration - elapsed
                progress = (elapsed / duration) * 100
                
                # プログレスバー表示
                bar_length = 30
                filled = int(bar_length * elapsed / duration)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                sys.stdout.write(
                    f"\r録画中... [{bar}] {progress:.0f}% "
                    f"({elapsed}/{duration}秒) "
                )
                sys.stdout.flush()
                time.sleep(1)
        
        # 録画停止
        self.formatter.print_info("\n録画を停止しています...")
        stop_result = self.screen_record_use_case.stop_recording()
        
        if stop_result.success:
            self.formatter.print_success(f"録画完了: {stop_result.filepath}")
            self.formatter.print_info(
                f"録画時間: {stop_result.duration:.1f}秒 / "
                f"ファイルサイズ: {stop_result.filesize / (1024*1024):.2f}MB"
            )
            return 0
        else:
            self.formatter.print_error(f"録画停止に失敗しました: {stop_result.message}")
            return 1
