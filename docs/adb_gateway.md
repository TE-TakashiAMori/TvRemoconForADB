# ADB Gateway 設計書

## 概要
Android Debug Bridge (ADB) との通信を担当するインフラストラクチャ層のゲートウェイ

## 責務
- ADB コマンドの実行
- デバイス接続状態の管理
- ADB レスポンスの解析
- エラーハンドリング

## インターフェース

### メソッド仕様

```python
class AdbGateway:
    def __init__(self, adb_path: str = "adb"):
        """ADBパスの設定"""
        
    def is_device_connected(self) -> bool:
        """デバイス接続状態の確認"""
        
    def get_connected_devices(self) -> List[str]:
        """接続済みデバイス一覧の取得"""
        
    def execute_input_command(self, keycode: str) -> AdbResult:
        """入力コマンドの実行"""
        
    def capture_screenshot(self, device_path: str) -> AdbResult:
        """スクリーンショットの取得"""
        
    def pull_file(self, device_path: str, local_path: str) -> AdbResult:
        """ファイルのプル（デバイス→ローカル）"""
        
    def remove_file(self, device_path: str) -> AdbResult:
        """デバイス上のファイル削除"""
        
    def execute_shell_command(self, command: str) -> AdbResult:
        """シェルコマンドの実行"""
```

### データ構造

```python
@dataclass
class AdbResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    command: str
```

## ADBコマンドマッピング

### リモコン操作
```python
KEYCODE_MAPPING = {
    'up': 'KEYCODE_DPAD_UP',
    'down': 'KEYCODE_DPAD_DOWN', 
    'left': 'KEYCODE_DPAD_LEFT',
    'right': 'KEYCODE_DPAD_RIGHT',
    'select': 'KEYCODE_DPAD_CENTER',
    'back': 'KEYCODE_BACK',
    'home': 'KEYCODE_HOME'
}
```

### 実行コマンド例
```bash
# 方向キー
adb shell input keyevent KEYCODE_DPAD_UP

# スクリーンショット
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png ./screenshot.png
adb shell rm /sdcard/screenshot.png

# デバイス確認
adb devices
```

## エラーハンドリング

### ADB関連エラー
- **AdbNotInstalledException**: ADB未インストール
- **DeviceNotConnectedException**: デバイス未接続
- **AdbCommandTimeoutException**: コマンドタイムアウト
- **AdbPermissionException**: 権限エラー
- **AdbNetworkException**: ネットワークエラー

### エラー検出パターン
```python
ERROR_PATTERNS = {
    'device_not_found': r'error: device .* not found',
    'no_devices': r'error: no devices/emulators found',
    'unauthorized': r'error: device unauthorized',
    'offline': r'error: device offline',
    'permission_denied': r'Permission denied'
}
```

## 設定項目

### デフォルト設定
```python
DEFAULT_CONFIG = {
    'adb_path': 'adb',
    'command_timeout': 30,  # 秒
    'connection_retry': 3,
    'retry_delay': 1.0,     # 秒
    'screenshot_format': 'png',
    'temp_screenshot_path': '/sdcard/remocon_temp.png'
}
```

## 依存関係
- subprocess: コマンド実行
- pathlib: ファイルパス操作
- typing: 型ヒント
- logging: ログ出力

## セキュリティ考慮事項
- コマンドインジェクション対策
- ファイルパスの検証
- 権限の最小化
- ログでの機密情報マスク

## パフォーマンス考慮事項
- コマンド実行のタイムアウト設定
- 大容量ファイル転送の進捗表示
- 同期/非同期実行の選択
- リソース使用量の監視

## テストケース

### 単体テスト
- 各コマンド実行の成功パターン
- エラーレスポンスの適切な解析
- タイムアウト処理の確認
- 接続状態確認の正確性

### 統合テスト
- 実際のAndroidデバイスとの通信
- 長時間実行での安定性
- 複数コマンドの連続実行
- エラー復旧の動作確認

## ログ出力

### ログレベル
- **DEBUG**: 実行コマンドの詳細
- **INFO**: 操作の成功・失敗
- **WARNING**: リトライ実行
- **ERROR**: 回復不可能なエラー

### ログ形式例
```
[2025-08-25 10:30:45] INFO - ADB command executed: adb shell input keyevent KEYCODE_DPAD_UP
[2025-08-25 10:30:45] DEBUG - Command result: success=True, return_code=0, time=0.234s
[2025-08-25 10:30:46] WARNING - Device not responding, retrying... (attempt 2/3)
[2025-08-25 10:30:47] ERROR - ADB command failed: device not found
```
