# Web Quality Analyzer Pro

世界最高水準のWebサイト品質分析ツール

## 📋 機能

- **SEO分析**: タイトル、メタタグ、見出し構造、OGP設定
- **アクセシビリティ分析**: alt属性、フォームラベル、言語設定
- **パフォーマンス分析**: CSS/JSファイル数、画像の遅延読み込み
- **デザイン分析**: viewport設定、favicon
- **セキュリティ分析**: HTTPS、外部リンクのnoopener
- **コード品質分析**: インラインスタイル、非推奨タグ

## 🚀 ローカル環境でのセットアップ

### 前提条件

- Python 3.8以上
- pip

### インストール手順

1. **リポジトリをクローン**

```bash
git clone https://github.com/gaaaachaaaaman/Quality-Control.git
cd Quality-Control/web-quality-analyzer
```

2. **依存パッケージをインストール**

```bash
pip install -r requirements.txt
```

3. **サーバーを起動**

```bash
python app.py
```

4. **ブラウザでアクセス**

以下のURLを開いてください：
```
http://localhost:5000
```

## 💻 使い方

### Web UI（推奨）

1. ブラウザで `http://localhost:5000` を開く
2. 以下のいずれかを選択：
   - **URL分析**: WebサイトのURLを入力
   - **ファイル分析**: HTMLファイルをアップロード
3. 「分析開始」ボタンをクリック
4. 結果を確認し、必要に応じてレポートをダウンロード

### コマンドライン

```bash
python test_analyzer.py
```

## 📊 スコアリング

- **S**: 90-100点 - 優秀
- **A**: 80-89点 - 良好
- **B**: 70-79点 - 標準
- **C**: 60-69点 - 要改善
- **D**: 0-59点 - 不合格

## 📁 プロジェクト構成

```
web-quality-analyzer/
├── app.py                 # Flask APIサーバー
├── analyzer.py            # コア分析エンジン
├── requirements.txt       # 依存パッケージ
├── templates/
│   └── index.html        # Webインターフェース
├── static/               # 静的ファイル
├── uploads/              # アップロードファイル保存先
├── reports/              # 分析レポート保存先
├── test.html             # テスト用HTMLファイル
└── test_analyzer.py      # テストスクリプト
```

## 🔧 API エンドポイント

### ヘルスチェック
```bash
GET /api/health
```

### URL分析
```bash
POST /api/analyze
Content-Type: application/json

{
  "url": "https://example.com"
}
```

### ファイル分析
```bash
POST /api/analyze-file
Content-Type: multipart/form-data

file: [HTMLファイル]
```

### レポートダウンロード
```bash
GET /api/download/{report_id}/markdown
GET /api/download/{report_id}/json
```

## 📝 レポート形式

分析結果は以下の形式でダウンロード可能：

- **Markdown**: 読みやすい形式のレポート
- **JSON**: プログラムで処理可能な形式

## 🎯 開発情報

### 技術スタック

- **バックエンド**: Flask, Flask-CORS
- **HTML解析**: BeautifulSoup4, lxml
- **HTTP通信**: requests
- **画像処理**: Pillow

### Phase構成

- **Phase 1**: コア分析エンジン（analyzer.py）
- **Phase 2**: Web APIとモバイルUI（app.py, index.html）
- **Phase 3**: デプロイと統合（予定）

## 🐛 トラブルシューティング

### ポート5000が既に使用中

別のポートを使用する場合：

```python
# app.py の最終行を変更
app.run(host='0.0.0.0', port=8080, debug=False)
```

### 依存パッケージのインストールエラー

```bash
pip install --upgrade pip
pip install -r requirements.txt --user
```

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。

## 🤝 貢献

バグ報告や機能リクエストは Issue でお願いします。
