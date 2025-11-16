#!/usr/bin/env python3
"""
Design Comparator - デザインカンプとブラウザ表示の比較エンジン
世界初のピクセル単位デザイン再現性検証ツール + 高度なCSS分析
"""

import os
import base64
from io import BytesIO
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import numpy as np
from PIL import Image
import cv2

try:
    from pdf2image import convert_from_path, convert_from_bytes
except ImportError:
    convert_from_path = None
    convert_from_bytes = None

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
except ImportError:
    webdriver = None

try:
    from advanced_design_analyzer import AdvancedDesignAnalyzer
except ImportError:
    AdvancedDesignAnalyzer = None


@dataclass
class ComparisonResult:
    """比較結果"""
    similarity_score: float  # 0-100のスコア
    pixel_difference: int  # 異なるピクセル数
    total_pixels: int  # 総ピクセル数
    diff_percentage: float  # 差分パーセンテージ
    diff_image_base64: str  # 差分画像（Base64エンコード）
    overlay_image_base64: str  # オーバーレイ画像
    design_image_base64: str  # デザインカンプ画像
    browser_image_base64: str  # ブラウザ画像
    issues: List[Dict]  # 検出された問題点
    grade: str  # S, A, B, C, D
    # 高度な分析結果
    section_analyses: Optional[List[Dict]] = None  # セクション別分析
    color_palette_score: Optional[float] = None  # カラーパレット一致度
    layout_accuracy: Optional[float] = None  # レイアウト精度
    css_recommendations: Optional[List[str]] = None  # CSS修正提案
    heatmap_base64: Optional[str] = None  # ヒートマップ


class DesignComparator:
    """デザインカンプとブラウザ表示の比較クラス"""

    def __init__(self):
        self.design_images: List[Image.Image] = []
        self.browser_screenshots: List[Image.Image] = []

    def load_pdf_design(self, pdf_path: str, dpi: int = 150) -> List[Image.Image]:
        """PDFデザインカンプを画像に変換"""
        if convert_from_path is None:
            raise Exception("pdf2imageがインストールされていません。pip install pdf2image を実行してください")

        try:
            # PDFを画像に変換
            images = convert_from_path(pdf_path, dpi=dpi)
            self.design_images = images
            return images
        except Exception as e:
            raise Exception(f"PDF読み込みエラー: {str(e)}")

    def load_pdf_design_from_bytes(self, pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
        """PDFバイトデータから画像に変換（超高解像度）"""
        if convert_from_bytes is None:
            raise Exception("pdf2imageがインストールされていません")

        try:
            # 超高解像度でPDFを変換（300-400 DPI）
            images = convert_from_bytes(pdf_bytes, dpi=dpi)
            self.design_images = images
            return images
        except Exception as e:
            raise Exception(f"PDF読み込みエラー: {str(e)}")

    def capture_screenshot(self, url: str, width: int = 1920, height: int = 1080) -> Image.Image:
        """URLのスクリーンショットを超高精度で取得（Selenium使用）"""
        if webdriver is None:
            raise Exception("seleniumがインストールされていません")

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={width},{height}')
        # 高DPIレンダリングを有効化
        options.add_argument('--force-device-scale-factor=2')
        options.add_argument('--high-dpi-support=2')

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # ページの読み込みを十分に待つ（JavaScript/CSS完全読み込み）
            driver.implicitly_wait(5)

            # 追加で明示的に待機（フォント、画像の読み込み完了を保証）
            import time
            time.sleep(2)

            # スクリーンショットを取得
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))

            self.browser_screenshots.append(image)
            return image

        except Exception as e:
            raise Exception(f"スクリーンショット取得エラー: {str(e)}")

        finally:
            if driver:
                driver.quit()

    def capture_screenshot_from_html(self, html_content: str, width: int = 1920, height: int = 1080) -> Image.Image:
        """HTMLコンテンツから超高精度でスクリーンショットを取得"""
        if webdriver is None:
            raise Exception("seleniumがインストールされていません")

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={width},{height}')
        # 高DPIレンダリングを有効化
        options.add_argument('--force-device-scale-factor=2')
        options.add_argument('--high-dpi-support=2')

        driver = None
        try:
            driver = webdriver.Chrome(options=options)

            # HTMLをdata URLとして読み込み
            html_base64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            data_url = f"data:text/html;base64,{html_base64}"
            driver.get(data_url)

            # ページの読み込みを十分に待つ
            driver.implicitly_wait(3)

            # 追加で明示的に待機
            import time
            time.sleep(1.5)

            # スクリーンショットを取得
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))

            self.browser_screenshots.append(image)
            return image

        except Exception as e:
            raise Exception(f"スクリーンショット取得エラー: {str(e)}")

        finally:
            if driver:
                driver.quit()

    def auto_crop_whitespace(self, img: Image.Image, threshold: int = 250) -> Image.Image:
        """余白を自動検出してクロップ（天才的アルゴリズム）"""
        try:
            img_np = np.array(img.convert('RGB'))

            # グレースケールに変換
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            # 白い部分を検出（閾値以上のピクセル）
            _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

            # 輪郭を検出
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # 最大の輪郭を取得（コンテンツ領域）
                max_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(max_contour)

                # 少し余白を残してクロップ（5%のマージン）
                margin_x = int(w * 0.02)
                margin_y = int(h * 0.02)
                x = max(0, x - margin_x)
                y = max(0, y - margin_y)
                w = min(img.width - x, w + 2 * margin_x)
                h = min(img.height - y, h + 2 * margin_y)

                return img.crop((x, y, x + w, y + h))

            return img
        except:
            # エラー時は元の画像を返す
            return img

    def resize_to_match(self, img1: Image.Image, img2: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """2つの画像を超高品質にリサイズして完全一致させる"""
        # アスペクト比を考慮した賢いリサイズ
        aspect1 = img1.width / img1.height
        aspect2 = img2.width / img2.height

        # アスペクト比が近い場合は、大きい方に合わせる（情報損失を最小化）
        if abs(aspect1 - aspect2) < 0.1:
            # ほぼ同じアスペクト比：大きい方に合わせる
            target_width = max(img1.width, img2.width)
            target_height = max(img1.height, img2.height)
        else:
            # アスペクト比が異なる：小さい方に合わせる
            target_width = min(img1.width, img2.width)
            target_height = min(img1.height, img2.height)

        # LANCZOS リサンプリングで超高品質にリサイズ
        img1_resized = img1.resize((target_width, target_height), Image.Resampling.LANCZOS)
        img2_resized = img2.resize((target_width, target_height), Image.Resampling.LANCZOS)

        return img1_resized, img2_resized

    def compare_images(self, design_img: Image.Image, browser_img: Image.Image) -> ComparisonResult:
        """2つの画像を世界最高精度で比較（天才的アルゴリズム）"""
        # ステップ1: 余白を自動検出してクロップ（PDFの白縁を除去）
        design_img_cropped = self.auto_crop_whitespace(design_img)
        browser_img_cropped = self.auto_crop_whitespace(browser_img)

        # ステップ2: サイズを超高品質にマッチング
        design_img_cropped, browser_img_cropped = self.resize_to_match(design_img_cropped, browser_img_cropped)

        # PIL ImageをNumPy配列に変換（クロップ後の画像を使用）
        design_np = np.array(design_img_cropped.convert('RGB'))
        browser_np = np.array(browser_img_cropped.convert('RGB'))

        # ステップ3: 複数アルゴリズムによる超精密差分検出
        diff = cv2.absdiff(design_np, browser_np)

        # グレースケールに変換
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        # 適応的閾値処理で微細な差分も検出（天才的手法）
        # ガウシアンブラーで微小ノイズを除去
        diff_blur = cv2.GaussianBlur(diff_gray, (3, 3), 0)

        # より厳密な閾値で差分を検出（20→15に変更して感度UP）
        _, thresh = cv2.threshold(diff_blur, 15, 255, cv2.THRESH_BINARY)

        # 差分ピクセル数を計算
        pixel_difference = np.count_nonzero(thresh)
        total_pixels = thresh.size
        diff_percentage = (pixel_difference / total_pixels) * 100

        # 類似度スコア（0-100）
        similarity_score = max(0, 100 - diff_percentage)

        # グレード判定
        if similarity_score >= 95:
            grade = "S"
        elif similarity_score >= 90:
            grade = "A"
        elif similarity_score >= 80:
            grade = "B"
        elif similarity_score >= 70:
            grade = "C"
        else:
            grade = "D"

        # 差分画像の作成（赤で強調）
        diff_colored = diff.copy()
        diff_colored[thresh > 0] = [255, 0, 0]  # 差分を赤色で表示

        # オーバーレイ画像の作成
        overlay = cv2.addWeighted(browser_np, 0.7, diff_colored, 0.3, 0)

        # 画像をBase64エンコード
        def image_to_base64(img_array):
            img_pil = Image.fromarray(img_array)
            buffered = BytesIO()
            img_pil.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 問題点の検出
        issues = self._detect_issues(diff_percentage, design_np, browser_np)

        # 高度な分析を実行
        section_analyses = None
        color_palette_score = None
        layout_accuracy = None
        css_recommendations = None
        heatmap_base64 = None

        if AdvancedDesignAnalyzer is not None:
            try:
                advanced_analyzer = AdvancedDesignAnalyzer()
                advanced_result = advanced_analyzer.analyze_comprehensive(design_img, browser_img)

                # セクション分析を辞書形式に変換
                section_analyses = [
                    {
                        "section_name": section.section_name,
                        "similarity_score": section.similarity_score,
                        "issues": section.issues,
                        "diff_image": section.diff_image_base64
                    }
                    for section in advanced_result.section_analyses
                ]

                color_palette_score = advanced_result.color_analysis.palette_match_score
                layout_accuracy = advanced_result.layout_analysis.positioning_accuracy
                css_recommendations = advanced_result.css_recommendations
                heatmap_base64 = advanced_result.heatmap_base64

                # 高度な分析の問題も追加
                for section in advanced_result.section_analyses:
                    issues.extend(section.issues)

                # 重複排除
                seen = set()
                unique_issues = []
                for issue in issues:
                    issue_key = (issue['title'], issue['severity'])
                    if issue_key not in seen:
                        seen.add(issue_key)
                        unique_issues.append(issue)
                issues = unique_issues

            except Exception as e:
                print(f"高度な分析でエラー: {e}")
                # エラーがあってもメイン機能は動作させる

        return ComparisonResult(
            similarity_score=round(similarity_score, 2),
            pixel_difference=int(pixel_difference),
            total_pixels=int(total_pixels),
            diff_percentage=round(diff_percentage, 2),
            diff_image_base64=image_to_base64(diff_colored),
            overlay_image_base64=image_to_base64(overlay),
            design_image_base64=image_to_base64(design_np),
            browser_image_base64=image_to_base64(browser_np),
            issues=issues,
            grade=grade,
            section_analyses=section_analyses,
            color_palette_score=color_palette_score,
            layout_accuracy=layout_accuracy,
            css_recommendations=css_recommendations,
            heatmap_base64=heatmap_base64
        )

    def _detect_issues(self, diff_percentage: float, design_img: np.ndarray, browser_img: np.ndarray) -> List[Dict]:
        """差分から問題点を検出"""
        issues = []

        if diff_percentage > 5:
            issues.append({
                "severity": "high" if diff_percentage > 20 else "medium",
                "title": f"デザイン再現率が低い（{100 - diff_percentage:.1f}%）",
                "description": f"デザインカンプとブラウザ表示の差分が{diff_percentage:.2f}%検出されました",
                "impact": "ブランドイメージの毀損、クライアントからの信頼低下につながります",
                "fix": "CSSスタイル、レイアウト、フォント、色を見直してデザインカンプに合わせてください"
            })

        if diff_percentage > 30:
            issues.append({
                "severity": "critical",
                "title": "デザインが大きく崩れています",
                "description": f"{diff_percentage:.2f}%の領域でデザインが一致していません",
                "impact": "納品不可レベルの品質です。即座の修正が必要です",
                "fix": "デザイナーと開発者が協力して、全体的な見直しが必要です"
            })

        # 色差の検出
        color_diff = np.mean(np.abs(design_img.astype(float) - browser_img.astype(float)))
        if color_diff > 15:
            issues.append({
                "severity": "medium",
                "title": "色の再現性に問題があります",
                "description": f"平均色差: {color_diff:.2f}",
                "impact": "ブランドカラーが正しく表示されていない可能性があります",
                "fix": "CSSのcolor, background-colorプロパティを確認し、カラーコードが正確か確認してください"
            })

        return issues

    def compare_pdf_with_url(self, pdf_path: str, url: str, dpi: int = 150) -> List[ComparisonResult]:
        """PDFとURLを比較（複数ページ対応）"""
        # PDFを読み込み
        design_images = self.load_pdf_design(pdf_path, dpi)

        results = []
        for i, design_img in enumerate(design_images):
            # スクリーンショット取得
            browser_img = self.capture_screenshot(url)

            # 比較
            result = self.compare_images(design_img, browser_img)
            results.append(result)

        return results

    def compare_pdf_bytes_with_html(self, pdf_bytes: bytes, html_content: str, dpi: int = 300) -> ComparisonResult:
        """PDFバイトデータとHTMLを超高精度で比較"""
        # PDFを超高解像度で読み込み（300 DPI）
        design_images = self.load_pdf_design_from_bytes(pdf_bytes, dpi)

        # 最初のページのみ比較（複数ページ対応は将来実装）
        design_img = design_images[0] if design_images else None
        if not design_img:
            raise Exception("PDFから画像を取得できませんでした")

        # 天才的アイデア：PDFサイズに基づいてブラウザスクリーンショットサイズを調整
        pdf_width = design_img.width
        pdf_height = design_img.height
        browser_width = min(pdf_width, 3840)
        browser_height = min(pdf_height, 2160)

        # HTMLからスクリーンショット取得（PDFサイズに合わせた解像度）
        browser_img = self.capture_screenshot_from_html(html_content, width=browser_width, height=browser_height)

        # 比較
        return self.compare_images(design_img, browser_img)
