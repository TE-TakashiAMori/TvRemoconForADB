"""AdbDeviceRepository - DeviceRepositoryの具象実装

このモジュールはAdbGatewayを使用してDeviceRepositoryを実装します。
Clean ArchitectureでのInfrastructure層として、
ドメイン層のRepositoryインターフェースを具体的に実装します。
"""

from datetime import datetime
from typing import List, Optional

from remocon_for_adb.domain.entities.android_device import AndroidDevice, DeviceStatus
from remocon_for_adb.domain.entities.remote_command import RemoteCommand
from remocon_for_adb.domain.repositories.device_repository import (
    DeviceRepository,
    DeviceConnectionError,
)
from remocon_for_adb.infrastructure.gateways.adb_gateway import (
    AdbGateway,
    DeviceNotConnectedException,
)


class AdbDeviceRepository(DeviceRepository):
    """AdbGatewayを使用したDeviceRepositoryの実装"""

    def __init__(self, adb_gateway: AdbGateway):
        """リポジトリを初期化

        Args:
            adb_gateway: ADB操作を行うゲートウェイ
        """
        self._adb_gateway = adb_gateway
        self._devices: List[AndroidDevice] = []

    def get_connected_devices(self) -> List[AndroidDevice]:
        """接続されているAndroidデバイス一覧を取得

        Returns:
            接続されているAndroidDeviceのリスト

        Raises:
            DeviceConnectionError: デバイス取得に失敗した場合
        """
        try:
            device_ids = self._adb_gateway.get_connected_devices()
            devices = []

            for device_id in device_ids:
                device = AndroidDevice(
                    device_id=device_id,
                    device_name=f"Android Device ({device_id})",
                    status=DeviceStatus.CONNECTED,
                    last_seen=datetime.now(),
                )
                devices.append(device)

            self._devices = devices
            return devices.copy()

        except DeviceNotConnectedException as e:
            raise DeviceConnectionError(f"デバイス一覧の取得に失敗しました: {e}")

    def get_device_by_id(self, device_id: str) -> Optional[AndroidDevice]:
        """指定されたIDのデバイスを取得

        Args:
            device_id: デバイスID

        Returns:
            該当するAndroidDevice、見つからない場合はNone
        """
        # まず内部のデバイスリストから検索
        for device in self._devices:
            if device.device_id == device_id:
                return device

        # 見つからない場合は再検索
        try:
            devices = self.get_connected_devices()
            for device in devices:
                if device.device_id == device_id:
                    return device
        except DeviceConnectionError:
            pass

        return None

    def is_device_available(self, device_id: str) -> bool:
        """デバイスが利用可能かどうかを確認

        Args:
            device_id: デバイスID

        Returns:
            デバイスが利用可能な場合True
        """
        try:
            # 接続されているデバイス一覧を取得してチェック
            connected_device_ids = self._adb_gateway.get_connected_devices()
            return device_id in connected_device_ids
        except DeviceNotConnectedException:
            return False

    def update_device_status(self, device_id: str, status: DeviceStatus) -> None:
        """デバイスのステータスを更新

        Args:
            device_id: デバイスID
            status: 新しいステータス
        """
        for device in self._devices:
            if device.device_id == device_id:
                device.update_status(status)
                break

    def refresh_device_list(self) -> None:
        """デバイス一覧を再取得して更新"""
        try:
            self.get_connected_devices()
        except DeviceConnectionError:
            # エラーが発生した場合は内部リストをクリア
            self._devices.clear()

    def execute_command(self, device_id: str, command: RemoteCommand) -> bool:
        """指定されたデバイスでコマンドを実行

        Args:
            device_id: デバイスID
            command: 実行するリモートコマンド

        Returns:
            コマンド実行が成功した場合True

        Raises:
            DeviceConnectionError: デバイス接続エラーまたはコマンド実行失敗
        """
        try:
            # デバイスが利用可能かチェック
            if not self.is_device_available(device_id):
                raise DeviceConnectionError(f"デバイス {device_id} は利用できません")

            # コマンドを実行
            # AdbGatewayは現在のプライマリデバイスにコマンドを送信
            result = self._adb_gateway.execute_input_command(command.key_code)

            return result.success

        except DeviceNotConnectedException as e:
            raise DeviceConnectionError(f"コマンド実行に失敗しました: {e}")

    def capture_screenshot(self, device_id: str, output_path: str) -> bool:
        """スクリーンショットを撮影

        Args:
            device_id: デバイスID
            output_path: 出力ファイルパス

        Returns:
            撮影が成功した場合True

        Raises:
            DeviceConnectionError: デバイス接続エラーまたは撮影失敗
        """
        try:
            # デバイスが利用可能かチェック
            if not self.is_device_available(device_id):
                raise DeviceConnectionError(f"デバイス {device_id} は利用できません")

            # スクリーンショットを撮影
            result = self._adb_gateway.capture_screenshot(device_id, output_path)

            return result.success

        except DeviceNotConnectedException as e:
            raise DeviceConnectionError(f"スクリーンショット撮影に失敗しました: {e}")

    def start_screen_record(self, device_id: str, local_path: str, duration: int = 0) -> bool:
        """画面録画を開始

        Args:
            device_id: デバイスID
            local_path: 保存先パス
            duration: 録画時間（秒）、0=手動停止モード

        Returns:
            開始が成功した場合True

        Raises:
            DeviceConnectionError: デバイス接続エラーまたは録画開始失敗
        """
        try:
            # デバイスが利用可能かチェック
            if not self.is_device_available(device_id):
                raise DeviceConnectionError(f"デバイス {device_id} は利用できません")

            # 録画を開始
            success = self._adb_gateway.start_screen_record(device_id, local_path, duration)

            return success

        except DeviceNotConnectedException as e:
            raise DeviceConnectionError(f"画面録画開始に失敗しました: {e}")

    def stop_screen_record(self, device_id: str) -> bool:
        """画面録画を停止

        Args:
            device_id: デバイスID

        Returns:
            停止が成功した場合True

        Raises:
            DeviceConnectionError: デバイス接続エラーまたは録画停止失敗
        """
        try:
            # デバイスが利用可能かチェック
            if not self.is_device_available(device_id):
                raise DeviceConnectionError(f"デバイス {device_id} は利用できません")

            # 録画を停止
            success = self._adb_gateway.stop_screen_record(device_id)
            
            if success:
                # ファイルをプル
                # Note: local_pathはstart_screen_recordで指定されているため、
                # AdbGatewayが内部で管理している前提
                # 実際の実装ではpull処理も必要
                pass

            return success

        except DeviceNotConnectedException as e:
            raise DeviceConnectionError(f"画面録画停止に失敗しました: {e}")

    def is_screen_recording(self, device_id: str) -> bool:
        """画面録画中かどうかを確認

        Args:
            device_id: デバイスID

        Returns:
            録画中の場合True

        Raises:
            DeviceConnectionError: デバイス接続エラー
        """
        try:
            # デバイスが利用可能かチェック
            if not self.is_device_available(device_id):
                return False

            # 録画状態を確認
            return self._adb_gateway.is_screen_recording(device_id)

        except DeviceNotConnectedException:
            return False
