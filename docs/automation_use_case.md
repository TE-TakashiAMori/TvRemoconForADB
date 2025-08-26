# Automation Use Case 設計書

## 概要
操作の記録・再生による自動化機能を提供するユースケース

## 責務
- 操作の記録開始・停止
- 記録したスクリプトの保存
- スクリプトの実行
- スクリプトファイルの管理

## インターフェース

### 入力
```python
@dataclass
class AutomationCommandDTO:
    action: str  # 'record_start', 'record_stop', 'play', 'list', 'delete'
    script_name: Optional[str] = None
    delay_between_commands: float = 1.0  # 秒
    repeat_count: int = 1
```

@dataclass
class ScriptEntryDTO:
    command_type: str
    command_detail: str
    delay_after: float
    timestamp: datetime
```

### 出力
```python
@dataclass
class AutomationResultDTO:
    success: bool
    script_name: Optional[str]
    executed_commands: int
    total_execution_time: float
    message: str
    script_list: Optional[List[str]] = None
```

## メソッド仕様

### start_recording(script_name: str) -> bool
**目的**: 操作記録の開始
**処理フロー**:
1. 既存スクリプト名の重複確認
2. 記録状態のセット
3. 一時記録ファイルの作成
4. 記録開始の通知

### stop_recording() -> AutomationResultDTO
**目的**: 操作記録の停止
**処理フロー**:
1. 記録状態の確認
2. 一時ファイルからスクリプトファイルへの変換
3. 記録コマンド数の集計
4. 結果返却

### record_command(command: RemoteCommandDTO) -> bool
**目的**: 記録中のコマンドを記録
**処理フロー**:
1. 記録状態の確認
2. コマンドの記録ファイルへの追記
3. 前回コマンドからの時間差計算

### play_script(command: AutomationCommandDTO) -> AutomationResultDTO
**目的**: スクリプトの実行
**処理フロー**:
1. スクリプトファイルの存在確認
2. スクリプトの読み込み
3. コマンドの順次実行
4. リピート回数に応じた繰り返し
5. 実行結果の集計
6. 結果返却

### list_scripts() -> AutomationResultDTO
**目的**: 保存済みスクリプトの一覧表示
**処理フロー**:
1. スクリプトディレクトリの検索
2. スクリプトファイルの一覧取得
3. ファイル情報の取得
4. 結果返却

### delete_script(script_name: str) -> bool
**目的**: スクリプトの削除
**処理フロー**:
1. スクリプトファイルの存在確認
2. 削除確認
3. ファイル削除
4. 結果返却

## スクリプト形式

### ファイル形式
- JSON形式 (.json)
- メタデータ + コマンドリスト

### スクリプトファイル例
```json
{
  "metadata": {
    "name": "navigate_to_settings",
    "description": "Navigate to settings menu",
    "created_at": "2025-08-25T10:30:45.123456",
    "total_commands": 5,
    "estimated_duration": 12.5
  },
  "commands": [
    {
      "command_type": "button",
      "command_detail": "home",
      "delay_after": 2.0,
      "timestamp": "2025-08-25T10:30:45.123456"
    },
    {
      "command_type": "direction",
      "command_detail": "down",
      "delay_after": 1.0,
      "timestamp": "2025-08-25T10:30:47.456789"
    }
  ]
}
```

## 設定項目
- スクリプト保存ディレクトリ: `~/.remocon_for_adb/scripts/`
- 一時記録ファイル: `~/.remocon_for_adb/tmp/recording.tmp`
- デフォルト遅延時間: 1.0秒
- 最大リピート回数: 100回

## 依存関係
- ScriptRepository: スクリプト永続化
- RemoteControlUseCase: コマンド実行
- LogRepository: 実行ログ記録
- FileRepository: ファイル操作

## 例外処理
- ScriptNotFoundException: スクリプト未存在
- RecordingNotStartedException: 記録未開始
- AlreadyRecordingException: 記録中の重複開始
- ScriptExecutionException: スクリプト実行エラー
- InvalidScriptFormatException: 不正なスクリプト形式

## テストケース
- 正常系: 記録開始・停止の成功
- 正常系: スクリプト実行の成功
- 正常系: リピート実行の成功
- 正常系: スクリプト一覧表示の成功
- 異常系: 重複記録開始時のエラー
- 異常系: 存在しないスクリプト実行時のエラー
- 異常系: 不正なスクリプト形式のエラー
