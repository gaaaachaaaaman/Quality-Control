# Web Quality Analyzer Pro - Phase 2: Web APIとモバイルインターフェース

## 概要
このフェーズでは、スマートフォンからアクセスできるWeb APIとモバイルフレンドリーなUIを構築します。

## 前提条件
- Phase 1が完了していること
- Flask、Flask-CORSがインストール済みであること

## ステップ1: Flask APIサーバーの実装

`app.py`という名前で以下のファイルを作成してください：

```python
#!/usr/bin/env python3
"""
Web Quality Analyzer Pro - Flask API Server
モバイル対応のWeb API
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from analyzer import WebQualityAnalyzer
import os
from datetime import datetime
import tempfile
import traceback

app = Flask(__name__)
CORS(app)  # クロスオリジンリクエストを許可

# 一時ファイル保存用ディレクトリ
UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """トップページ（モバイルフレンドリーなUI）"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    URL分析エンドポイント
    
    リクエストボディ:
    {
        "url": "https://example.com"
    }
    
    レスポンス:
    {
        "success": true,
        "report": {...},
        "report_id": "20241116_123456"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URLが指定されていません'
            }), 400
        
        url = data['url']
        
        # URL形式の簡易バリデーション
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'URLは http:// または https:// で始まる必要があります'
            }), 400
        
        # 分析実行
        analyzer = WebQualityAnalyzer(url, is_file=False)
        report = analyzer.analyze()
        
        # レポートIDの生成
        report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Markdownレポートの保存
        md_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report.to_markdown())
        
        # JSONレポートの保存
        json_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.json')
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'report': report.to_dict(),
            'report_id': report_id,
            'download_links': {
                'markdown': f'/api/download/{report_id}/markdown',
                'json': f'/api/download/{report_id}/json'
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """
    HTMLファイルアップロード分析エンドポイント
    
    フォームデータ:
    - file: HTMLファイル
    
    レスポンス:
    {
        "success": true,
        "report": {...},
        "report_id": "20241116_123456"
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'ファイルが指定されていません'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'ファイルが選択されていません'
            }), 400
        
        # HTMLファイルかチェック
        if not file.filename.endswith(('.html', '.htm')):
            return jsonify({
                'success': False,
                'error': 'HTMLファイル(.html, .htm)のみ対応しています'
            }), 400
        
        # 一時ファイルとして保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f'upload_{timestamp}_{file.filename}'
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        
        # 分析実行
        analyzer = WebQualityAnalyzer(temp_path, is_file=True)
        report = analyzer.analyze()
        
        # 一時ファイルの削除
        os.remove(temp_path)
        
        # レポートIDの生成
        report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Markdownレポートの保存
        md_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report.to_markdown())
        
        # JSONレポートの保存
        json_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.json')
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'report': report.to_dict(),
            'report_id': report_id,
            'download_links': {
                'markdown': f'/api/download/{report_id}/markdown',
                'json': f'/api/download/{report_id}/json'
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<report_id>/<format>')
def download_report(report_id, format):
    """
    レポートダウンロードエンドポイント
    
    パラメータ:
    - report_id: レポートID
    - format: 'markdown' または 'json'
    """
    try:
        if format == 'markdown':
            file_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.md')
            mimetype = 'text/markdown'
            download_name = f'quality_report_{report_id}.md'
        elif format == 'json':
            file_path = os.path.join(REPORT_FOLDER, f'report_{report_id}.json')
            mimetype = 'application/json'
            download_name = f'quality_report_{report_id}.json'
        else:
            return jsonify({
                'success': False,
                'error': '無効な形式です。markdown または json を指定してください'
            }), 400
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'レポートが見つかりません'
            }), 404
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    # 本番環境では適切なWSGIサーバー（gunicorn等）を使用してください
    app.run(host='0.0.0.0', port=5000, debug=False)
```

## ステップ2: モバイルフレンドリーなHTMLテンプレートの作成

`templates`ディレクトリを作成し、その中に`index.html`を作成してください：

```bash
mkdir templates
```

`templates/index.html`:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Quality Analyzer Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab-button {
            flex: 1;
            padding: 12px;
            border: none;
            background: #f0f0f0;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab-button.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .input-group input[type="text"],
        .input-group input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .input-group input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analyze-button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .analyze-button:active {
            transform: scale(0.98);
        }
        
        .analyze-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
        }
        
        .result.active {
            display: block;
        }
        
        .score-display {
            text-align: center;
            padding: 30px;
            margin-bottom: 20px;
        }
        
        .score-circle {
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: bold;
            color: white;
        }
        
        .score-S { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .score-A { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .score-B { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .score-C { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .score-D { background: linear-gradient(135deg, #e52d27 0%, #b31217 100%); }
        
        .grade-label {
            font-size: 18px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .score-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        
        .category-scores {
            margin-bottom: 20px;
        }
        
        .category-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .category-item:last-child {
            border-bottom: none;
        }
        
        .category-name {
            font-weight: 600;
            color: #333;
        }
        
        .category-score {
            font-weight: bold;
            color: #667eea;
        }
        
        .issue-list {
            margin-top: 20px;
        }
        
        .issue-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .issue-critical {
            background: #fee;
            border-color: #e53e3e;
        }
        
        .issue-high {
            background: #fff5e6;
            border-color: #ff9800;
        }
        
        .issue-medium {
            background: #fff9e6;
            border-color: #ffd700;
        }
        
        .issue-low {
            background: #e6f7ff;
            border-color: #2196f3;
        }
        
        .issue-title {
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }
        
        .issue-description {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .issue-fix {
            font-size: 13px;
            color: #444;
            background: white;
            padding: 8px;
            border-radius: 4px;
            margin-top: 8px;
        }
        
        .download-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .download-button {
            flex: 1;
            padding: 12px;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            text-align: center;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .download-button:hover {
            background: #e0e0e0;
        }
        
        .error {
            background: #fee;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
        }
        
        .error.active {
            display: block;
        }
        
        @media (max-width: 480px) {
            .header h1 {
                font-size: 24px;
            }
            
            .card {
                padding: 16px;
            }
            
            .score-circle {
                width: 120px;
                height: 120px;
                font-size: 36px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Web Quality Analyzer Pro</h1>
            <p>世界最高水準のWebサイト品質分析ツール</p>
        </div>
        
        <div class="card">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="switchTab('url')">URL分析</button>
                <button class="tab-button" onclick="switchTab('file')">ファイル分析</button>
            </div>
            
            <!-- URL分析タブ -->
            <div id="url-tab" class="tab-content active">
                <div class="input-group">
                    <label for="url-input">分析するURL</label>
                    <input type="text" id="url-input" placeholder="https://example.com">
                </div>
                <button class="analyze-button" onclick="analyzeUrl()">分析開始</button>
            </div>
            
            <!-- ファイル分析タブ -->
            <div id="file-tab" class="tab-content">
                <div class="input-group">
                    <label for="file-input">HTMLファイルを選択</label>
                    <input type="file" id="file-input" accept=".html,.htm">
                </div>
                <button class="analyze-button" onclick="analyzeFile()">分析開始</button>
            </div>
            
            <!-- ローディング表示 -->
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>分析中...</p>
            </div>
            
            <!-- エラー表示 -->
            <div id="error" class="error"></div>
        </div>
        
        <!-- 分析結果 -->
        <div id="result" class="result">
            <div class="card">
                <div class="score-display">
                    <div id="score-circle" class="score-circle">
                        <span id="score-text">--</span>
                    </div>
                    <div class="grade-label">総合グレード: <span id="grade">-</span></div>
                    <div class="score-value"><span id="total-score">--</span> / 100</div>
                </div>
                
                <div class="category-scores" id="category-scores">
                    <!-- カテゴリ別スコアが動的に追加されます -->
                </div>
                
                <div class="download-buttons">
                    <a id="download-md" href="#" class="download-button">📄 Markdown</a>
                    <a id="download-json" href="#" class="download-button">📊 JSON</a>
                </div>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: 15px;">検出された問題</h3>
                <div id="issue-list" class="issue-list">
                    <!-- 問題一覧が動的に追加されます -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {
            // タブボタンの切り替え
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // タブコンテンツの切り替え
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tab + '-tab').classList.add('active');
            
            // エラーと結果をクリア
            hideError();
            hideResult();
        }
        
        function showLoading() {
            document.getElementById('loading').classList.add('active');
            document.querySelectorAll('.analyze-button').forEach(btn => {
                btn.disabled = true;
            });
        }
        
        function hideLoading() {
            document.getElementById('loading').classList.remove('active');
            document.querySelectorAll('.analyze-button').forEach(btn => {
                btn.disabled = false;
            });
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.classList.add('active');
        }
        
        function hideError() {
            document.getElementById('error').classList.remove('active');
        }
        
        function showResult() {
            document.getElementById('result').classList.add('active');
        }
        
        function hideResult() {
            document.getElementById('result').classList.remove('active');
        }
        
        async function analyzeUrl() {
            const url = document.getElementById('url-input').value.trim();
            
            if (!url) {
                showError('URLを入力してください');
                return;
            }
            
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showError('URLは http:// または https:// で始まる必要があります');
                return;
            }
            
            hideError();
            hideResult();
            showLoading();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResult(data.report, data.download_links);
                } else {
                    showError(data.error || '分析に失敗しました');
                }
            } catch (error) {
                showError('サーバーとの通信に失敗しました: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function analyzeFile() {
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            
            if (!file) {
                showError('ファイルを選択してください');
                return;
            }
            
            hideError();
            hideResult();
            showLoading();
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/analyze-file', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResult(data.report, data.download_links);
                } else {
                    showError(data.error || '分析に失敗しました');
                }
            } catch (error) {
                showError('サーバーとの通信に失敗しました: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        function displayResult(report, downloadLinks) {
            // スコア表示
            const scoreCircle = document.getElementById('score-circle');
            const scoreText = document.getElementById('score-text');
            const gradeText = document.getElementById('grade');
            const totalScoreText = document.getElementById('total-score');
            
            scoreText.textContent = report.total_score;
            gradeText.textContent = report.grade;
            totalScoreText.textContent = report.total_score;
            
            // グレードに応じた色設定
            scoreCircle.className = 'score-circle score-' + report.grade;
            
            // カテゴリ別スコア表示
            const categoryScoresDiv = document.getElementById('category-scores');
            categoryScoresDiv.innerHTML = '';
            
            const categoryEmojis = {
                'SEO': '🔍',
                'アクセシビリティ': '♿',
                'パフォーマンス': '⚡',
                'デザイン': '🎨',
                'セキュリティ': '🔒',
                'コード品質': '💻'
            };
            
            for (const [category, score] of Object.entries(report.category_scores)) {
                const item = document.createElement('div');
                item.className = 'category-item';
                item.innerHTML = `
                    <span class="category-name">${categoryEmojis[category] || ''} ${category}</span>
                    <span class="category-score">${score}/100</span>
                `;
                categoryScoresDiv.appendChild(item);
            }
            
            // 問題一覧表示
            const issueListDiv = document.getElementById('issue-list');
            issueListDiv.innerHTML = '';
            
            if (report.issues.length === 0) {
                issueListDiv.innerHTML = '<p style="text-align: center; color: #666;">問題は検出されませんでした！</p>';
            } else {
                // 重要度順にソート
                const severityOrder = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3 };
                const sortedIssues = report.issues.sort((a, b) => 
                    severityOrder[a.severity] - severityOrder[b.severity]
                );
                
                sortedIssues.forEach(issue => {
                    const item = document.createElement('div');
                    item.className = `issue-item issue-${issue.severity}`;
                    
                    const severityLabels = {
                        'critical': '🔴 致命的',
                        'high': '🟠 重要',
                        'medium': '🟡 中程度',
                        'low': '🟢 軽微'
                    };
                    
                    item.innerHTML = `
                        <div style="font-size: 12px; color: #888; margin-bottom: 5px;">
                            ${severityLabels[issue.severity]} | ${issue.category}
                        </div>
                        <div class="issue-title">${issue.title}</div>
                        <div class="issue-description">${issue.description}</div>
                        <div class="issue-fix"><strong>修正方法:</strong> ${issue.fix}</div>
                    `;
                    issueListDiv.appendChild(item);
                });
            }
            
            // ダウンロードリンク設定
            document.getElementById('download-md').href = downloadLinks.markdown;
            document.getElementById('download-json').href = downloadLinks.json;
            
            showResult();
        }
    </script>
</body>
</html>
```

## ステップ3: サーバーの起動

```bash
python app.py
```

サーバーが起動したら、以下のURLにアクセスできます：

- ローカル: `http://localhost:5000`
- 同一ネットワーク内の他のデバイス: `http://[サーバーのIPアドレス]:5000`

## ステップ4: スマートフォンからのアクセス

### 方法1: ローカルネットワーク経由（同じWi-Fi内）

1. サーバーのIPアドレスを確認：
   ```bash
   # macOS/Linux
   ifconfig | grep inet
   
   # Windows
   ipconfig
   ```

2. スマートフォンのブラウザで以下にアクセス：
   ```
   http://[サーバーのIPアドレス]:5000
   ```

### 方法2: ngrokを使った外部公開（インターネット経由）

```bash
# ngrokのインストール（初回のみ）
# https://ngrok.com/ からダウンロード

# サーバーを公開
ngrok http 5000
```

ngrokが表示するURLにスマートフォンからアクセスできます。

## Phase 2の完了確認

以下が正常に動作すれば、Phase 2は完了です：

- [ ] Flask APIサーバーが起動する
- [ ] ブラウザで http://localhost:5000 にアクセスできる
- [ ] URL分析が動作する
- [ ] ファイルアップロード分析が動作する
- [ ] レポートのダウンロードができる
- [ ] スマートフォンからアクセスできる

## 次のステップ

Phase 2が完了したら、Phase 3（Claude Code統合とデプロイ）に進みます。
