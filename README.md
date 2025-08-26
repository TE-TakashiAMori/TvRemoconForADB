# RemoconForAdb

Ubuntu環境でADB経由でAndroid TVをリモコン操作するコマンドラインアプリケーション

## 🎯 プロジェクト概要

Android TVデバイスをU```

## 📋 使用方法

### CLI版（コマンドライン）

#### 基本操作環境からADB（Android Debug Bridge）を使用してリモコン操作できるコマンドラインツールです。

## ✨ 主な機能

- 🎮 **基本リモコン操作**: 方向キー（上下左右）、決定、戻る、ホームボタン
- � **CLI・GUI両対応**: コマンドライン版とグラフィカル版を提供
- �📸 **スクリーンショット機能**: Android TVの画面キャプチャと保存
- 📝 **操作ログ機能**: 実行したコマンドの記録と参照
- 🤖 **自動化機能**: 操作の記録・再生とスクリプト実行

## 🏗️ アーキテクチャ

Clean Architectureを採用した4層構造：

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   CLI Interface │  │  Command Parser │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │   Use Cases     │  │   Controllers   │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │    Entities     │  │   Repositories  │                │
│  │                 │  │   (Interfaces)  │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐                │
│  │ ADB Gateway     │  │  File System    │                │
│  │                 │  │    Gateway      │                │
│  └─────────────────┘  └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 インストール方法

### 前提条件
- Ubuntu Linux
- Python 3.8以上
- ADB (Android Debug Bridge)

### ADBのインストール
```bash
sudo apt update
sudo apt install android-tools-adb
```

### アプリケーションのインストール
```bash
git clone https://github.com/tinygc/RemoconForAdb.git
cd RemoconForAdb
pip install -r requirements.txt
pip install -e .
```

### インストール確認
```bash
# コマンドが正常にインストールされているか確認
remocon-adb --help

# 期待される出力: コマンドのヘルプメッセージが表示される
```

## � Android TV 設定

### デベロッパーオプションの有効化
1. Android TVの「設定」→「端末情報」
2. 「ビルド」を7回タップしてデベロッパーオプションを有効化

### ADBデバッグの有効化
1. 「設定」→「端末設定」→「開発者向けオプション」
2. 「USBデバッグ」をONにする
3. 「ネットワーク経由でのADBデバッグ」をONにする（WiFi接続時）

### 接続確認
```bash
# USB接続の場合
adb devices

# ネットワーク接続の場合（Android TVのIPアドレスを確認してから）
adb connect [Android TVのIPアドレス]:5555
adb devices

# 接続されたデバイス一覧をremocon-adbで確認
remocon-adb devices
```

## �📋 使用方法

### 基本操作
```bash
# 方向キー
remocon-adb up                # 上
remocon-adb down              # 下
remocon-adb left              # 左
remocon-adb right             # 右

# 基本ボタン
remocon-adb select            # 決定
remocon-adb back              # 戻る
remocon-adb home              # ホーム

# デバイス一覧表示
remocon-adb devices           # 接続中のデバイス一覧
```

#### 拡張機能
```bash
# スクリーンショット（開発中）
remocon-adb screenshot

# 使用方法の詳細表示
remocon-adb --help
remocon-adb up --help
remocon-adb select --help
```

### GUI版（グラフィカル）

#### 起動方法
```bash
# GUIアプリケーションを起動
remocon-adb-gui
```

#### 操作方法
- **マウス操作**: ボタンをクリックしてリモコン操作
- **キーボードショートカット**:
  - 矢印キー → 方向操作
  - Enter → 選択
  - Esc → 戻る
  - F1 → ホーム

#### GUI特徴
- 🎨 **直感的なリモコンデザイン**: 実際のリモコンを模したレイアウト
- 🔵 **リアルタイム状態表示**: デバイス接続状況とコマンド実行結果
- ⚡ **即座のフィードバック**: ボタン押下時の視覚効果
- 📱 **デバイス管理**: 複数デバイスの切り替えが簡単

### 実際の使用例
```bash
# 1. デバイス接続確認
$ remocon-adb devices
=== 接続デバイス (1台) ===
 1. 126492100000000B0000AA2F4C4 
    名前: Android Device (126492100000000B0000AA2F4C4)
    状態: CONNECTED

# 2. Android TVで上に移動
$ remocon-adb up
✓ 方向キー 'up' を送信しました
実行時間: 0.069秒

# 3. 決定ボタンを押す
$ remocon-adb select  
✓ ボタン 'select' を送信しました
実行時間: 0.067秒
```

## 🔧 開発環境

### 開発ツール
- **言語**: Python 3.8+
- **テストフレームワーク**: pytest
- **コードフォーマッター**: black
- **リンター**: flake8
- **型チェック**: mypy

### テスト実行
```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=remocon_for_adb --cov-report=html

# 特定のテスト実行
pytest tests/unit/domain/
```

## �️ トラブルシューティング

### コマンドが見つからない場合
```bash
# 1. インストール確認
pip list | grep remocon

# 2. 再インストール
pip uninstall remocon-for-adb
pip install -e .

# 3. PATHの確認
which remocon-adb
```

### デバイスが検出されない場合
```bash
# 1. ADB接続確認
adb devices

# 2. デバイスの権限確認（初回接続時は認証が必要）
# Android TV側で「このコンピュータからのUSBデバッグを常に許可する」をチェック

# 3. ネットワーク接続の場合はポート確認
adb connect [IPアドレス]:5555
```

### 権限エラーの場合
```bash
# udevルールの設定（必要に応じて）
sudo usermod -aG plugdev $USER
# 再ログインが必要
```

## �📈 開発進捗

### ✅ 完了
- [x] 要件定義書作成
- [x] アーキテクチャ設計書作成  
- [x] Clean Architecture 4層実装完了
  - [x] Domain層（エンティティとビジネスルール）
  - [x] Application層（ユースケースとDTO）  
  - [x] Infrastructure層（ADB Gateway実装）
  - [x] Presentation層（CLI・GUI Interface）
- [x] CLI版リモコン機能実装
  - [x] 方向キー操作（上下左右）
  - [x] ボタン操作（決定・戻る・ホーム）
  - [x] デバイス一覧表示
  - [x] シンプルなコマンド構造（`remocon-adb up`等）
- [x] GUI版リモコン機能実装
  - [x] リモコンパネル（十字キー・ボタン）
  - [x] デバイス管理パネル
  - [x] ステータス表示
  - [x] キーボードショートカット
  - [x] ダークテーマUI
- [x] テスト実装（カバレッジ90%以上）
- [x] 統合テスト完了（実機動作確認済み）

### 🚧 進行中  
- [ ] スクリーンショット機能の最終調整
- [ ] エラーハンドリングの改善
- [ ] ドキュメントの充実

### 📋 今後の予定
- [ ] 統合テスト実装
- [ ] E2Eテスト実装
- [ ] CLI インターフェース実装
- [ ] パッケージング
- [ ] ドキュメント整備

## 🤝 開発方針

- **TDD (Test Driven Development)** による実装
- **Clean Architecture** による設計
- **高いテストカバレッジ** の維持（80%以上）
- **継続的インテグレーション** の実装

## 📄 ライセンス

MIT License

## 👤 作者

- **作者**: TE-TakashiAMori
- **GitHub**: https://github.com/TE-TakashiAMori
- **メール**: takashi.a.mori@sony.com

## 🔗 関連リンク

- [要件定義書](requirements.md)
- [アーキテクチャ設計書](architecture.md)
- [設計書一覧](docs/)
