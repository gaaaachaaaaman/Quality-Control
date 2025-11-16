# Web Quality Analyzer Pro - プロジェクト構造完全ガイド

## 📁 最終的なディレクトリ構造

```
web-quality-analyzer/
│
├── README.md                          # プロジェクト説明
├── requirements.txt                   # Pythonパッケージ一覧
├── runtime.txt                        # Python バージョン（デプロイ用）
├── Procfile                          # Herokuデプロイ設定
├── render.yaml                       # Renderデプロイ設定
├── .gitignore                        # Git除外ファイル
│
├── analyzer.py                       # 🔥 コア分析エンジン（Phase 1）
├── app.py                           # 🌐 Flask Webサーバー（Phase 2）
├── cli.py                           # 💻 CLI インターフェース（Phase 3）
├── batch_analyze.py                 # 📊 一括分析スクリプト（Phase 3）
├── test_analyzer.py                 # ✅ テストスクリプト
│
├── templates/                        # HTMLテンプレート
│   └── index.html                   # 🎨 モバイルフレンドリーUI（Phase 2）
│
├── static/                          # 静的ファイル（PWA用）
│   ├── manifest.json                # PWAマニフェスト（Phase 3）
│   ├── sw.js                        # Service Worker（Phase 3）
│   ├── icon-192.png                 # アプリアイコン 192x192
│   └── icon-512.png                 # アプリアイコン 512x512
│
├── uploads/                         # アップロードファイル一時保存
├── reports/                         # 生成されたレポート保存先
│
└── docs/                            # ドキュメント
    ├── phase1.md                    # Phase 1 ガイド
    ├── phase2.md                    # Phase 2 ガイド
    ├── phase3.md                    # Phase 3 ガイド
    └── quickstart.md                # クイックスタート
```

---

## 📄 各ファイルの詳細と役割

### 必須ファイル（Phase 1 - 最小構成）

#### `requirements.txt`
```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
Pillow>=10.0.0
```

**役割**: 必要なPythonパッケージを定義  
**使用タイミング**: `pip install -r requirements.txt`

---

#### `analyzer.py`
**役割**: Web品質分析の核心エンジン  
**主要クラス**:
- `Issue`: 検出された問題を表現
- `QualityReport`: 分析結果レポート
- `WebQualityAnalyzer`: 分析実行エンジン

**分析項目**:
1. 基本構造（DOCTYPE, lang属性など）
2. SEO（title, meta description, OGPなど）
3. アクセシビリティ（alt, labelなど）
4. パフォーマンス（CSS/JSファイル数など）
5. デザイン（viewport, faviconなど）
6. セキュリティ（HTTPS, noopenerなど）
7. コード品質（非推奨タグ、インラインスタイルなど）

**出力形式**:
- Markdown形式のレポート
- JSON形式のデータ

---

#### `test_analyzer.py`
```python
from analyzer import WebQualityAnalyzer

analyzer = WebQualityAnalyzer("https://example.com")
report = analyzer.analyze()

print(f"総合スコア: {report.total_score}/100")
print(f"グレード: {report.grade}")
print(f"問題数: {len(report.issues)}件")
```

**役割**: 動作確認用の簡単なテストスクリプト  
**使用タイミング**: Phase 1のセットアップ完了確認

---

### Webアプリ化（Phase 2）

#### `requirements.txt`（Phase 2版）
```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
Pillow>=10.0.0
flask>=3.0.0
flask-cors>=4.0.0
```

**追加パッケージ**:
- `flask`: Webフレームワーク
- `flask-cors`: クロスオリジンリクエスト対応

---

#### `app.py`
**役割**: Flask Webサーバー  
**提供API**:

1. `GET /` - Webインターフェース表示
2. `POST /api/analyze` - URL分析API
3. `POST /api/analyze-file` - ファイルアップロード分析API
4. `GET /api/download/<report_id>/<format>` - レポートダウンロード
5. `GET /api/health` - ヘルスチェック

**リクエスト例**:
```bash
# URL分析
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# ファイルアップロード
curl -X POST http://localhost:5000/api/analyze-file \
  -F "file=@index.html"
```

---

#### `templates/index.html`
**役割**: モバイルフレンドリーなWebインターフェース

**主要機能**:
- タブ切り替え（URL分析 / ファイル分析）
- リアルタイム分析進捗表示
- スコア円グラフ表示
- カテゴリ別スコア一覧
- 問題一覧（重要度別）
- レポートダウンロード（Markdown/JSON）

**レスポンシブデザイン**:
- スマートフォン最適化
- タブレット対応
- デスクトップ対応

---

### CLI & デプロイ（Phase 3）

#### `cli.py`
**役割**: コマンドラインインターフェース

**使用例**:
```bash
# URL分析
python cli.py --url https://example.com

# ファイル分析
python cli.py --file index.html

# JSON出力も含める
python cli.py --url https://example.com --json

# 出力先指定
python cli.py --url https://example.com --output ./my-reports

# 静かモード（標準出力を抑制）
python cli.py --url https://example.com --quiet
```

**オプション一覧**:
- `--url <URL>`: 分析するURL
- `--file <PATH>`: 分析するHTMLファイル
- `--output <DIR>`: 出力ディレクトリ（デフォルト: ./reports）
- `--json`: JSON形式でも出力
- `--no-markdown`: Markdownレポートを出力しない
- `--quiet`: 標準出力を抑制

---

#### `batch_analyze.py`
**役割**: 複数サイトの一括分析

**使用例**:
```bash
# URLリストを作成
echo "https://example.com" > urls.txt
echo "https://google.com" >> urls.txt

# 一括分析実行
python batch_analyze.py urls.txt results.csv
```

**出力形式**: CSV
- URL
- スコア
- グレード
- 問題数
- 各カテゴリスコア
- 分析日時

**活用シーン**:
- 競合サイト分析
- ポートフォリオサイトの定期チェック
- クライアントサイトの品質レポート

---

#### `Procfile`（Heroku用）
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

**役割**: Herokuでの起動コマンド指定  
**必要パッケージ**: `gunicorn`

---

#### `runtime.txt`（Heroku用）
```
python-3.11.6
```

**役割**: 使用するPythonバージョン指定

---

#### `render.yaml`（Render用）
```yaml
services:
  - type: web
    name: web-quality-analyzer-pro
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.6
```

**役割**: Renderでの自動デプロイ設定

---

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# 一時ファイル
uploads/
reports/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

**役割**: Git管理から除外するファイル指定

---

### PWA化（Phase 3 - オプション）

#### `static/manifest.json`
```json
{
  "name": "Web Quality Analyzer Pro",
  "short_name": "WQA Pro",
  "description": "世界最高水準のWebサイト品質分析ツール",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "orientation": "portrait",
  "icons": [...]
}
```

**役割**: PWA（Progressive Web App）設定  
**効果**: スマホのホーム画面に追加可能

---

#### `static/sw.js`
```javascript
const CACHE_NAME = 'wqa-pro-v1';
const urlsToCache = ['/'];

self.addEventListener('install', event => {
  // キャッシュ処理
});

self.addEventListener('fetch', event => {
  // オフライン対応
});
```

**役割**: Service Worker（オフライン対応）

---

## 🎯 段階的なセットアップ手順

### Phase 1: ローカル実行（5分）

```bash
# 1. ディレクトリ作成
mkdir web-quality-analyzer
cd web-quality-analyzer

# 2. ファイル作成
# - requirements.txt
# - analyzer.py
# - test_analyzer.py

# 3. パッケージインストール
pip install -r requirements.txt

# 4. テスト実行
python test_analyzer.py
```

**確認項目**:
- ✅ パッケージがインストールされた
- ✅ テストが成功した
- ✅ スコアが表示された

---

### Phase 2: Webアプリ化（+5分）

```bash
# 1. ディレクトリ作成
mkdir templates

# 2. ファイル作成
# - app.py
# - templates/index.html

# 3. 追加パッケージインストール
pip install flask flask-cors

# 4. サーバー起動
python app.py

# 5. ブラウザで確認
# http://localhost:5000
```

**確認項目**:
- ✅ サーバーが起動した
- ✅ UIが表示された
- ✅ URL分析が動作した
- ✅ ファイル分析が動作した

---

### Phase 3: CLI & デプロイ（+10分）

```bash
# 1. ファイル作成
# - cli.py
# - batch_analyze.py
# - Procfile
# - runtime.txt
# - .gitignore

# 2. CLIテスト
python cli.py --url https://example.com

# 3. Git初期化
git init
git add .
git commit -m "Initial commit"

# 4. デプロイ（好みのプラットフォーム）
# Heroku: heroku create && git push heroku main
# Render: GitHubにプッシュ後、Render連携
```

**確認項目**:
- ✅ CLIが動作した
- ✅ レポートが生成された
- ✅ デプロイに成功した
- ✅ 公開URLにアクセスできた

---

## 📊 ファイルサイズの目安

| ファイル | サイズ | 重要度 |
|---------|--------|--------|
| analyzer.py | ~25KB | ★★★★★ |
| app.py | ~12KB | ★★★★☆ |
| cli.py | ~8KB | ★★★☆☆ |
| templates/index.html | ~18KB | ★★★★☆ |
| batch_analyze.py | ~4KB | ★★★☆☆ |
| requirements.txt | ~200B | ★★★★★ |

---

## 🔄 アップデート手順

### 新機能追加時

```bash
# 1. 変更を加える
# analyzer.pyやapp.pyを編集

# 2. ローカルでテスト
python test_analyzer.py

# 3. Git commit
git add .
git commit -m "Add new feature: XXX"

# 4. デプロイ
git push heroku main
# または
git push origin main  # Renderの場合は自動デプロイ
```

---

## 🆘 トラブルシューティング

### ファイルが見つからないエラー

```
FileNotFoundError: [Errno 2] No such file or directory: 'templates/index.html'
```

**解決方法**:
1. ディレクトリ構造を確認
2. templatesフォルダが存在するか確認
3. index.htmlが正しく配置されているか確認

---

### パッケージインポートエラー

```
ModuleNotFoundError: No module named 'flask'
```

**解決方法**:
```bash
pip install -r requirements.txt
```

---

### ポート使用中エラー

```
OSError: [Errno 48] Address already in use
```

**解決方法**:
```bash
# 使用中のプロセスを特定
lsof -i :5000

# プロセスを終了
kill -9 <PID>

# または、別のポートを使用
# app.py内: app.run(port=5001)
```

---

## ✅ 最終チェックリスト

プロジェクト完成時に確認してください：

### ファイル存在確認
- [ ] requirements.txt
- [ ] analyzer.py
- [ ] app.py
- [ ] templates/index.html
- [ ] cli.py
- [ ] .gitignore

### 動作確認
- [ ] ローカルで分析が動作する
- [ ] Webサーバーが起動する
- [ ] ブラウザでUIが表示される
- [ ] CLIから実行できる
- [ ] レポートが生成される

### デプロイ確認（オプション）
- [ ] Gitリポジトリが作成されている
- [ ] デプロイに成功した
- [ ] 公開URLで動作する
- [ ] スマホからアクセスできる

---

## 🎓 次のステップ

1. **Phase 1完了後**: test_analyzer.pyで動作確認
2. **Phase 2完了後**: スマホから実際に使ってみる
3. **Phase 3完了後**: 実案件で活用開始

すべてのPhaseが完了したら、池高さんのビジネスに完全統合できる状態です！
