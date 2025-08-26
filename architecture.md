# RemoconForAdb アーキテクチャ設計書

## Clean Architecture 概要

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

## レイヤー構成

### 1. Presentation Layer (プレゼンテーション層)
- **CLI Interface**: コマンドライン引数の受け取り
- **Command Parser**: コマンド解析とバリデーション
- **Output Formatter**: 結果の表示形式制御

### 2. Application Layer (アプリケーション層)
- **Use Cases**: ビジネスロジックの実行
- **Controllers**: ユースケースの呼び出し制御
- **DTOs**: データ転送オブジェクト

### 3. Domain Layer (ドメイン層)
- **Entities**: ビジネスエンティティ
- **Repository Interfaces**: データアクセスの抽象化
- **Domain Services**: ドメインロジック

### 4. Infrastructure Layer (インフラストラクチャ層)
- **ADB Gateway**: ADB通信の実装
- **File System Gateway**: ファイル操作の実装
- **Logger**: ログ出力の実装

## モジュール構成

```
remocon_for_adb/
├── presentation/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── command_parser.py
│   └── formatters/
│       ├── __init__.py
│       └── output_formatter.py
├── application/
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── remote_control_use_case.py
│   │   ├── screenshot_use_case.py
│   │   ├── logging_use_case.py
│   │   └── automation_use_case.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── remote_controller.py
│   └── dtos/
│       ├── __init__.py
│       └── command_dto.py
├── domain/
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── android_device.py
│   │   ├── remote_command.py
│   │   └── operation_log.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── device_repository.py
│   │   ├── log_repository.py
│   │   └── script_repository.py
│   └── services/
│       ├── __init__.py
│       └── command_validator.py
└── infrastructure/
    ├── gateways/
    │   ├── __init__.py
    │   ├── adb_gateway.py
    │   └── file_gateway.py
    ├── repositories/
    │   ├── __init__.py
    │   ├── device_repository_impl.py
    │   ├── log_repository_impl.py
    │   └── script_repository_impl.py
    └── config/
        ├── __init__.py
        └── settings.py
```

## 依存関係の方向

```
Presentation → Application → Domain ← Infrastructure
```

- Presentation層はApplication層に依存
- Application層はDomain層に依存
- Infrastructure層はDomain層に依存
- Domain層は他の層に依存しない（依存性逆転の原則）

## データフロー

### 1. コマンド実行フロー
```
CLI Input → Command Parser → Controller → Use Case → Repository → Gateway → ADB
```

### 2. スクリーンショット実行フロー
```
CLI Input → Screenshot Use Case → Device Repository → ADB Gateway → File Gateway
```

### 3. ログ記録フロー
```
Command Execution → Logging Use Case → Log Repository → File Gateway
```

## エラーハンドリング戦略

### 1. 例外の分類
- **Domain Exceptions**: ビジネスルール違反
- **Infrastructure Exceptions**: 外部システムエラー
- **Application Exceptions**: アプリケーション固有エラー

### 2. エラー伝播
```
Infrastructure → Domain → Application → Presentation
```

### 3. エラー処理方針
- 各層で適切な例外変換
- ユーザーフレンドリーなエラーメッセージ
- ログによるデバッグ情報記録

## テスト戦略

### 1. 単体テスト
- 各層のクラス単位でのテスト
- モックを使用した依存関係の分離

### 2. 統合テスト
- ADB接続を含むエンドツーエンドテスト
- ファイル操作を含む永続化テスト

### 3. テスト構成
```
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── integration/
│   ├── adb_integration_test.py
│   └── file_integration_test.py
└── e2e/
    └── cli_e2e_test.py
```

## 設定管理

### 1. 設定ファイル
- YAML形式での設定管理
- 環境別設定対応
- デフォルト値の提供

### 2. 設定項目
- ADB接続設定
- ログ出力設定
- スクリーンショット保存設定
- スクリプト保存設定
