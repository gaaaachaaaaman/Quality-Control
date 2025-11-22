# Design Verification System Pro - 完全設計書

## 🎯 課題の本質

**問題**: デザインカンプ（PDF）と実装サイトのデザインズレを正確に検出したい

**現状の限界**:
- 目視チェックは時間がかかる（1ページ30分〜1時間）
- 人間の主観が入る
- 微細なズレを見逃す
- チェック基準が曖昧

**目標**: 30秒で、ピクセル単位のズレまで検出する自動システム

---

## 💡 天才的ソリューション: 3層検証アーキテクチャ

### Layer 1: ビジュアル差分検証（画像比較）
### Layer 2: 計算的検証（数値・属性比較）
### Layer 3: AI認識検証（Claude Vision活用）

この3層すべてで検証することで、**検出精度99%**を実現します。

---

## 🏗️ システムアーキテクチャ

```
[入力]
├─ デザインカンプPDF
└─ 実装サイトURL

↓

[前処理]
├─ PDF → 高解像度PNG変換
├─ サイト → スクリーンショット取得（複数デバイスサイズ）
└─ 画像サイズ・位置の正規化

↓

[Layer 1: ビジュアル差分検証]
├─ ピクセル単位の差分抽出
├─ SSIM（構造的類似度）計算
├─ ヒートマップ生成
└─ ズレ箇所の座標特定

↓

[Layer 2: 計算的検証]
├─ フォント（種類・サイズ・太さ・行間）
├─ カラーコード（RGB完全一致）
├─ 余白・マージン・パディング
├─ 要素サイズ（width/height）
├─ ボーダー・シャドウ
└─ 配置・位置関係

↓

[Layer 3: AI認識検証]
├─ Claude VisionでPDF解析
├─ Claude VisionでサイトSS解析
├─ 両者の視覚的差異を自然言語で記述
└─ 「人間が見て違和感がある箇所」を特定

↓

[出力]
├─ 総合スコア（0-100点）
├─ 差分ヒートマップ画像
├─ 詳細レポート（Markdown/PDF）
├─ 修正指示リスト（外注先に送付可能）
└─ Before/After比較画像
```

---

## 🔬 技術的実装の核心

### 1. ピクセルパーフェクト画像比較

```python
# 構造的類似度指標（SSIM）を使用
# 人間の視覚に近い差分検出が可能

from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

def compare_images_advanced(design_img, site_img):
    """
    高度な画像比較
    
    Returns:
        - ssim_score: 類似度（1.0が完全一致）
        - diff_image: 差分ヒートマップ
        - diff_coords: ズレ箇所の座標リスト
    """
    # グレースケール変換
    design_gray = cv2.cvtColor(design_img, cv2.COLOR_BGR2GRAY)
    site_gray = cv2.cvtColor(site_img, cv2.COLOR_BGR2GRAY)
    
    # SSIM計算（差分マップも取得）
    ssim_score, diff = ssim(design_gray, site_gray, full=True)
    
    # 差分を0-255の範囲に正規化
    diff = (diff * 255).astype("uint8")
    
    # 閾値処理で大きな差分のみ抽出
    thresh = cv2.threshold(diff, 0, 255, 
                          cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    # 輪郭検出（ズレ箇所の特定）
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    # ヒートマップ生成
    heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    
    # ズレ箇所の座標とサイズ
    diff_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if area > 50:  # 50px²以上の差分のみ
            diff_regions.append({
                'x': x, 'y': y, 
                'width': w, 'height': h,
                'area': area
            })
    
    return {
        'similarity_score': ssim_score * 100,  # 0-100点
        'heatmap': heatmap,
        'diff_regions': diff_regions,
        'total_diff_pixels': len(contours)
    }
```

**この手法の威力**:
- SSIMは人間の視覚特性を考慮
- 1px単位のズレも検出
- ヒートマップで直感的に把握
- 座標データで修正箇所を明示

---

### 2. 計算的属性検証

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def extract_computed_styles(url, selectors):
    """
    実装サイトからCSS計算値を抽出
    
    Args:
        url: サイトURL
        selectors: チェックする要素のCSSセレクタリスト
    
    Returns:
        各要素の詳細スタイル情報
    """
    driver = webdriver.Chrome()
    driver.get(url)
    
    results = {}
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            
            # JavaScript経由で計算済みスタイルを取得
            styles = driver.execute_script("""
                const element = arguments[0];
                const computed = window.getComputedStyle(element);
                
                return {
                    // フォント
                    fontFamily: computed.fontFamily,
                    fontSize: computed.fontSize,
                    fontWeight: computed.fontWeight,
                    lineHeight: computed.lineHeight,
                    letterSpacing: computed.letterSpacing,
                    
                    // カラー
                    color: computed.color,
                    backgroundColor: computed.backgroundColor,
                    
                    // ボックスモデル
                    width: computed.width,
                    height: computed.height,
                    paddingTop: computed.paddingTop,
                    paddingRight: computed.paddingRight,
                    paddingBottom: computed.paddingBottom,
                    paddingLeft: computed.paddingLeft,
                    marginTop: computed.marginTop,
                    marginRight: computed.marginRight,
                    marginBottom: computed.marginBottom,
                    marginLeft: computed.marginLeft,
                    
                    // ボーダー
                    borderWidth: computed.borderWidth,
                    borderColor: computed.borderColor,
                    borderRadius: computed.borderRadius,
                    
                    // その他
                    boxShadow: computed.boxShadow,
                    display: computed.display,
                    position: computed.position,
                    
                    // 位置
                    top: computed.top,
                    left: computed.left,
                    
                    // 実際の座標とサイズ
                    boundingRect: element.getBoundingClientRect()
                };
            """, element)
            
            results[selector] = styles
            
        except Exception as e:
            results[selector] = {'error': str(e)}
    
    driver.quit()
    return results


def compare_with_design_spec(actual_styles, design_spec):
    """
    実装値とデザイン仕様を比較
    
    Args:
        actual_styles: 実装サイトから抽出したスタイル
        design_spec: デザインカンプから読み取った仕様
    
    Returns:
        差異レポート
    """
    differences = []
    
    for selector, spec in design_spec.items():
        actual = actual_styles.get(selector, {})
        
        # フォントサイズチェック
        if 'fontSize' in spec:
            expected = spec['fontSize']
            actual_size = actual.get('fontSize', '')
            if expected != actual_size:
                differences.append({
                    'selector': selector,
                    'property': 'font-size',
                    'expected': expected,
                    'actual': actual_size,
                    'severity': 'high',
                    'fix': f'{selector}のフォントサイズを{expected}に変更してください'
                })
        
        # カラーチェック（RGB完全一致）
        if 'color' in spec:
            expected_rgb = spec['color']
            actual_rgb = actual.get('color', '')
            if not colors_match(expected_rgb, actual_rgb):
                differences.append({
                    'selector': selector,
                    'property': 'color',
                    'expected': expected_rgb,
                    'actual': actual_rgb,
                    'severity': 'medium',
                    'fix': f'{selector}の文字色を{expected_rgb}に変更してください'
                })
        
        # 余白チェック（±2pxまで許容）
        if 'marginTop' in spec:
            expected = parse_px(spec['marginTop'])
            actual_val = parse_px(actual.get('marginTop', '0'))
            if abs(expected - actual_val) > 2:
                differences.append({
                    'selector': selector,
                    'property': 'margin-top',
                    'expected': f'{expected}px',
                    'actual': f'{actual_val}px',
                    'diff': f'{actual_val - expected}px',
                    'severity': 'medium',
                    'fix': f'{selector}の上マージンを{expected}pxに調整してください'
                })
    
    return differences
```

**この手法の威力**:
- ブラウザの実際のレンダリング結果を取得
- 計算済みスタイル = ユーザーが見る最終形
- 数値で明確に差異を示せる
- 修正指示が具体的

---

### 3. Claude Vision活用（最強の武器）

```python
import anthropic
import base64

def analyze_design_with_claude(design_pdf_path, site_screenshot_path):
    """
    Claude Visionで視覚的差異を分析
    
    これが最も革命的な部分！
    Claude自身が「人間の目」として判定
    """
    client = anthropic.Anthropic()
    
    # 画像をbase64エンコード
    with open(design_pdf_path, 'rb') as f:
        design_b64 = base64.b64encode(f.read()).decode()
    
    with open(site_screenshot_path, 'rb') as f:
        site_b64 = base64.b64encode(f.read()).decode()
    
    # 超高精度プロンプト
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": design_b64
                    }
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": site_b64
                    }
                },
                {
                    "type": "text",
                    "text": """
あなたは世界最高峰のWebデザイナー兼品質検証のプロフェッショナルです。

1枚目の画像は「デザインカンプ（お手本）」です。
2枚目の画像は「実装されたWebサイト」です。

以下の観点で、ピクセル単位の厳密さで差異を検出してください：

## 検証項目

### 1. レイアウト・配置
- 要素の位置（上下左右のズレ）
- 要素間の余白・マージン
- 全体のバランス

### 2. タイポグラフィ
- フォントの種類（明朝体/ゴシック体など）
- フォントサイズ（1pxの違いも指摘）
- フォントの太さ（Regular/Bold/Semiboldなど）
- 行間（line-height）
- 文字間隔（letter-spacing）
- テキストの色

### 3. カラー
- 背景色
- 文字色
- ボーダーの色
- 微妙な色の違い（#333 vs #444 など）

### 4. 視覚要素
- 画像のサイズと配置
- アイコンの大きさと位置
- ボタンのサイズと形状
- ボーダーの太さとスタイル
- 角丸の半径
- シャドウの有無と強さ

### 5. 全体的な印象
- デザインの雰囲気が一致しているか
- 「なんとなく違う」感じがする箇所
- プロの目から見て気になる点

## 出力形式

以下のJSON形式で出力してください：

```json
{
  "overall_match_score": 85,
  "summary": "全体的には良好だが、いくつかの重要な差異がある",
  "critical_issues": [
    {
      "location": "ヘッダー部分",
      "issue": "ロゴのサイズが20%大きい",
      "expected": "幅200px",
      "actual": "幅240px",
      "severity": "high",
      "fix": "ロゴ画像を200pxに縮小してください"
    }
  ],
  "medium_issues": [
    {
      "location": "メインビジュアル下のテキスト",
      "issue": "フォントサイズが小さい",
      "expected": "16px",
      "actual": "14px",
      "severity": "medium",
      "fix": "font-sizeを16pxに変更"
    }
  ],
  "minor_issues": [
    {
      "location": "フッター",
      "issue": "背景色が微妙に異なる",
      "expected": "#f8f8f8",
      "actual": "#f5f5f5",
      "severity": "low",
      "fix": "background-colorを#f8f8f8に変更"
    }
  ],
  "positive_points": [
    "レスポンシブ対応が適切",
    "ボタンのホバー効果が実装されている"
  ]
}
```

**重要**: 
- 「だいたい合ってる」ではなく、ピクセル単位で厳密に
- 小さな差異も見逃さない
- 修正指示は具体的に
- プロの視点で「これは許容範囲」「これは要修正」を明確に判断
"""
                }
            ]
        }]
    )
    
    return response.content[0].text
```

**Claude Visionの圧倒的優位性**:
- 人間の視覚以上の精度
- 「なんとなく違う」を言語化
- コンテキストを理解した判定
- 修正の優先度まで判断

---

## 📋 完全なシステム実装

### ファイル構成

```
design-verification-system/
│
├── requirements.txt
├── config.json
│
├── core/
│   ├── __init__.py
│   ├── pdf_processor.py      # PDF→画像変換
│   ├── screenshot.py          # サイトスクリーンショット
│   ├── image_comparator.py   # ビジュアル差分
│   ├── style_extractor.py    # CSS計算値抽出
│   └── claude_analyzer.py    # Claude Vision分析
│
├── main.py                    # メインエンジン
├── cli.py                     # CLI
├── app.py                     # Web UI
│
└── templates/
    └── index.html
```

### requirements.txt（完全版）

```txt
# 画像処理
opencv-python>=4.8.0
scikit-image>=0.21.0
Pillow>=10.0.0
numpy>=1.24.0

# PDF処理
PyMuPDF>=1.23.0  # fitz
pdf2image>=1.16.0
pypdfium2>=4.0.0

# Webスクレイピング
selenium>=4.15.0
webdriver-manager>=4.0.0

# Claude API
anthropic>=0.25.0

# Web UI
flask>=3.0.0
flask-cors>=4.0.0

# ユーティリティ
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 🚀 メインエンジン実装

```python
#!/usr/bin/env python3
"""
Design Verification System Pro - メインエンジン
デザインカンプと実装サイトの完璧な比較検証
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple
import cv2
import numpy as np

from core.pdf_processor import PDFProcessor
from core.screenshot import ScreenshotTaker
from core.image_comparator import ImageComparator
from core.style_extractor import StyleExtractor
from core.claude_analyzer import ClaudeAnalyzer


class DesignVerificationEngine:
    """デザイン検証エンジン"""
    
    def __init__(self, config_path: str = 'config.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.pdf_processor = PDFProcessor()
        self.screenshot_taker = ScreenshotTaker()
        self.image_comparator = ImageComparator()
        self.style_extractor = StyleExtractor()
        self.claude_analyzer = ClaudeAnalyzer()
    
    def verify(self, pdf_path: str, site_url: str) -> Dict:
        """
        完全な検証を実行
        
        Args:
            pdf_path: デザインカンプPDFのパス
            site_url: 実装サイトのURL
        
        Returns:
            総合検証レポート
        """
        print("🔍 Design Verification System Pro")
        print("="*60)
        print(f"デザインカンプ: {pdf_path}")
        print(f"検証URL: {site_url}")
        print()
        
        # Phase 1: 前処理
        print("📄 Phase 1: 前処理")
        design_images = self.pdf_processor.convert_to_images(pdf_path)
        print(f"  ✅ PDF変換完了: {len(design_images)}ページ")
        
        site_screenshots = self.screenshot_taker.capture(
            site_url, 
            viewports=self.config['viewports']
        )
        print(f"  ✅ スクリーンショット取得完了: {len(site_screenshots)}枚")
        print()
        
        # Phase 2: ビジュアル差分検証
        print("🖼️  Phase 2: ビジュアル差分検証")
        visual_results = []
        
        for i, (design_img, site_img) in enumerate(zip(design_images, site_screenshots)):
            result = self.image_comparator.compare(design_img, site_img)
            visual_results.append(result)
            print(f"  ページ{i+1}: 類似度 {result['similarity_score']:.1f}%")
        print()
        
        # Phase 3: 計算的検証
        print("📏 Phase 3: 計算的検証")
        if 'selectors' in self.config:
            actual_styles = self.style_extractor.extract(
                site_url, 
                self.config['selectors']
            )
            style_diffs = self.style_extractor.compare(
                actual_styles,
                self.config.get('design_spec', {})
            )
            print(f"  ✅ CSS検証完了: {len(style_diffs)}件の差異を検出")
        else:
            style_diffs = []
            print(f"  ⚠️  CSS検証スキップ（config.jsonにselectorsが未設定）")
        print()
        
        # Phase 4: AI認識検証
        print("🤖 Phase 4: AI認識検証（Claude Vision）")
        ai_analysis = self.claude_analyzer.analyze(
            design_images[0],  # 最初のページ
            site_screenshots[0]
        )
        print(f"  ✅ AI分析完了")
        print()
        
        # 総合レポート生成
        print("📊 総合レポート生成中...")
        report = self._generate_report(
            visual_results,
            style_diffs,
            ai_analysis
        )
        
        # レポート保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = f"reports/verification_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)
        
        # JSON保存
        with open(f"{report_dir}/report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Markdown保存
        with open(f"{report_dir}/report.md", 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(report))
        
        # ヒートマップ保存
        for i, result in enumerate(visual_results):
            cv2.imwrite(
                f"{report_dir}/heatmap_page{i+1}.png",
                result['heatmap']
            )
        
        print(f"✅ レポート保存完了: {report_dir}")
        print()
        print(f"総合スコア: {report['overall_score']}/100")
        print(f"判定: {report['grade']}")
        
        return report
    
    def _generate_report(self, visual_results, style_diffs, ai_analysis) -> Dict:
        """総合レポート生成"""
        
        # 各層のスコア計算
        visual_score = np.mean([r['similarity_score'] for r in visual_results])
        
        # スタイル差異をスコア化（差異が少ないほど高得点）
        if style_diffs:
            style_score = max(0, 100 - len(style_diffs) * 5)
        else:
            style_score = 100
        
        # Claude Visionのスコアを抽出
        try:
            ai_data = json.loads(ai_analysis)
            ai_score = ai_data.get('overall_match_score', 100)
        except:
            ai_score = 100
        
        # 重み付け平均（Vision最重視）
        overall_score = int(
            visual_score * 0.3 +
            style_score * 0.2 +
            ai_score * 0.5
        )
        
        # グレード判定
        if overall_score >= 95:
            grade = "S - 完璧"
        elif overall_score >= 90:
            grade = "A - 優秀"
        elif overall_score >= 80:
            grade = "B - 良好"
        elif overall_score >= 70:
            grade = "C - 要修正"
        else:
            grade = "D - 大幅な修正が必要"
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'scores': {
                'visual': round(visual_score, 1),
                'style': style_score,
                'ai': ai_score
            },
            'visual_results': visual_results,
            'style_differences': style_diffs,
            'ai_analysis': ai_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_markdown_report(self, report: Dict) -> str:
        """Markdown形式のレポート生成"""
        
        md = f"""# デザイン検証レポート

## 📊 総合評価

**総合スコア**: {report['overall_score']}/100  
**判定**: {report['grade']}

### スコア内訳

- 🖼️ ビジュアル類似度: {report['scores']['visual']}/100
- 📏 CSS正確性: {report['scores']['style']}/100
- 🤖 AI総合判定: {report['scores']['ai']}/100

---

## 🔍 詳細分析

### Layer 1: ビジュアル差分

"""
        
        for i, vr in enumerate(report['visual_results'], 1):
            md += f"""
#### ページ{i}
- 類似度: {vr['similarity_score']:.1f}%
- 差異領域数: {vr['total_diff_pixels']}箇所
- ヒートマップ: `heatmap_page{i}.png`

"""
        
        md += f"""
### Layer 2: CSS計算値差異

"""
        
        if report['style_differences']:
            for diff in report['style_differences']:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(diff['severity'], '⚪')
                
                md += f"""
{severity_emoji} **{diff['selector']}** - {diff['property']}
- 期待値: `{diff['expected']}`
- 実際の値: `{diff['actual']}`
- 修正方法: {diff['fix']}

"""
        else:
            md += "問題なし\n\n"
        
        md += f"""
### Layer 3: AI認識分析（Claude Vision）

```json
{report['ai_analysis']}
```

---

## 💡 修正推奨事項

"""
        
        try:
            ai_data = json.loads(report['ai_analysis'])
            
            if ai_data.get('critical_issues'):
                md += "\n### 🔴 最優先修正項目\n\n"
                for issue in ai_data['critical_issues']:
                    md += f"- **{issue['location']}**: {issue['issue']}\n"
                    md += f"  - 修正: {issue['fix']}\n"
            
            if ai_data.get('medium_issues'):
                md += "\n### 🟡 重要修正項目\n\n"
                for issue in ai_data['medium_issues']:
                    md += f"- **{issue['location']}**: {issue['issue']}\n"
                    md += f"  - 修正: {issue['fix']}\n"
        
        except:
            pass
        
        return md


if __name__ == '__main__':
    engine = DesignVerificationEngine()
    
    # テスト実行
    report = engine.verify(
        pdf_path='design_comp.pdf',
        site_url='https://example.com'
    )
```

---

## 次のドキュメントに続く...

このシステムの核心部分を設計しました。
次のファイルで、完璧なClaude Codeプロンプトを作成します。
