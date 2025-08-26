# Remote Control Use Case 設計書

## 概要
Android TVのリモコン操作機能を提供するユースケース

## 責務
- 方向キー操作の実行
- 基本ボタン操作の実行
- 操作結果の返却
- 操作ログの記録

## インターフェース

### 入力
```python
@dataclass
class RemoteCommandDTO:
    command_type: str  # 'direction', 'button'
    key: str          # 'up', 'down', 'left', 'right', 'select', 'back', 'home'
    timestamp: datetime
```

### 出力
```python
@dataclass
class CommandResultDTO:
    success: bool
    message: str
    execution_time: float
    timestamp: datetime
```

## メソッド仕様

### execute_direction_key(command: RemoteCommandDTO) -> CommandResultDTO
**目的**: 方向キーの操作を実行
**処理フロー**:
1. コマンドバリデーション
2. ADBコマンド実行
3. 実行結果の確認
4. ログ記録
5. 結果返却

### execute_button(command: RemoteCommandDTO) -> CommandResultDTO
**目的**: ボタン操作を実行
**処理フロー**:
1. コマンドバリデーション
2. ADBコマンド実行
3. 実行結果の確認
4. ログ記録
5. 結果返却

## 依存関係
- DeviceRepository: デバイス操作
- LogRepository: ログ記録
- CommandValidator: バリデーション

## 例外処理
- InvalidCommandException: 無効なコマンド
- DeviceNotConnectedException: デバイス未接続
- AdbExecutionException: ADB実行エラー

## テストケース
- 正常系: 各キー操作の成功
- 異常系: デバイス未接続時のエラー
- 異常系: 無効なコマンド入力時のエラー
