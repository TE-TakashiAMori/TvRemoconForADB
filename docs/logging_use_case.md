# Logging Use Case 設計書

## 概要
操作ログの記録・参照機能を提供するユースケース

## 責務
- 操作ログの記録
- ログの表示・検索
- ログファイルの管理
- ログの出力形式制御

## インターフェース

### 入力
```python
@dataclass
class LogCommandDTO:
    action: str  # 'record', 'show', 'clear', 'search'
    log_entry: Optional[LogEntryDTO] = None
    search_query: Optional[str] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
```

@dataclass
class LogEntryDTO:
    timestamp: datetime
    command_type: str
    command_detail: str
    result: str
    execution_time: float
    device_id: str
```

### 出力
```python
@dataclass
class LogResultDTO:
    success: bool
    log_entries: List[LogEntryDTO]
    total_count: int
    message: str
```

## メソッド仕様

### record_log(log_entry: LogEntryDTO) -> bool
**目的**: 操作ログを記録
**処理フロー**:
1. ログエントリの検証
2. ログファイルへの追記
3. ログローテーション確認
4. 記録結果の返却

### show_logs(command: LogCommandDTO) -> LogResultDTO
**目的**: ログの表示
**処理フロー**:
1. 条件に応じたログフィルタリング
2. ログエントリの読み込み
3. 表示形式での整形
4. 結果返却

### clear_logs() -> bool
**目的**: ログのクリア
**処理フロー**:
1. 確認プロンプト
2. ログファイルのクリア
3. 結果返却

### search_logs(query: str, date_range: Optional[Tuple[datetime, datetime]]) -> LogResultDTO
**目的**: ログの検索
**処理フロー**:
1. 検索条件の解析
2. ログファイルの検索
3. マッチしたエントリの抽出
4. 結果返却

## ログ形式

### ファイル形式
- JSON Lines形式 (.jsonl)
- 1行1ログエントリ
- タイムスタンプ順でソート

### ログエントリ例
```json
{
  "timestamp": "2025-08-25T10:30:45.123456",
  "command_type": "direction",
  "command_detail": "up",
  "result": "success",
  "execution_time": 0.234,
  "device_id": "192.168.1.100:5555"
}
```

## 設定項目
- ログファイルパス: `~/.remocon_for_adb/logs/`
- ファイル名: `remocon_YYYYMMDD.jsonl`
- ローテーション: 日次
- 保持期間: 30日
- 最大ファイルサイズ: 10MB

## 依存関係
- LogRepository: ログ永続化
- FileRepository: ファイル操作
- ConfigService: 設定管理

## 例外処理
- LogFileNotFoundException: ログファイル未存在
- LogWriteException: ログ書き込みエラー
- DiskSpaceException: ディスク容量不足
- PermissionException: ファイルアクセス権限エラー

## テストケース
- 正常系: ログ記録の成功
- 正常系: ログ表示の成功
- 正常系: ログ検索の成功
- 正常系: ログクリアの成功
- 異常系: ディスク容量不足時のエラー
- 異常系: 権限不足時のエラー
