#!/usr/bin/env python3
"""
Claude Analyzer - Claude Visionによるデザイン分析
人間の視覚を超える精度で差異を検出
"""

import os
import json
import base64
from typing import Dict, Optional
import numpy as np
from PIL import Image
from io import BytesIO

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeAnalyzer:
    """Claude Visionによる高度な分析"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Claude APIクライアントの初期化

        Args:
            api_key: Anthropic APIキー（省略時は環境変数から取得）
        """
        if anthropic is None:
            raise ImportError(
                "anthropicパッケージがインストールされていません。\n"
                "pip install anthropic を実行してください"
            )

        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEYが設定されていません。\n"
                "export ANTHROPIC_API_KEY='your-key' を実行してください"
            )

        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(self, design_img: np.ndarray, site_img: np.ndarray) -> Dict:
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

        result_text = response.content[0].text
        print("  ✅ Claude分析完了")

        # JSONをパース
        try:
            # JSONブロックを抽出（```json ... ``` の場合も対応）
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                json_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                json_text = result_text[json_start:json_end].strip()
            else:
                json_text = result_text.strip()

            result = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON解析エラー: {e}")
            # フォールバック: テキストのまま返す
            result = {
                "overall_match_score": 0,
                "summary": "JSON解析に失敗しました",
                "raw_response": result_text,
                "critical_issues": [],
                "high_issues": [],
                "medium_issues": [],
                "low_issues": []
            }

        return result

    def _numpy_to_base64(self, img_array: np.ndarray) -> str:
        """numpy配列をbase64文字列に変換"""
        # BGR -> RGB (OpenCVの場合)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            # BGRの場合のみ変換
            if img_array.dtype == np.uint8:
                img_array = img_array[:, :, ::-1]

        # PIL Image に変換
        img = Image.fromarray(img_array.astype('uint8'))

        # base64エンコード
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
      "location": "メインビジュアル > 見出し",
      "issue": "フォントサイズが小さい",
      "expected": "48px",
      "actual": "42px（推定）",
      "severity": "high",
      "fix": "h1 { font-size: 48px; } に変更してください",
      "impact": "インパクトが弱まり、訴求力が低下"
    }
  ],
  "medium_issues": [
    {
      "location": "ボタン",
      "issue": "角丸の半径が異なる",
      "expected": "8px",
      "actual": "4px（推定）",
      "severity": "medium",
      "fix": ".btn { border-radius: 8px; } に変更してください",
      "impact": "デザインの印象が若干変わる"
    }
  ],
  "low_issues": []
}
```

## 注意事項

- スコアは0-100で評価（100が完全一致）
- 各issueには必ず「fix」フィールドで具体的なCSS修正方法を記載
- 「impact」にはビジネスへの影響を記載
- 差異がない場合は各issuesを空配列にしてください
"""
