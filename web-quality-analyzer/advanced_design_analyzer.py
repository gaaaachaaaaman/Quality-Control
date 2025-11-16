#!/usr/bin/env python3
"""
Advanced Design Analyzer - 世界最高峰のCSS再現度検証エンジン
セクション単位・ピクセル単位での徹底比較
"""

import os
import base64
from io import BytesIO
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from collections import Counter
import numpy as np
from PIL import Image
import cv2

try:
    from sklearn.cluster import KMeans
except ImportError:
    KMeans = None


@dataclass
class SectionAnalysis:
    """セクション分析結果"""
    section_name: str
    y_start: int
    y_end: int
    similarity_score: float
    issues: List[Dict]
    diff_image_base64: str


@dataclass
class ColorPalette:
    """カラーパレット分析"""
    dominant_colors: List[Tuple[int, int, int]]  # RGB
    color_count: int
    palette_match_score: float  # 0-100


@dataclass
class LayoutAnalysis:
    """レイアウト構造分析"""
    element_count_diff: int
    positioning_accuracy: float  # 0-100
    spacing_issues: List[Dict]
    alignment_issues: List[Dict]


@dataclass
class AdvancedComparisonResult:
    """高度な比較結果"""
    overall_score: float
    grade: str
    section_analyses: List[SectionAnalysis]
    color_analysis: ColorPalette
    layout_analysis: LayoutAnalysis
    css_recommendations: List[str]
    heatmap_base64: str
    pixel_diff_percentage: float


class AdvancedDesignAnalyzer:
    """高度なデザイン分析クラス"""

    def __init__(self):
        self.design_img: Optional[np.ndarray] = None
        self.browser_img: Optional[np.ndarray] = None

    def analyze_comprehensive(self, design_img: Image.Image, browser_img: Image.Image) -> AdvancedComparisonResult:
        """包括的な分析を実行"""
        # 画像をNumPy配列に変換
        self.design_img = np.array(design_img.convert('RGB'))
        self.browser_img = np.array(browser_img.convert('RGB'))

        # サイズを揃える
        height = min(self.design_img.shape[0], self.browser_img.shape[0])
        width = min(self.design_img.shape[1], self.browser_img.shape[1])
        self.design_img = cv2.resize(self.design_img, (width, height))
        self.browser_img = cv2.resize(self.browser_img, (width, height))

        # 各種分析を実行
        section_analyses = self._analyze_sections()
        color_analysis = self._analyze_colors()
        layout_analysis = self._analyze_layout()
        heatmap = self._generate_heatmap()
        css_recommendations = self._generate_css_recommendations(section_analyses, color_analysis, layout_analysis)

        # 全体スコアの計算（加重平均）
        section_scores = [s.similarity_score for s in section_analyses]
        avg_section_score = sum(section_scores) / len(section_scores) if section_scores else 0

        overall_score = (
            avg_section_score * 0.5 +
            color_analysis.palette_match_score * 0.25 +
            layout_analysis.positioning_accuracy * 0.25
        )

        # ピクセル差分パーセンテージ
        diff = cv2.absdiff(self.design_img, self.browser_img)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
        pixel_diff_percentage = (np.count_nonzero(thresh) / thresh.size) * 100

        # グレード判定
        grade = self._calculate_grade(overall_score)

        return AdvancedComparisonResult(
            overall_score=round(overall_score, 2),
            grade=grade,
            section_analyses=section_analyses,
            color_analysis=color_analysis,
            layout_analysis=layout_analysis,
            css_recommendations=css_recommendations,
            heatmap_base64=heatmap,
            pixel_diff_percentage=round(pixel_diff_percentage, 2)
        )

    def _analyze_sections(self) -> List[SectionAnalysis]:
        """セクション単位で分析"""
        height = self.design_img.shape[0]

        # 画像を縦に分割（ヘッダー、メイン、フッターなど）
        sections = [
            ("ヘッダー領域", 0, height // 4),
            ("メインコンテンツ上部", height // 4, height // 2),
            ("メインコンテンツ下部", height // 2, 3 * height // 4),
            ("フッター領域", 3 * height // 4, height)
        ]

        results = []
        for section_name, y_start, y_end in sections:
            design_section = self.design_img[y_start:y_end, :]
            browser_section = self.browser_img[y_start:y_end, :]

            # セクションの差分を計算
            diff = cv2.absdiff(design_section, browser_section)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)

            # 類似度スコア
            diff_pixels = np.count_nonzero(thresh)
            total_pixels = thresh.size
            similarity = max(0, 100 - (diff_pixels / total_pixels) * 100)

            # 差分画像を生成
            diff_colored = diff.copy()
            diff_colored[thresh > 0] = [255, 0, 0]

            # Base64エンコード
            diff_img_pil = Image.fromarray(diff_colored)
            buffered = BytesIO()
            diff_img_pil.save(buffered, format="PNG")
            diff_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # 問題検出
            issues = []
            if similarity < 90:
                severity = "critical" if similarity < 70 else "high" if similarity < 85 else "medium"
                issues.append({
                    "severity": severity,
                    "description": f"{section_name}の再現率が{similarity:.1f}%です",
                    "impact": f"ユーザーが最初に目にする{section_name}で違和感を感じます",
                    "fix": f"{section_name}のレイアウト、フォント、色を見直してください"
                })

            results.append(SectionAnalysis(
                section_name=section_name,
                y_start=y_start,
                y_end=y_end,
                similarity_score=round(similarity, 2),
                issues=issues,
                diff_image_base64=diff_base64
            ))

        return results

    def _analyze_colors(self) -> ColorPalette:
        """カラーパレット分析"""
        # デザインカンプの主要色を抽出
        design_colors = self._extract_dominant_colors(self.design_img, n_colors=8)
        browser_colors = self._extract_dominant_colors(self.browser_img, n_colors=8)

        # 色の一致度を計算
        match_score = self._calculate_color_match(design_colors, browser_colors)

        return ColorPalette(
            dominant_colors=design_colors,
            color_count=len(design_colors),
            palette_match_score=match_score
        )

    def _extract_dominant_colors(self, img: np.ndarray, n_colors: int = 8) -> List[Tuple[int, int, int]]:
        """画像から主要な色を抽出"""
        # 画像をリシェイプ
        pixels = img.reshape(-1, 3)

        # 白と黒に近い色を除外
        mask = ~((pixels.sum(axis=1) > 240 * 3) | (pixels.sum(axis=1) < 15 * 3))
        filtered_pixels = pixels[mask]

        if len(filtered_pixels) == 0:
            return [(128, 128, 128)]  # グレー

        # K-meansクラスタリングで主要色を抽出
        if KMeans is not None and len(filtered_pixels) > n_colors:
            try:
                kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
                kmeans.fit(filtered_pixels)
                colors = kmeans.cluster_centers_.astype(int)
                return [tuple(color) for color in colors]
            except:
                pass

        # K-meansが使えない場合は、最も頻出する色を返す
        unique_colors = np.unique(filtered_pixels, axis=0)
        if len(unique_colors) > n_colors:
            # ランダムサンプリング
            indices = np.random.choice(len(unique_colors), n_colors, replace=False)
            colors = unique_colors[indices]
        else:
            colors = unique_colors

        return [tuple(color) for color in colors]

    def _calculate_color_match(self, colors1: List[Tuple], colors2: List[Tuple]) -> float:
        """2つのカラーパレットの一致度を計算"""
        if not colors1 or not colors2:
            return 0.0

        matches = 0
        threshold = 30  # 色差の許容値

        for c1 in colors1:
            for c2 in colors2:
                # ユークリッド距離で色差を計算
                diff = np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))
                if diff < threshold:
                    matches += 1
                    break

        match_percentage = (matches / len(colors1)) * 100
        return round(match_percentage, 2)

    def _analyze_layout(self) -> LayoutAnalysis:
        """レイアウト構造を分析"""
        # エッジ検出でレイアウト構造を抽出
        design_edges = cv2.Canny(cv2.cvtColor(self.design_img, cv2.COLOR_RGB2GRAY), 50, 150)
        browser_edges = cv2.Canny(cv2.cvtColor(self.browser_img, cv2.COLOR_RGB2GRAY), 50, 150)

        # 輪郭を検出
        design_contours, _ = cv2.findContours(design_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        browser_contours, _ = cv2.findContours(browser_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        element_count_diff = abs(len(design_contours) - len(browser_contours))

        # エッジの一致度
        edge_diff = cv2.absdiff(design_edges, browser_edges)
        positioning_accuracy = max(0, 100 - (np.count_nonzero(edge_diff) / edge_diff.size) * 100)

        # スペーシング問題の検出
        spacing_issues = []
        if positioning_accuracy < 80:
            spacing_issues.append({
                "severity": "high",
                "description": "要素の配置精度が低い",
                "fix": "margin, padding, position プロパティを確認してください"
            })

        alignment_issues = []
        if element_count_diff > 10:
            alignment_issues.append({
                "severity": "medium",
                "description": f"要素数が{element_count_diff}個異なります",
                "fix": "レイアウトの構造を見直してください"
            })

        return LayoutAnalysis(
            element_count_diff=element_count_diff,
            positioning_accuracy=round(positioning_accuracy, 2),
            spacing_issues=spacing_issues,
            alignment_issues=alignment_issues
        )

    def _generate_heatmap(self) -> str:
        """差分のヒートマップを生成"""
        # 差分を計算
        diff = cv2.absdiff(self.design_img, self.browser_img)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        # ヒートマップに変換
        heatmap = cv2.applyColorMap(diff_gray, cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        # Base64エンコード
        heatmap_pil = Image.fromarray(heatmap_rgb)
        buffered = BytesIO()
        heatmap_pil.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def _generate_css_recommendations(self, sections: List[SectionAnalysis],
                                     colors: ColorPalette, layout: LayoutAnalysis) -> List[str]:
        """具体的なCSS修正提案を生成"""
        recommendations = []

        # セクション別の推奨事項
        for section in sections:
            if section.similarity_score < 90:
                recommendations.append(
                    f"【{section.section_name}】再現率{section.similarity_score:.1f}% - "
                    f"セレクタを確認し、font-family, font-size, line-height, color を見直してください"
                )

        # カラー一致の推奨事項
        if colors.palette_match_score < 85:
            recommendations.append(
                f"【カラー】一致率{colors.palette_match_score:.1f}% - "
                f"デザインカンプのカラーコードを正確に取得し、CSS変数で管理してください"
            )

        # レイアウトの推奨事項
        if layout.positioning_accuracy < 80:
            recommendations.append(
                f"【レイアウト】配置精度{layout.positioning_accuracy:.1f}% - "
                f"Flexbox/Gridのgap, justify-content, align-itemsを確認してください"
            )

        # スペーシング
        if layout.spacing_issues:
            recommendations.append(
                "【余白】margin, paddingの値をデザインカンプと照合し、8pxグリッドシステムの採用を検討してください"
            )

        return recommendations[:10]  # 上位10件

    def _calculate_grade(self, score: float) -> str:
        """グレード判定"""
        if score >= 98: return "S+"
        elif score >= 95: return "S"
        elif score >= 90: return "A"
        elif score >= 85: return "B+"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        else: return "D"
