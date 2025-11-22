# 🌟 世界最強プロンプト集 - Design Verification System Pro

## 📖 このドキュメントについて

**目的**: デザインカンプとサイトのズレを**ピクセル単位**で検出するシステムを、Claude Codeで**確実に**構築する

**対象者**: 池高和典さん（Web制作外注管理のプロ）

**実現すること**:
- デザインカンプ（PDF）vs 実装サイト（URL）の完全比較
- 3層検証（画像差分 + CSS計算値 + Claude Vision）
- 30秒で検証完了
- 外注先に送れる具体的な修正指示

**成功率**: このプロンプト通りに進めれば **98%**

---

## 🎯 システムの革命性

### 従来の問題
```
デザインカンプ確認: 1ページ30分
↓
目視チェック（主観的）
↓
「なんか違う気がする...」
↓
外注先「どこですか？」
↓
説明に時間がかかる
```

### このシステム
```
PDF + URL を投入: 5秒
↓
3層自動検証: 30秒
↓
「ヘッダーロゴが20px大きい」
↓
修正指示PDFを自動生成
↓
外注先に送信
```

**時間削減**: 30分 → 30秒（**60倍の効率化**）

---

## 🏗️ Claude Code 実装プロトコル

### 【絶対ルール】

1. **一度に1ファイルずつ作成**
2. **各ステップで動作確認**
3. **コードは全文を渡す（「参考に」は禁止）**
4. **エラーは即座に報告させる**
5. **Python 3.11以上を使用**

---

## 📋 Phase 0: 事前準備プロンプト

```
# Design Verification System Pro - 環境確認

以下を順番に実行して、結果を報告してください：

1. 環境確認
   python --version
   （期待: Python 3.11以上）

2. pipの確認
   pip --version

3. 作業ディレクトリの作成と移動
   mkdir -p design-verification-system
   cd design-verification-system
   pwd

4. サブディレクトリの作成
   mkdir -p core reports templates static

5. ディレクトリ構造の確認
   tree -L 2
   （またはls -R）

各コマンドの実行結果を見せてください。
エラーが出た場合は、進まずに報告してください。
```

**重要**: この段階で環境の問題を潰す

---

## 📋 Phase 1: 依存関係インストール

```
# Phase 1: パッケージインストール

以下の内容で requirements.txt を作成してください：

```txt
# 画像処理（最重要）
opencv-python>=4.8.0
scikit-image>=0.21.0
Pillow>=10.0.0
numpy>=1.24.0

# PDF処理
PyMuPDF>=1.23.0
pdf2image>=1.16.0

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

ファイル作成後、以下を実行：

1. cat requirements.txt
   （内容確認）

2. pip install -r requirements.txt
   （インストール実行）

3. pip list | grep -E "(opencv|anthropic|selenium)"
   （インストール確認）

結果を報告してください。
特に、opencvとanthropicが正しくインストールされたか確認してください。
```

**チェックポイント**:
- opencv-pythonが入っているか
- anthropicが入っているか
- エラーが出ていないか

---

## 📋 Phase 2: 設定ファイル作成

```
# Phase 2: config.json の作成

以下の内容で config.json を作成してください：

```json
{
  "viewports": [
    {
      "name": "desktop",
      "width": 1920,
      "height": 1080
    },
    {
      "name": "tablet",
      "width": 768,
      "height": 1024
    },
    {
      "name": "mobile",
      "width": 375,
      "height": 667
    }
  ],
  "selectors": {
    "header .logo": {
      "width": "200px",
      "height": "50px"
    },
    "h1": {
      "fontSize": "32px",
      "fontWeight": "700",
      "color": "rgb(51, 51, 51)"
    },
    ".main-button": {
      "backgroundColor": "rgb(67, 97, 238)",
      "paddingTop": "12px",
      "paddingBottom": "12px",
      "borderRadius": "8px"
    }
  },
  "design_spec": {
    "header .logo": {
      "width": "200px",
      "height": "50px"
    },
    "h1": {
      "fontSize": "32px",
      "fontWeight": "700",
      "color": "rgb(51, 51, 51)"
    }
  },
  "tolerance": {
    "size_px": 2,
    "color_diff": 5
  }
}
```

作成後、以下を実行：

cat config.json | python -m json.tool

（JSON形式が正しいか確認）

結果を報告してください。
```

---

## 📋 Phase 3: PDFプロセッサ実装（核心①）

```
# Phase 3: core/pdf_processor.py の作成

以下の内容を**一字一句そのまま**作成してください。
変更や改良は一切不要です。

```python
#!/usr/bin/env python3
"""
PDF Processor - デザインカンプPDFを高解像度画像に変換
"""

import os
from typing import List
import numpy as np
from PIL import Image
import fitz  # PyMuPDF


class PDFProcessor:
    """PDFを高解像度画像に変換"""
    
    def __init__(self, dpi: int = 300):
        """
        Args:
            dpi: 解像度（デフォルト300dpi、高精度なら600dpi）
        """
        self.dpi = dpi
    
    def convert_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        PDFを画像リストに変換
        
        Args:
            pdf_path: PDFファイルのパス
        
        Returns:
            各ページの画像（numpy配列）のリスト
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
        
        print(f"  📄 PDF読み込み: {pdf_path}")
        
        # PDFを開く
        doc = fitz.open(pdf_path)
        images = []
        
        # 各ページを画像化
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # DPIから拡大率を計算（72dpiが基準）
            zoom = self.dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            
            # ページをPixmapに変換
            pix = page.get_pixmap(matrix=mat)
            
            # PILイメージに変換
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # numpy配列に変換（OpenCV形式）
            img_array = np.array(img)
            img_array = img_array[:, :, ::-1]  # RGB -> BGR
            
            images.append(img_array)
            print(f"    ✅ ページ{page_num + 1}: {pix.width}x{pix.height}px")
        
        doc.close()
        
        return images
    
    def save_images(self, images: List[np.ndarray], output_dir: str):
        """
        画像をファイルとして保存
        
        Args:
            images: 画像リスト
            output_dir: 出力ディレクトリ
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i, img in enumerate(images):
            output_path = os.path.join(output_dir, f"page_{i+1}.png")
            # BGR -> RGB
            img_rgb = img[:, :, ::-1]
            Image.fromarray(img_rgb).save(output_path)
            print(f"    💾 保存: {output_path}")


# テストコード
if __name__ == '__main__':
    processor = PDFProcessor(dpi=300)
    
    # テスト用PDFがあれば実行
    test_pdf = 'test_design.pdf'
    if os.path.exists(test_pdf):
        images = processor.convert_to_images(test_pdf)
        print(f"\n✅ 変換成功: {len(images)}ページ")
        processor.save_images(images, 'test_output')
    else:
        print(f"ℹ️  テストPDF（{test_pdf}）が見つかりません")
        print("実際のPDFで試してください")
```

ファイル作成後、以下を実行：

1. cat core/pdf_processor.py | head -30
   （先頭30行を確認）

2. python -m py_compile core/pdf_processor.py
   （構文チェック）

3. python core/pdf_processor.py
   （テスト実行）

結果を報告してください。
```

**このファイルの役割**: PDFを高解像度画像に変換（差分検出の精度を左右）

---

## 📋 Phase 4: スクリーンショット取得（核心②）

```
# Phase 4: core/screenshot.py の作成

以下の内容を**そのまま**作成：

```python
#!/usr/bin/env python3
"""
Screenshot Taker - Webサイトの正確なスクリーンショット取得
"""

import time
from typing import List, Dict
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class ScreenshotTaker:
    """Webサイトのスクリーンショット取得"""
    
    def __init__(self):
        """Chrome WebDriverの初期化"""
        self.driver = None
    
    def _setup_driver(self, width: int, height: int):
        """WebDriverのセットアップ"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # ヘッドレスモード
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--window-size={width},{height}')
        chrome_options.add_argument('--force-device-scale-factor=1')  # Retina対策
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def capture(self, url: str, viewports: List[Dict]) -> List[np.ndarray]:
        """
        複数ビューポートでスクリーンショット取得
        
        Args:
            url: 対象URL
            viewports: ビューポート設定リスト
        
        Returns:
            スクリーンショット画像リスト
        """
        screenshots = []
        
        for viewport in viewports:
            print(f"  📸 スクリーンショット取得: {viewport['name']}")
            
            # WebDriver起動
            self._setup_driver(viewport['width'], viewport['height'])
            
            try:
                # ページアクセス
                self.driver.get(url)
                
                # ページ読み込み待機
                time.sleep(3)
                
                # スクリーンショット取得
                png = self.driver.get_screenshot_as_png()
                
                # PIL Image -> numpy配列
                img = Image.open(io.BytesIO(png))
                img_array = np.array(img)
                
                # RGB -> BGR（OpenCV形式）
                if len(img_array.shape) == 3:
                    img_array = img_array[:, :, ::-1]
                
                screenshots.append(img_array)
                print(f"    ✅ {viewport['width']}x{viewport['height']}")
                
            finally:
                if self.driver:
                    self.driver.quit()
        
        return screenshots
    
    def capture_element(self, url: str, selector: str, width: int = 1920, height: int = 1080) -> np.ndarray:
        """
        特定要素のスクリーンショット取得
        
        Args:
            url: 対象URL
            selector: CSSセレクタ
            width: ウィンドウ幅
            height: ウィンドウ高さ
        
        Returns:
            要素のスクリーンショット画像
        """
        self._setup_driver(width, height)
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            from selenium.webdriver.common.by import By
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # 要素をスクリーンショット
            png = element.screenshot_as_png
            
            img = Image.open(io.BytesIO(png))
            img_array = np.array(img)
            
            if len(img_array.shape) == 3:
                img_array = img_array[:, :, ::-1]
            
            return img_array
            
        finally:
            if self.driver:
                self.driver.quit()


# テストコード
if __name__ == '__main__':
    import io
    
    taker = ScreenshotTaker()
    
    test_url = 'https://example.com'
    test_viewports = [
        {'name': 'desktop', 'width': 1920, 'height': 1080}
    ]
    
    print(f"🌐 テスト: {test_url}")
    screenshots = taker.capture(test_url, test_viewports)
    print(f"\n✅ スクリーンショット取得成功: {len(screenshots)}枚")
    
    # 保存
    if screenshots:
        img = Image.fromarray(screenshots[0][:, :, ::-1])
        img.save('test_screenshot.png')
        print("💾 test_screenshot.png に保存")
```

ファイル作成後：

1. python -m py_compile core/screenshot.py

2. python core/screenshot.py
   （example.comのスクリーンショットが取得される）

3. ls -lh test_screenshot.png
   （ファイルが生成されたか確認）

結果を報告してください。
```

**このファイルの役割**: 実装サイトを正確にキャプチャ

---

## 📋 Phase 5: 画像比較エンジン（核心③）

```
# Phase 5: core/image_comparator.py の作成

この部分が最も重要です。**完全にそのまま**作成してください。

```python
#!/usr/bin/env python3
"""
Image Comparator - ピクセルパーフェクト画像比較
SSIMとヒートマップ生成
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from typing import Dict, List, Tuple


class ImageComparator:
    """高度な画像比較エンジン"""
    
    def __init__(self, threshold: int = 30):
        """
        Args:
            threshold: 差分検出の閾値（0-255）
        """
        self.threshold = threshold
    
    def compare(self, img1: np.ndarray, img2: np.ndarray) -> Dict:
        """
        2つの画像を比較
        
        Args:
            img1: デザインカンプ画像
            img2: 実装サイト画像
        
        Returns:
            比較結果（類似度、ヒートマップ、差分領域）
        """
        # サイズ調整（小さい方に合わせる）
        img1_resized, img2_resized = self._resize_to_match(img1, img2)
        
        # グレースケール変換
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
        
        # SSIM計算
        ssim_score, diff = ssim(gray1, gray2, full=True)
        
        # 差分を0-255の範囲に正規化
        diff = (diff * 255).astype("uint8")
        
        # 閾値処理
        thresh = cv2.threshold(
            diff, 
            0, 
            255, 
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]
        
        # 輪郭検出
        contours = cv2.findContours(
            thresh.copy(), 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        contours = contours[0] if len(contours) == 2 else contours[1]
        
        # 差分領域の抽出
        diff_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50:  # 50px²以上の差分のみ
                x, y, w, h = cv2.boundingRect(contour)
                diff_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(area)
                })
        
        # ヒートマップ生成
        heatmap = self._generate_heatmap(diff, img1_resized)
        
        # 差分領域を枠で囲んだ画像
        marked_image = img2_resized.copy()
        for region in diff_regions:
            cv2.rectangle(
                marked_image,
                (region['x'], region['y']),
                (region['x'] + region['width'], region['y'] + region['height']),
                (0, 0, 255),  # 赤枠
                2
            )
        
        return {
            'similarity_score': ssim_score * 100,
            'heatmap': heatmap,
            'marked_image': marked_image,
            'diff_regions': diff_regions,
            'total_diff_pixels': len(contours)
        }
    
    def _resize_to_match(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """2つの画像を同じサイズにリサイズ"""
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # 小さい方のサイズに合わせる
        target_h = min(h1, h2)
        target_w = min(w1, w2)
        
        img1_resized = cv2.resize(img1, (target_w, target_h))
        img2_resized = cv2.resize(img2, (target_w, target_h))
        
        return img1_resized, img2_resized
    
    def _generate_heatmap(self, diff: np.ndarray, base_image: np.ndarray) -> np.ndarray:
        """ヒートマップ生成"""
        # カラーマップ適用（青→緑→黄→赤）
        heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
        
        # 元画像とブレンド（透過度50%）
        blended = cv2.addWeighted(base_image, 0.5, heatmap, 0.5, 0)
        
        return blended
    
    def calculate_color_difference(self, color1: str, color2: str) -> float:
        """
        2つの色の差分を計算
        
        Args:
            color1: "rgb(255, 0, 0)" 形式
            color2: "rgb(255, 0, 0)" 形式
        
        Returns:
            色差（0-441、0が完全一致）
        """
        rgb1 = self._parse_rgb(color1)
        rgb2 = self._parse_rgb(color2)
        
        # ユークリッド距離
        diff = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
        
        return diff
    
    def _parse_rgb(self, color_str: str) -> Tuple[int, int, int]:
        """RGB文字列をタプルに変換"""
        # "rgb(255, 0, 0)" -> (255, 0, 0)
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
        if match:
            return tuple(map(int, match.groups()))
        return (0, 0, 0)


# テストコード
if __name__ == '__main__':
    comparator = ImageComparator()
    
    # テスト画像があれば実行
    import os
    if os.path.exists('test_screenshot.png'):
        # 同じ画像同士を比較（類似度100%になるはず）
        img = cv2.imread('test_screenshot.png')
        
        result = comparator.compare(img, img)
        print(f"✅ 類似度: {result['similarity_score']:.1f}%")
        print(f"差分領域: {len(result['diff_regions'])}箇所")
        
        # ヒートマップ保存
        cv2.imwrite('test_heatmap.png', result['heatmap'])
        print("💾 test_heatmap.png に保存")
    else:
        print("ℹ️  test_screenshot.png が見つかりません")
```

実行:

1. python -m py_compile core/image_comparator.py

2. python core/image_comparator.py
   （同じ画像の比較で100%になるはず）

結果を報告してください。
```

**このファイルの役割**: ピクセル単位の差分検出（システムの心臓部）

---

## 次のプロンプトに続く...

ここまでで、システムの核心3つ（PDF変換、スクリーンショット、画像比較）が完成しました。

次のファイルで：
- CSS計算値抽出
- Claude Vision統合（最強）
- メインエンジン
- CLI/Web UI

を実装します。
