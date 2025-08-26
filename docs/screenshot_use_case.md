# Screenshot Use Case 設計書

## 概要
Android TVの画面キャプチャ機能を提供するユースケース

## 責務
- スクリーンショットの取得
- 画像ファイルの保存
- ファイル名の生成
- 操作ログの記録

## インターフェース

### 入力
```python
@dataclass
class ScreenshotCommandDTO:
    filename: Optional[str] = None  # 指定なしの場合は自動生成
    timestamp: datetime = field(default_factory=datetime.now)
```

### 出力
```python
@dataclass
class ScreenshotResultDTO:
    success: bool
    filepath: str
    filesize: int
    message: str
    execution_time: float
    timestamp: datetime
```

## メソッド仕様

### capture_screenshot(command: ScreenshotCommandDTO) -> ScreenshotResultDTO
**目的**: スクリーンショットを取得して保存
**処理フロー**:
1. デバイス接続確認
2. ファイル名生成（未指定の場合）
3. ADBでスクリーンキャプチャ実行
4. ローカルへファイル転送
5. デバイス上の一時ファイル削除
6. ファイル情報取得
7. ログ記録
8. 結果返却

### generate_filename() -> str
**目的**: 自動ファイル名生成
**命名規則**: `screenshot_YYYYMMDD_HHMMSS.png`

## 設定項目
- 保存ディレクトリ: `~/remocon_screenshots/`
- ファイル形式: PNG
- 一時ファイルパス: `/sdcard/screenshot_temp.png`

## 依存関係
- DeviceRepository: デバイス操作
- FileRepository: ファイル保存
- LogRepository: ログ記録

## 例外処理
- DeviceNotConnectedException: デバイス未接続
- ScreenshotFailedException: キャプチャ失敗
- FileTransferException: ファイル転送エラー
- DiskSpaceException: ディスク容量不足

## テストケース
- 正常系: ファイル名指定ありの成功
- 正常系: ファイル名自動生成の成功
- 異常系: デバイス未接続時のエラー
- 異常系: ディスク容量不足時のエラー
- 異常系: 権限不足時のエラー
