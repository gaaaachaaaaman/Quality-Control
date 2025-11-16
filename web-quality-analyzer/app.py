#!/usr/bin/env python3
"""
Web Quality Analyzer Pro - Flask API Server
モバイル対応のWeb API
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from analyzer import WebQualityAnalyzer
from design_comparator import DesignComparator
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


@app.route('/api/compare-design', methods=['POST'])
def compare_design():
    """
    デザインカンプ(PDF)とHTML実装を比較するエンドポイント

    フォームデータ:
    - pdf_file: PDFファイル（デザインカンプ）
    - html_file: HTMLファイル（実装）

    レスポンス:
    {
        "success": true,
        "result": {
            "similarity_score": 95.5,
            "grade": "S",
            "diff_percentage": 4.5,
            "pixel_difference": 12345,
            "total_pixels": 2073600,
            "issues": [...],
            "diff_image": "base64...",
            "overlay_image": "base64...",
            "design_image": "base64...",
            "browser_image": "base64..."
        }
    }
    """
    try:
        # ファイルの確認
        if 'pdf_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'PDFファイルが指定されていません'
            }), 400

        if 'html_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'HTMLファイルが指定されていません'
            }), 400

        pdf_file = request.files['pdf_file']
        html_file = request.files['html_file']

        if pdf_file.filename == '' or html_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'ファイルが選択されていません'
            }), 400

        # PDFファイルのチェック
        if not pdf_file.filename.endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'PDFファイル(.pdf)を指定してください'
            }), 400

        # HTMLファイルのチェック
        if not html_file.filename.endswith(('.html', '.htm')):
            return jsonify({
                'success': False,
                'error': 'HTMLファイル(.html, .htm)を指定してください'
            }), 400

        # PDFをバイトデータで読み込み
        pdf_bytes = pdf_file.read()

        # HTMLを文字列で読み込み
        html_content = html_file.read().decode('utf-8')

        # デザイン比較実行
        comparator = DesignComparator()
        result = comparator.compare_pdf_bytes_with_html(pdf_bytes, html_content)

        # 結果をJSON形式で返す
        response_data = {
            'success': True,
            'result': {
                'similarity_score': result.similarity_score,
                'grade': result.grade,
                'diff_percentage': result.diff_percentage,
                'pixel_difference': result.pixel_difference,
                'total_pixels': result.total_pixels,
                'issues': result.issues,
                'diff_image': result.diff_image_base64,
                'overlay_image': result.overlay_image_base64,
                'design_image': result.design_image_base64,
                'browser_image': result.browser_image_base64,
                # 高度な分析結果を追加
                'section_analyses': result.section_analyses,
                'color_palette_score': result.color_palette_score,
                'layout_accuracy': result.layout_accuracy,
                'css_recommendations': result.css_recommendations,
                'heatmap': result.heatmap_base64
            }
        }

        return jsonify(response_data)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 本番環境では適切なWSGIサーバー（gunicorn等）を使用してください
    app.run(host='0.0.0.0', port=5000, debug=False)
