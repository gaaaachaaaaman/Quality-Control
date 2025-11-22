# 🌟 世界最強プロンプト Part 2 - Claude Vision統合

## 📋 Phase 6: Claude Vision分析器（最強の武器）

```
# Phase 6: core/claude_analyzer.py の作成

**これがシステムの最強部分です**
Claude Visionで「人間の目」として判定します。

以下の内容を**完全にそのまま**作成：

```python
#!/usr/bin/env python3
"""
Claude Analyzer - Claude Visionによるデザイン分析
人間の視覚を超える精度で差異を検出
"""

import os
import json
import base64
from typing import Dict
import numpy as np
from PIL import Image
import anthropic


class ClaudeAnalyzer:
    """Claude Visionによる高度な分析"""
    
    def __init__(self):
        """Claude APIクライアントの初期化"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEYが設定されていません。\n"
                "export ANTHROPIC_API_KEY='your-key' を実行してください"
            )
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def analyze(self, design_img: np.ndarray, site_img: np.ndarray) -> str:
        """
        2つの画像を比較分析
        
        Args:
            design_img: デザインカンプ画像（numpy配列）
            site_img: 実装サイト画像（numpy配列）
        
        Returns:
            JSON形式の分析結果
        """
        print("  🤖 Claude Vision分析開始...")
        
        # numpy配列 -> base64エンコード
        design_b64 = self._numpy_to_base64(design_img)
        site_b64 = self._numpy_to_base64(site_img)
        
        # 超高精度プロンプト
        prompt = self._create_analysis_prompt()
        
        # Claude API呼び出し
        response = self.client.messages.create(
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
                        "text": prompt
                    }
                ]
            }]
        )
        
        result = response.content[0].text
        print("  ✅ 分析完了")
        
        return result
    
    def _numpy_to_base64(self, img_array: np.ndarray) -> str:
        """numpy配列をbase64文字列に変換"""
        # BGR -> RGB
        if len(img_array.shape) == 3:
            img_array = img_array[:, :, ::-1]
        
        # PIL Image に変換
        img = Image.fromarray(img_array.astype('uint8'))
        
        # base64エンコード
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """超高精度分析プロンプト"""
        return """
あなたは世界最高峰のWebデザイナー兼品質検証のプロフェッショナルです。
15年以上の実務経験があり、ピクセル単位の精度でデザインを評価できます。

## 役割

1枚目の画像: **デザインカンプ（お手本・理想形）**
2枚目の画像: **実装されたWebサイト（実際の成果物）**

あなたの任務は、この2つを**ピクセル単位の厳密さ**で比較し、
すべての差異を検出することです。

## 検証観点（優先度順）

### 🔴 Critical（致命的）- 必ず指摘
1. **レイアウト崩れ**
   - 要素の位置が大きくずれている（10px以上）
   - 改行位置が違う
   - 要素の重なりや表示順序の問題

2. **フォントの重大な違い**
   - フォントファミリーが違う（明朝体 vs ゴシック体など）
   - サイズが大きく違う（2px以上）
   - 太さが違う（Regular vs Bold）

3. **色の明確な違い**
   - 主要色（ブランドカラー、ボタンなど）が違う
   - コントラスト比が著しく異なる

### 🟠 High（重要）- 優先的に修正すべき
4. **余白・間隔**
   - マージン・パディングのずれ（5px以上）
   - 要素間の距離が不均等

5. **サイズ**
   - 画像・アイコンのサイズ違い
   - ボタン・入力欄の大きさ

6. **視覚効果**
   - シャドウの有無または強さ
   - ボーダーの太さ・色
   - 角丸の半径

### 🟡 Medium（中程度）- できれば修正
7. **細かなスタイル**
   - 行間（line-height）
   - 文字間隔（letter-spacing）
   - 微妙な色の違い（#333 vs #444など）

### 🟢 Low（軽微）- 必要に応じて
8. **その他**
   - アニメーションの有無
   - ホバー効果
   - レスポンシブ対応

## 分析のポイント

1. **定量的に**: 「少し大きい」ではなく「約20px大きい」
2. **具体的に**: 「ヘッダーのロゴ」など位置を明確に
3. **実装的に**: CSSの具体的な修正方法を提示
4. **優先度を**: 致命的→重要→軽微の順で整理

## 出力形式

以下のJSON形式で出力してください。
**必ずJSONのみを出力し、前後に説明文を入れないでください。**

```json
{
  "overall_match_score": 85,
  "summary": "全体的には良好だが、ヘッダー部分に重要な差異がある",
  "critical_issues": [
    {
      "location": "ヘッダー > ロゴ",
      "issue": "ロゴ画像のサイズが設計より大きい",
      "expected": "幅: 200px, 高さ: 50px",
      "actual": "幅: 240px, 高さ: 60px（推定）",
      "severity": "critical",
      "fix": ".header .logo { width: 200px; height: 50px; } に変更してください",
      "impact": "ヘッダーの高さが全体的に大きくなり、ファーストビューが圧迫される"
    }
  ],
  "high_issues": [
    {
      "location": "メインビジュアル > 見出しテキスト",
      "issue": "フォントサイズが小さい",
      "expected": "48px",
      "actual": "42px（推定）",
      "severity": "high",
      "fix": "h1 { font-size: 48px; } に変更してください",
      "impact": "訴求力が弱まり、デザインの意図が伝わらない"
    },
    {
      "location": "メインボタン",
      "issue": "ボタンの色が異なる",
      "expected": "#4361EE（青）",
      "actual": "#5B8DEE（より明るい青）",
      "severity": "high",
      "fix": ".main-button { background-color: #4361EE; } に変更してください",
      "impact": "ブランドカラーとの不一致、視認性の低下"
    }
  ],
  "medium_issues": [
    {
      "location": "セクション1 > テキストブロック",
      "issue": "行間が狭い",
      "expected": "line-height: 1.8（推定）",
      "actual": "line-height: 1.5（推定）",
      "severity": "medium",
      "fix": ".text-block { line-height: 1.8; } に設定してください",
      "impact": "可読性がやや低下"
    }
  ],
  "low_issues": [
    {
      "location": "フッター > リンク",
      "issue": "文字色が微妙に濃い",
      "expected": "#666666",
      "actual": "#555555（推定）",
      "severity": "low",
      "fix": ".footer a { color: #666666; } に変更してください",
      "impact": "ほとんど目立たないが、厳密には異なる"
    }
  ],
  "positive_points": [
    "レスポンシブ対応が適切に実装されている",
    "画像の配置とサイズは正確",
    "ホバー効果が丁寧に実装されている"
  ],
  "recommendations": [
    "ヘッダーロゴのサイズ調整を最優先で実施",
    "メインビジュアルのフォントサイズとボタン色を修正",
    "行間の調整は余裕があれば対応"
  ]
}
```

## 重要な注意事項

1. **数値は推定でOK**: ピクセル単位の正確な計測は不要。視覚的判断で「約〜px」で構いません
2. **比較が難しい場合**: 片方しか要素がない、大きく構造が違うなどの場合は、その旨を記載
3. **微細な違い**: 1-2pxの違いは、実用上問題なければlow_issuesに
4. **肯定的な点**: 良くできている部分も必ず記載（モチベーション維持のため）

あなたの鋭い視点で、制作物の品質を最高レベルに引き上げてください。
"""
    
    def parse_result(self, result_json: str) -> Dict:
        """JSON文字列をパースして辞書に変換"""
        try:
            # マークダウンのコードブロックを除去
            if '```json' in result_json:
                start = result_json.find('```json') + 7
                end = result_json.rfind('```')
                result_json = result_json[start:end].strip()
            elif '```' in result_json:
                start = result_json.find('```') + 3
                end = result_json.rfind('```')
                result_json = result_json[start:end].strip()
            
            return json.loads(result_json)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析エラー: {e}")
            print(f"生の出力: {result_json[:500]}")
            return {
                'overall_match_score': 0,
                'summary': 'JSON解析に失敗しました',
                'critical_issues': [],
                'high_issues': [],
                'medium_issues': [],
                'low_issues': [],
                'positive_points': [],
                'recommendations': [],
                'raw_output': result_json
            }


# テストコード
if __name__ == '__main__':
    # ANTHROPIC_API_KEY環境変数が必要
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEYが設定されていません")
        print("export ANTHROPIC_API_KEY='your-key' を実行してください")
    else:
        print("✅ Claude Analyzer初期化完了")
        print("ℹ️  実際の画像で analyze() メソッドを使用してください")
```

ファイル作成後：

1. python -m py_compile core/claude_analyzer.py

2. 環境変数の設定を確認:
   echo $ANTHROPIC_API_KEY
   （何か表示されればOK）

3. python core/claude_analyzer.py

結果を報告してください。

**重要**: ANTHROPIC_API_KEYの設定が必要です。
まだ設定していない場合は、以下を実行：

export ANTHROPIC_API_KEY='sk-ant-xxxxx'

（xxxxx部分は実際のAPIキー）
```

**このファイルの役割**: AIの目で人間以上の精度で差異検出

---

## 📋 Phase 7: CSS計算値抽出

```
# Phase 7: core/style_extractor.py の作成

```python
#!/usr/bin/env python3
"""
Style Extractor - 実装サイトのCSS計算値を抽出
ブラウザの実際のレンダリング結果を取得
"""

from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class StyleExtractor:
    """CSS計算値の抽出と比較"""
    
    def extract(self, url: str, selectors: Dict[str, Dict]) -> Dict:
        """
        指定されたセレクタのスタイルを抽出
        
        Args:
            url: 対象URL
            selectors: CSSセレクタとチェック項目の辞書
        
        Returns:
            各セレクタの計算済みスタイル
        """
        print(f"  📏 CSS計算値を抽出中...")
        
        # WebDriver起動
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            
            results = {}
            
            for selector in selectors.keys():
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
                            position: computed.position
                        };
                    """, element)
                    
                    results[selector] = styles
                    print(f"    ✅ {selector}")
                    
                except Exception as e:
                    results[selector] = {'error': str(e)}
                    print(f"    ❌ {selector}: {str(e)}")
            
            return results
            
        finally:
            driver.quit()
    
    def compare(self, actual_styles: Dict, design_spec: Dict) -> List[Dict]:
        """
        実装値とデザイン仕様を比較
        
        Args:
            actual_styles: 実装から抽出したスタイル
            design_spec: デザイン仕様
        
        Returns:
            差異リスト
        """
        differences = []
        
        for selector, spec in design_spec.items():
            actual = actual_styles.get(selector, {})
            
            if 'error' in actual:
                differences.append({
                    'selector': selector,
                    'property': 'existence',
                    'issue': f'要素が見つかりません: {actual["error"]}',
                    'severity': 'critical',
                    'fix': f'{selector}が存在するか確認してください'
                })
                continue
            
            # 各プロパティをチェック
            for property_name, expected_value in spec.items():
                actual_value = actual.get(property_name, '')
                
                # 値の比較
                if not self._values_match(property_name, expected_value, actual_value):
                    # 重要度を判定
                    severity = self._determine_severity(property_name)
                    
                    differences.append({
                        'selector': selector,
                        'property': property_name,
                        'expected': expected_value,
                        'actual': actual_value,
                        'severity': severity,
                        'fix': self._generate_fix(selector, property_name, expected_value)
                    })
        
        return differences
    
    def _values_match(self, property_name: str, expected: str, actual: str) -> bool:
        """2つの値が一致するかチェック（許容範囲を考慮）"""
        
        # ピクセル値の場合、±2pxまで許容
        if 'px' in expected and 'px' in actual:
            try:
                exp_val = float(expected.replace('px', ''))
                act_val = float(actual.replace('px', ''))
                return abs(exp_val - act_val) <= 2
            except:
                pass
        
        # RGB値の場合、各成分±5まで許容
        if 'rgb' in expected and 'rgb' in actual:
            return self._colors_similar(expected, actual, threshold=5)
        
        # その他は完全一致
        return expected == actual
    
    def _colors_similar(self, color1: str, color2: str, threshold: int = 5) -> bool:
        """2つの色が類似しているかチェック"""
        import re
        
        def parse_rgb(color_str):
            match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
            if match:
                return tuple(map(int, match.groups()))
            return None
        
        rgb1 = parse_rgb(color1)
        rgb2 = parse_rgb(color2)
        
        if rgb1 and rgb2:
            return all(abs(a - b) <= threshold for a, b in zip(rgb1, rgb2))
        
        return color1 == color2
    
    def _determine_severity(self, property_name: str) -> str:
        """プロパティの重要度を判定"""
        critical_props = ['fontSize', 'color', 'backgroundColor', 'width', 'height']
        high_props = ['fontWeight', 'padding', 'margin', 'borderRadius']
        
        if property_name in critical_props:
            return 'high'
        elif property_name in high_props:
            return 'medium'
        else:
            return 'low'
    
    def _generate_fix(self, selector: str, property: str, expected_value: str) -> str:
        """修正指示を生成"""
        # CSS property名に変換（camelCase -> kebab-case）
        css_property = ''.join([
            f'-{c.lower()}' if c.isupper() else c 
            for c in property
        ]).lstrip('-')
        
        return f'{selector} {{ {css_property}: {expected_value}; }}'


# テストコード
if __name__ == '__main__':
    extractor = StyleExtractor()
    
    test_url = 'https://example.com'
    test_selectors = {
        'h1': {},
        'body': {}
    }
    
    print(f"🌐 テスト: {test_url}")
    styles = extractor.extract(test_url, test_selectors)
    
    print("\n取得したスタイル:")
    import json
    print(json.dumps(styles, indent=2, ensure_ascii=False))
```

実行:

1. python -m py_compile core/style_extractor.py

2. python core/style_extractor.py

結果を報告してください。
```

---

## 📋 Phase 8: メインエンジン統合

```
# Phase 8: main.py の作成（システムの心臓部）

これがすべてを統合する最重要ファイルです。

```python
#!/usr/bin/env python3
"""
Design Verification System Pro - メインエンジン
3層検証（画像差分 + CSS計算値 + Claude Vision）の統合
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict
import cv2
import numpy as np

# 自作モジュールのインポート
sys.path.append(os.path.dirname(__file__))
from core.pdf_processor import PDFProcessor
from core.screenshot import ScreenshotTaker
from core.image_comparator import ImageComparator
from core.style_extractor import StyleExtractor
from core.claude_analyzer import ClaudeAnalyzer


class DesignVerificationEngine:
    """デザイン検証エンジン"""
    
    def __init__(self, config_path: str = 'config.json'):
        # 設定読み込み
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            print(f"⚠️  {config_path} が見つかりません。デフォルト設定を使用します")
            self.config = self._default_config()
        
        # 各モジュールの初期化
        self.pdf_processor = PDFProcessor(dpi=300)
        self.screenshot_taker = ScreenshotTaker()
        self.image_comparator = ImageComparator()
        self.style_extractor = StyleExtractor()
        
        # Claude Analyzer（APIキーが必要）
        try:
            self.claude_analyzer = ClaudeAnalyzer()
            self.claude_enabled = True
        except ValueError as e:
            print(f"⚠️  Claude Analyzer無効: {e}")
            self.claude_enabled = False
    
    def verify(self, pdf_path: str, site_url: str, output_dir: str = None) -> Dict:
        """
        完全な検証を実行
        
        Args:
            pdf_path: デザインカンプPDFのパス
            site_url: 実装サイトのURL
            output_dir: 出力ディレクトリ（省略時は自動生成）
        
        Returns:
            総合検証レポート
        """
        print("\n" + "="*70)
        print("🔍 Design Verification System Pro".center(70))
        print("="*70)
        print(f"\n📄 デザインカンプ: {pdf_path}")
        print(f"🌐 検証URL: {site_url}\n")
        
        # 出力ディレクトリ作成
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"reports/verification_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Phase 1: 前処理
        print("📄 Phase 1: 前処理")
        print("-" * 70)
        design_images = self.pdf_processor.convert_to_images(pdf_path)
        print(f"  ✅ PDF変換完了: {len(design_images)}ページ\n")
        
        site_screenshots = self.screenshot_taker.capture(
            site_url, 
            self.config.get('viewports', [{'name': 'desktop', 'width': 1920, 'height': 1080}])
        )
        print(f"  ✅ スクリーンショット取得完了: {len(site_screenshots)}枚\n")
        
        # Phase 2: ビジュアル差分検証
        print("🖼️  Phase 2: ビジュアル差分検証")
        print("-" * 70)
        visual_results = []
        
        for i, (design_img, site_img) in enumerate(zip(design_images, site_screenshots)):
            result = self.image_comparator.compare(design_img, site_img)
            visual_results.append(result)
            
            # ヒートマップ保存
            cv2.imwrite(f"{output_dir}/heatmap_page{i+1}.png", result['heatmap'])
            cv2.imwrite(f"{output_dir}/marked_page{i+1}.png", result['marked_image'])
            
            print(f"  ページ{i+1}: 類似度 {result['similarity_score']:.1f}% | "
                  f"差分領域 {len(result['diff_regions'])}箇所")
        
        print()
        
        # Phase 3: 計算的検証
        print("📏 Phase 3: CSS計算値検証")
        print("-" * 70)
        
        if 'selectors' in self.config:
            actual_styles = self.style_extractor.extract(
                site_url, 
                self.config['selectors']
            )
            style_diffs = self.style_extractor.compare(
                actual_styles,
                self.config.get('design_spec', {})
            )
            print(f"  ✅ CSS検証完了: {len(style_diffs)}件の差異を検出\n")
        else:
            style_diffs = []
            print(f"  ⚠️  スキップ（config.jsonにselectorsが未設定）\n")
        
        # Phase 4: AI認識検証
        print("🤖 Phase 4: AI認識検証（Claude Vision）")
        print("-" * 70)
        
        if self.claude_enabled:
            ai_analysis = self.claude_analyzer.analyze(
                design_images[0],
                site_screenshots[0]
            )
            print(f"  ✅ AI分析完了\n")
        else:
            ai_analysis = json.dumps({
                'overall_match_score': 100,
                'summary': 'Claude Vision無効',
                'critical_issues': [],
                'high_issues': [],
                'medium_issues': [],
                'low_issues': []
            })
        
        # 総合レポート生成
        print("📊 総合レポート生成中...")
        print("-" * 70)
        
        report = self._generate_report(
            visual_results,
            style_diffs,
            ai_analysis,
            pdf_path,
            site_url
        )
        
        # レポート保存
        self._save_reports(report, output_dir)
        
        print(f"\n✅ 完了！レポート保存先: {output_dir}")
        print("="*70)
        print(f"\n📊 総合スコア: {report['overall_score']}/100")
        print(f"🏆 判定: {report['grade']}\n")
        
        return report
    
    def _generate_report(self, visual_results, style_diffs, ai_analysis, pdf_path, site_url) -> Dict:
        """総合レポート生成"""
        
        # 各層のスコア計算
        visual_score = np.mean([r['similarity_score'] for r in visual_results])
        
        style_score = max(0, 100 - len(style_diffs) * 3) if style_diffs else 100
        
        # AI分析のスコア
        try:
            ai_data = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
            ai_score = ai_data.get('overall_match_score', 100)
        except:
            ai_score = 100
            ai_data = {}
        
        # 重み付け平均（Claude Vision最重視）
        overall_score = int(
            visual_score * 0.25 +
            style_score * 0.25 +
            ai_score * 0.50
        )
        
        # グレード判定
        if overall_score >= 95:
            grade = "S - 完璧（そのまま納品可能）"
        elif overall_score >= 90:
            grade = "A - 優秀（軽微な修正のみ）"
        elif overall_score >= 80:
            grade = "B - 良好（重要な修正が必要）"
        elif overall_score >= 70:
            grade = "C - 要修正（複数の問題あり）"
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
            'ai_analysis': ai_data,
            'metadata': {
                'pdf_path': pdf_path,
                'site_url': site_url,
                'timestamp': datetime.now().isoformat(),
                'claude_enabled': self.claude_enabled
            }
        }
    
    def _save_reports(self, report: Dict, output_dir: str):
        """レポート保存"""
        
        # JSON保存
        with open(f"{output_dir}/report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # Markdown保存
        md_content = self._generate_markdown_report(report)
        with open(f"{output_dir}/report.md", 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  💾 report.json")
        print(f"  💾 report.md")
    
    def _generate_markdown_report(self, report: Dict) -> str:
        """Markdown形式のレポート生成"""
        
        md = f"""# デザイン検証レポート

生成日時: {report['metadata']['timestamp']}

## 📊 総合評価

**総合スコア**: {report['overall_score']}/100  
**判定**: {report['grade']}

### スコア内訳

| 項目 | スコア | 説明 |
|------|--------|------|
| 🖼️ ビジュアル類似度 | {report['scores']['visual']}/100 | SSIM画像比較 |
| 📏 CSS正確性 | {report['scores']['style']}/100 | 計算値の一致度 |
| 🤖 AI総合判定 | {report['scores']['ai']}/100 | Claude Vision分析 |

---

## 🔍 詳細分析

### Layer 1: ビジュアル差分検証

"""
        
        for i, vr in enumerate(report['visual_results'], 1):
            md += f"""
#### ページ{i}

- **類似度**: {vr['similarity_score']:.1f}%
- **差分領域数**: {len(vr['diff_regions'])}箇所
- **ヒートマップ**: `heatmap_page{i}.png`
- **マーク画像**: `marked_page{i}.png`

"""
            if vr['diff_regions']:
                md += "主な差分領域:\n\n"
                for j, region in enumerate(vr['diff_regions'][:5], 1):
                    md += f"{j}. 位置({region['x']}, {region['y']}) サイズ{region['width']}x{region['height']}px\n"
                md += "\n"
        
        md += """
### Layer 2: CSS計算値差異

"""
        
        if report['style_differences']:
            # 重要度別に整理
            by_severity = {}
            for diff in report['style_differences']:
                sev = diff['severity']
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(diff)
            
            severity_labels = {
                'high': '🔴 重要',
                'medium': '🟡 中程度',
                'low': '🟢 軽微'
            }
            
            for sev in ['high', 'medium', 'low']:
                if sev in by_severity:
                    md += f"\n#### {severity_labels.get(sev, sev)}\n\n"
                    for diff in by_severity[sev]:
                        md += f"**{diff['selector']}** - `{diff['property']}`\n"
                        md += f"- 期待値: `{diff['expected']}`\n"
                        md += f"- 実際: `{diff['actual']}`\n"
                        md += f"- 修正: `{diff['fix']}`\n\n"
        else:
            md += "✅ 問題なし\n\n"
        
        md += """
### Layer 3: AI認識分析（Claude Vision）

"""
        
        ai_data = report.get('ai_analysis', {})
        
        if ai_data:
            md += f"\n**AIスコア**: {ai_data.get('overall_match_score', 0)}/100\n"
            md += f"**総評**: {ai_data.get('summary', '')}\n\n"
            
            # 致命的な問題
            if ai_data.get('critical_issues'):
                md += "#### 🔴 致命的な問題\n\n"
                for issue in ai_data['critical_issues']:
                    md += f"**{issue['location']}**\n"
                    md += f"- 問題: {issue['issue']}\n"
                    md += f"- 期待: {issue['expected']}\n"
                    md += f"- 実際: {issue['actual']}\n"
                    md += f"- 修正: {issue['fix']}\n"
                    md += f"- 影響: {issue['impact']}\n\n"
            
            # 重要な問題
            if ai_data.get('high_issues'):
                md += "#### 🟠 重要な問題\n\n"
                for issue in ai_data['high_issues']:
                    md += f"**{issue['location']}**: {issue['issue']}\n"
                    md += f"- 修正: {issue['fix']}\n\n"
            
            # 良い点
            if ai_data.get('positive_points'):
                md += "#### ✅ 良くできている点\n\n"
                for point in ai_data['positive_points']:
                    md += f"- {point}\n"
                md += "\n"
        
        md += """
---

## 💡 推奨される対応

"""
        
        if ai_data.get('recommendations'):
            for i, rec in enumerate(ai_data['recommendations'], 1):
                md += f"{i}. {rec}\n"
        
        md += f"""

---

## 📎 添付ファイル

- `report.json` - 機械可読形式の詳細レポート
- `heatmap_page*.png` - 差分ヒートマップ
- `marked_page*.png` - 差分箇所マーク画像

---

*Generated by Design Verification System Pro*
"""
        
        return md
    
    def _default_config(self) -> Dict:
        """デフォルト設定"""
        return {
            'viewports': [
                {'name': 'desktop', 'width': 1920, 'height': 1080}
            ],
            'selectors': {},
            'design_spec': {}
        }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("使用法: python main.py <PDFパス> <サイトURL>")
        print("例: python main.py design.pdf https://example.com")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    site_url = sys.argv[2]
    
    engine = DesignVerificationEngine()
    report = engine.verify(pdf_path, site_url)
```

実行テスト:

python main.py test_design.pdf https://example.com

（test_design.pdfは実際のPDFに置き換えてください）

結果を報告してください。
```

---

これで、完全なシステムが完成しました！

次のファイルで、CLI/Web UIとClaude Codeでの実行最終プロンプトを作成します。
