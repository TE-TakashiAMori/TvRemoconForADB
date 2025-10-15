"""
ADB Gateway の実装
Android Debug Bridge (ADB) との通信を担当するインフラストラクチャ層のゲートウェイ
"""
import re
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


class AdbGatewayException(Exception):
    """AdbGateway関連の基底例外クラス"""
    pass


class AdbNotInstalledException(AdbGatewayException):
    """ADB未インストール例外"""
    pass


class DeviceNotConnectedException(AdbGatewayException):
    """デバイス未接続例外"""
    pass


class AdbCommandTimeoutException(AdbGatewayException):
    """ADBコマンドタイムアウト例外"""
    pass


class AdbPermissionException(AdbGatewayException):
    """ADB権限例外"""
    pass


@dataclass
class AdbResult:
    """ADBコマンド実行結果"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    command: str


class AdbGateway:
    """ADB通信ゲートウェイ"""
    
    # エラーパターン
    ERROR_PATTERNS = {
        'device_not_found': r'error: device .* not found',
        'no_devices': r'error: no devices/emulators found',
        'unauthorized': r'error: device unauthorized',
        'offline': r'error: device offline',
        'permission_denied': r'Permission denied'
    }
    
    def __init__(self, adb_path: str = "adb"):
        """ADBパスの設定"""
        self.adb_path = adb_path
        self.command_timeout = 30  # デフォルトタイムアウト（秒）
        self.connection_retry = 3  # リトライ回数
        self.retry_delay = 1.0     # リトライ間隔（秒）
    
    def is_device_connected(self) -> bool:
        """デバイス接続状態の確認"""
        devices = self.get_connected_devices()
        return len(devices) > 0
    
    def get_connected_devices(self) -> List[str]:
        """接続済みデバイス一覧の取得"""
        result = self._execute_adb_command(["devices"])
        
        if not result.success:
            return []
        
        devices = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines[1:]:  # "List of devices attached"をスキップ
            if line.strip() and '\t' in line:
                device_id, status = line.split('\t')
                if status.strip() == 'device':
                    devices.append(device_id.strip())
        
        return devices
    
    def execute_input_command(self, keycode: str) -> AdbResult:
        """入力コマンドの実行"""
        command = ["shell", "input", "keyevent", keycode]
        return self._execute_adb_command_with_retry(command)
    
    def capture_screenshot(self, device_id: str, local_path: str) -> AdbResult:
        """スクリーンショットの取得
        
        Args:
            device_id: デバイスID
            local_path: ローカル保存パス
        """
        # デバイス上の一時パス
        temp_device_path = "/sdcard/temp_screenshot.png"
        
        # デバイス上でスクリーンショット撮影
        screenshot_command = ["shell", "screencap", "-p", temp_device_path]
        screenshot_result = self._execute_adb_command_with_retry(screenshot_command)
        
        if not screenshot_result.success:
            return screenshot_result
        
        # ローカルにプル
        pull_result = self.pull_file(temp_device_path, local_path)
        
        # デバイス上の一時ファイル削除
        self.remove_file(temp_device_path)
        
        return pull_result
    
    def pull_file(self, device_path: str, local_path: str) -> AdbResult:
        """ファイルのプル（デバイス→ローカル）"""
        command = ["pull", device_path, local_path]
        return self._execute_adb_command_with_retry(command)
    
    def remove_file(self, device_path: str) -> AdbResult:
        """デバイス上のファイル削除"""
        command = ["shell", "rm", device_path]
        return self._execute_adb_command_with_retry(command)
    
    def execute_shell_command(self, shell_command: str) -> AdbResult:
        """シェルコマンドの実行"""
        command = ["shell", shell_command]
        return self._execute_adb_command_with_retry(command)
    
    def _execute_adb_command_with_retry(self, command: List[str]) -> AdbResult:
        """リトライ付きADBコマンド実行"""
        last_result = None
        
        for attempt in range(self.connection_retry):
            try:
                result = self._execute_adb_command(command)
                
                if result.success:
                    return result
                
                # デバイス関連エラーの場合はリトライ
                if self._is_retriable_error(result.stderr):
                    last_result = result
                    if attempt < self.connection_retry - 1:
                        time.sleep(self.retry_delay)
                        continue
                else:
                    # リトライ不可エラーの場合は即座に返却
                    return result
                    
            except (DeviceNotConnectedException, AdbCommandTimeoutException) as e:
                if attempt < self.connection_retry - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e
        
        return last_result or AdbResult(
            success=False,
            stdout="",
            stderr="Max retry attempts exceeded",
            return_code=-1,
            execution_time=0.0,
            command=" ".join([self.adb_path] + command)
        )
    
    def _execute_adb_command(self, command: List[str]) -> AdbResult:
        """ADBコマンドの実行"""
        full_command = [self.adb_path] + command
        start_time = time.time()
        
        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self.command_timeout
            )
            
            execution_time = time.time() - start_time
            
            # エラーパターンチェック
            if result.returncode != 0:
                self._check_and_raise_exceptions(result.stderr)
            
            return AdbResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                command=" ".join(full_command)
            )
            
        except FileNotFoundError:
            raise AdbNotInstalledException(f"ADB not found at path: {self.adb_path}")
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            raise AdbCommandTimeoutException(
                f"ADB command timed out after {self.command_timeout} seconds"
            )
    
    def _check_and_raise_exceptions(self, stderr: str) -> None:
        """エラーメッセージから適切な例外を発生"""
        if re.search(self.ERROR_PATTERNS['no_devices'], stderr):
            raise DeviceNotConnectedException("No devices/emulators found")
        
        if re.search(self.ERROR_PATTERNS['device_not_found'], stderr):
            raise DeviceNotConnectedException("Device not found")
        
        if re.search(self.ERROR_PATTERNS['unauthorized'], stderr):
            raise AdbPermissionException("Device unauthorized")
        
        if re.search(self.ERROR_PATTERNS['permission_denied'], stderr):
            raise AdbPermissionException("Permission denied")
    
    def _is_retriable_error(self, stderr: str) -> bool:
        """リトライ可能なエラーかどうかの判定"""
        retriable_patterns = [
            self.ERROR_PATTERNS['offline'],
            'device offline'
        ]
        
        for pattern in retriable_patterns:
            if re.search(pattern, stderr):
                return True
        
        return False
