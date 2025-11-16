# Web Quality Analyzer Pro - Phase 3: Claude Code統合とデプロイ

## 概要
このフェーズでは、Claude Codeからの実行とクラウドへのデプロイを実現します。

## 前提条件
- Phase 1とPhase 2が完了していること
- Claude Code（CLI）がインストールされていること

---

## パート1: Claude Code統合

### ステップ1: Claude Code用のコマンドラインインターフェース作成

`cli.py`を作成してください：

```python
#!/usr/bin/env python3
"""
Web Quality Analyzer Pro - CLI
Claude Codeから実行可能なコマンドラインツール
"""

import argparse
import sys
import os
from analyzer import WebQualityAnalyzer
from datetime import datetime
import json


def main():
    parser = argparse.ArgumentParser(
        description='Web Quality Analyzer Pro - 世界最高水準のWebサイト品質分析ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # URLを分析
  python cli.py --url https://example.com
  
  # HTMLファイルを分析
  python cli.py --file index.html
  
  # JSONレポートも出力
  python cli.py --url https://example.com --json
  
  # 出力先ディレクトリを指定
  python cli.py --url https://example.com --output ./reports
        '''
    )
    
    # 入力オプション
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', type=str, help='分析するURL')
    input_group.add_argument('--file', type=str, help='分析するHTMLファイルのパス')
    
    # 出力オプション
    parser.add_argument('--output', type=str, default='./reports',
                       help='レポート出力先ディレクトリ（デフォルト: ./reports）')
    parser.add_argument('--json', action='store_true',
                       help='JSON形式のレポートも出力')
    parser.add_argument('--no-markdown', action='store_true',
                       help='Markdownレポートを出力しない')
    parser.add_argument('--quiet', action='store_true',
                       help='標準出力を抑制')
    
    args = parser.parse_args()
    
    try:
        # 出力ディレクトリの作成
        os.makedirs(args.output, exist_ok=True)
        
        if not args.quiet:
            print("="*60)
            print("Web Quality Analyzer Pro")
            print("="*60)
            print()
        
        # 分析実行
        if args.url:
            if not args.quiet:
                print(f"📡 URL分析: {args.url}")
            analyzer = WebQualityAnalyzer(args.url, is_file=False)
        else:
            if not os.path.exists(args.file):
                print(f"❌ エラー: ファイルが見つかりません: {args.file}", file=sys.stderr)
                return 1
            if not args.quiet:
                print(f"📄 ファイル分析: {args.file}")
            analyzer = WebQualityAnalyzer(args.file, is_file=True)
        
        if not args.quiet:
            print("🔍 分析中...")
            print()
        
        report = analyzer.analyze()
        
        # レポートID生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Markdownレポート出力
        if not args.no_markdown:
            md_filename = f'quality_report_{timestamp}.md'
            md_path = os.path.join(args.output, md_filename)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(report.to_markdown())
            
            if not args.quiet:
                print(f"✅ Markdownレポート: {md_path}")
        
        # JSONレポート出力
        if args.json:
            json_filename = f'quality_report_{timestamp}.json'
            json_path = os.path.join(args.output, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            
            if not args.quiet:
                print(f"✅ JSONレポート: {json_path}")
        
        # サマリー表示
        if not args.quiet:
            print()
            print("="*60)
            print("📊 分析結果サマリー")
            print("="*60)
            print(f"総合スコア: {report.total_score}/100 (グレード: {report.grade})")
            print(f"検出された問題: {len(report.issues)}件")
            
            critical_count = len([i for i in report.issues if i.severity == 'critical'])
            high_count = len([i for i in report.issues if i.severity == 'high'])
            
            if critical_count > 0:
                print(f"  🔴 致命的: {critical_count}件")
            if high_count > 0:
                print(f"  🟠 重要: {high_count}件")
            
            print()
            print("カテゴリ別スコア:")
            for category, score in report.category_scores.items():
                emoji = {
                    'SEO': '🔍',
                    'アクセシビリティ': '♿',
                    'パフォーマンス': '⚡',
                    'デザイン': '🎨',
                    'セキュリティ': '🔒',
                    'コード品質': '💻'
                }.get(category, '📋')
                print(f"  {emoji} {category}: {score}/100")
            
            if report.recommendations:
                print()
                print("優先対応事項:")
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"  {i}. {rec}")
        
        return 0
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}", file=sys.stderr)
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

実行権限を付与：

```bash
chmod +x cli.py
```

### ステップ2: Claude Codeからの実行テスト

Claude Codeのターミナルから以下を実行：

```bash
# URL分析
python cli.py --url https://example.com --json

# ローカルファイル分析
python cli.py --file test.html --output ./my-reports
```

---

## パート2: Herokuへのデプロイ（無料プラン）

### ステップ1: 必要なファイルの準備

#### `Procfile`の作成（Heroku用）

```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

#### `runtime.txt`の作成

```
python-3.11.6
```

#### `requirements.txt`の更新

既存のrequirements.txtに以下を追加：

```
gunicorn>=21.2.0
```

### ステップ2: Herokuアカウントとセットアップ

1. Herokuアカウント作成（無料）: https://signup.heroku.com/

2. Heroku CLIのインストール:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # https://devcenter.heroku.com/articles/heroku-cli からインストーラーをダウンロード
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

3. Herokuにログイン:
   ```bash
   heroku login
   ```

### ステップ3: Gitリポジトリの初期化

```bash
# プロジェクトディレクトリで実行
git init
git add .
git commit -m "Initial commit"
```

### ステップ4: Herokuアプリの作成とデプロイ

```bash
# アプリを作成（名前は自動生成）
heroku create

# または、アプリ名を指定
heroku create web-quality-analyzer-pro

# デプロイ
git push heroku main

# アプリを開く
heroku open
```

### ステップ5: 環境変数の設定（必要に応じて）

```bash
heroku config:set FLASK_ENV=production
```

---

## パート3: Renderへのデプロイ（推奨・より安定）

Renderは無料プランでもより安定しており、自動的にHTTPSが有効になります。

### ステップ1: render.yamlの作成

プロジェクトルートに`render.yaml`を作成：

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

### ステップ2: GitHubリポジトリにプッシュ

```bash
# GitHubで新しいリポジトリを作成後
git remote add origin https://github.com/yourusername/web-quality-analyzer.git
git branch -M main
git push -u origin main
```

### ステップ3: Renderでデプロイ

1. https://render.com でアカウント作成（GitHubアカウントで連携可能）
2. "New +" → "Web Service"を選択
3. GitHubリポジトリを接続
4. 設定を確認してデプロイ

数分でデプロイが完了し、URLが発行されます。

---

## パート4: Railway.appへのデプロイ（最も簡単）

### ステップ1: Railwayアカウント作成

https://railway.app でGitHubアカウントで登録

### ステップ2: デプロイ

1. ダッシュボードから"New Project"
2. "Deploy from GitHub repo"を選択
3. リポジトリを選択
4. 自動的に検出され、デプロイ開始
5. "Settings"からポート設定を確認（5000）

---

## パート5: 独自ドメインの設定（オプション）

### Renderの場合

1. Renderダッシュボード → "Settings" → "Custom Domain"
2. ドメインを入力（例: analyzer.yourdomain.com）
3. DNSレコードを設定:
   ```
   CNAME analyzer yourdomain.onrender.com
   ```

### Herokuの場合

```bash
heroku domains:add analyzer.yourdomain.com
```

その後、DNSで以下を設定:
```
CNAME analyzer yourapp.herokuapp.com
```

---

## パート6: モバイルアプリ化（PWA）

### ステップ1: manifest.jsonの作成

`static`ディレクトリを作成し、`manifest.json`を配置：

```bash
mkdir static
```

`static/manifest.json`:

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
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### ステップ2: Service Workerの作成

`static/sw.js`:

```javascript
const CACHE_NAME = 'wqa-pro-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

### ステップ3: HTMLテンプレートの更新

`templates/index.html`の`<head>`内に追加：

```html
<!-- PWA対応 -->
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#667eea">
<link rel="apple-touch-icon" href="/static/icon-192.png">

<!-- Service Worker登録 -->
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js')
    .then(reg => console.log('Service Worker registered'))
    .catch(err => console.log('Service Worker registration failed'));
}
</script>
```

### ステップ4: アイコン画像の準備

192x192pxと512x512pxのPNG画像を`static/`に配置してください。

これで、スマートフォンのブラウザから「ホーム画面に追加」でアプリとして使用できます。

---

## パート7: Claude Code統合の高度な使用例

### 一括分析スクリプト

`batch_analyze.py`:

```python
#!/usr/bin/env python3
"""
複数サイトの一括分析スクリプト
"""

import sys
from analyzer import WebQualityAnalyzer
import csv
from datetime import datetime

def batch_analyze(urls_file, output_csv):
    """URLリストファイルから一括分析"""
    
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    results = []
    
    print(f"📊 {len(urls)}件のサイトを分析します...")
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        try:
            analyzer = WebQualityAnalyzer(url, is_file=False)
            report = analyzer.analyze()
            
            results.append({
                'URL': url,
                'スコア': report.total_score,
                'グレード': report.grade,
                '問題数': len(report.issues),
                'SEO': report.category_scores['SEO'],
                'アクセシビリティ': report.category_scores['アクセシビリティ'],
                'パフォーマンス': report.category_scores['パフォーマンス'],
                '分析日時': report.analyzed_at
            })
            
            print(f"  ✅ スコア: {report.total_score}/100 (グレード: {report.grade})")
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")
            results.append({
                'URL': url,
                'スコア': 'エラー',
                'グレード': '-',
                '問題数': '-',
                'SEO': '-',
                'アクセシビリティ': '-',
                'パフォーマンス': '-',
                '分析日時': datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            })
    
    # CSV出力
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ 結果を保存しました: {output_csv}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("使用法: python batch_analyze.py urls.txt output.csv")
        sys.exit(1)
    
    batch_analyze(sys.argv[1], sys.argv[2])
```

使用方法:

```bash
# urls.txtに分析したいURLを1行ずつ記載
echo "https://example.com" > urls.txt
echo "https://google.com" >> urls.txt

# 一括分析実行
python batch_analyze.py urls.txt results.csv
```

---

## Phase 3の完了確認

以下がすべて完了していれば、システムは本番運用可能です：

- [ ] Claude CodeのCLIから実行できる
- [ ] クラウドにデプロイされている
- [ ] スマートフォンからアクセスできる
- [ ] PWAとしてインストール可能
- [ ] 一括分析が実行できる

## トラブルシューティング

### Herokuでメモリエラーが出る場合

```bash
# より軽量なWebサーバーに変更
pip install waitress
```

`Procfile`を以下に変更：
```
web: waitress-serve --port=$PORT app:app
```

### RenderでビルドがタイムアウトNする場合

`render.yaml`のbuildCommandに制限時間を追加：

```yaml
buildCommand: pip install --no-cache-dir -r requirements.txt
```

---

## 次のステップ（オプション）

1. **Slack/Discord通知機能**: 分析結果を自動通知
2. **定期実行機能**: cron jobで定期的に品質チェック
3. **ダッシュボード機能**: 過去の分析履歴を可視化
4. **API認証**: APIキーによるアクセス制御
5. **マルチユーザー対応**: ユーザーアカウント機能

これらの拡張機能の実装ガイドが必要な場合は、Phase 4として提供可能です。
