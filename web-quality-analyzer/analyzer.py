#!/usr/bin/env python3
"""
Web Quality Analyzer Pro - コア分析エンジン
世界最高水準のWebサイト品質分析ツール
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PIL import Image
import io


@dataclass
class Issue:
    """検出された問題"""
    category: str  # SEO, アクセシビリティ, パフォーマンス, デザイン, セキュリティ, コード品質
    severity: str  # critical, high, medium, low
    title: str
    description: str
    impact: str  # ビジネスへの影響
    fix: str  # 具体的な修正方法
    element: Optional[str] = None  # 該当する要素（あれば）

    def get_score_impact(self) -> int:
        """重大度に応じた減点スコア"""
        impacts = {"critical": 15, "high": 10, "medium": 5, "low": 2}
        return impacts.get(self.severity, 0)


@dataclass
class QualityReport:
    """品質レポート"""
    url: str
    analyzed_at: str
    total_score: int
    grade: str  # S, A, B, C, D
    issues: List[Issue]
    category_scores: Dict[str, int]
    summary: Dict[str, any]
    recommendations: List[str]

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'url': self.url,
            'analyzed_at': self.analyzed_at,
            'total_score': self.total_score,
            'grade': self.grade,
            'category_scores': self.category_scores,
            'summary': self.summary,
            'issues': [asdict(issue) for issue in self.issues],
            'recommendations': self.recommendations
        }

    def to_markdown(self) -> str:
        """Markdown形式のレポート生成"""
        md = f"""# Webサイト品質分析レポート

## 📊 総合評価

**分析URL:** {self.url}
**分析日時:** {self.analyzed_at}
**総合スコア:** {self.total_score}/100 (グレード: {self.grade})

### カテゴリ別スコア
"""
        for category, score in self.category_scores.items():
            emoji = self._get_category_emoji(category)
            md += f"- {emoji} **{category}:** {score}/100\n"

        md += f"\n## 📈 サイト概要\n\n"
        for key, value in self.summary.items():
            md += f"- **{key}:** {value}\n"

        if self.issues:
            md += "\n## ⚠️ 検出された問題点\n\n"

            # 重要度順にソート
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            sorted_issues = sorted(self.issues, key=lambda x: severity_order.get(x.severity, 99))

            current_severity = None
            for issue in sorted_issues:
                if issue.severity != current_severity:
                    current_severity = issue.severity
                    severity_labels = {
                        "critical": "🔴 致命的",
                        "high": "🟠 重要",
                        "medium": "🟡 中程度",
                        "low": "🟢 軽微"
                    }
                    md += f"\n### {severity_labels.get(issue.severity, issue.severity)}\n\n"

                md += f"#### {issue.title}\n\n"
                md += f"**カテゴリ:** {issue.category}  \n"
                md += f"**問題:** {issue.description}  \n"
                md += f"**ビジネスへの影響:** {issue.impact}  \n"
                md += f"**修正方法:** {issue.fix}  \n"
                if issue.element:
                    md += f"**該当箇所:** `{issue.element[:100]}`  \n"
                md += "\n---\n\n"

        if self.recommendations:
            md += "\n## 💡 優先的に対応すべき項目\n\n"
            for i, rec in enumerate(self.recommendations, 1):
                md += f"{i}. {rec}\n"

        md += "\n## 🎯 総評\n\n"
        md += self._generate_overall_comment()

        return md

    def _get_category_emoji(self, category: str) -> str:
        emojis = {
            "SEO": "🔍",
            "アクセシビリティ": "♿",
            "パフォーマンス": "⚡",
            "デザイン": "🎨",
            "セキュリティ": "🔒",
            "コード品質": "💻"
        }
        return emojis.get(category, "📋")

    def _generate_overall_comment(self) -> str:
        """総合コメントの生成"""
        if self.total_score >= 90:
            return "優れた品質のWebサイトです。細かな改善点はありますが、そのまま納品可能なレベルです。クライアントに自信を持って提示できます。"
        elif self.total_score >= 80:
            return "良好な品質です。いくつかの重要な改善点がありますが、基本的な品質基準は満たしています。指摘事項を修正すれば、高品質なサイトになります。"
        elif self.total_score >= 70:
            return "標準的な品質です。複数の改善が必要ですが、致命的な問題は少ないです。主要な指摘事項を優先的に対応してください。"
        elif self.total_score >= 60:
            return "品質に課題があります。納品前に必ず修正が必要です。特に重要度の高い問題から対応を開始してください。"
        else:
            return "品質基準を満たしていません。複数の重大な問題があり、大幅な修正が必要です。外注先に全面的な見直しを依頼してください。"


class WebQualityAnalyzer:
    """Webサイト品質分析エンジン"""

    def __init__(self, url_or_html: str, is_file: bool = False):
        self.url = url_or_html
        self.is_file = is_file
        self.soup: Optional[BeautifulSoup] = None
        self.issues: List[Issue] = []
        self.summary: Dict[str, any] = {}

    def analyze(self) -> QualityReport:
        """完全な品質分析を実行"""
        if self.is_file:
            with open(self.url, 'r', encoding='utf-8') as f:
                html = f.read()
            self.soup = BeautifulSoup(html, 'lxml')
            actual_url = "ローカルファイル"
        else:
            try:
                response = requests.get(self.url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                html = response.text
                self.soup = BeautifulSoup(html, 'lxml')
                actual_url = self.url
            except Exception as e:
                raise Exception(f"サイトの取得に失敗しました: {str(e)}")

        # 各種分析を実行
        self._analyze_basic_structure()
        self._analyze_seo()
        self._analyze_accessibility()
        self._analyze_performance()
        self._analyze_design()
        self._analyze_security()
        self._analyze_code_quality()

        # スコアリング
        category_scores = self._calculate_category_scores()
        total_score = self._calculate_total_score(category_scores)
        grade = self._calculate_grade(total_score)
        recommendations = self._generate_recommendations()

        return QualityReport(
            url=actual_url,
            analyzed_at=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
            total_score=total_score,
            grade=grade,
            issues=self.issues,
            category_scores=category_scores,
            summary=self.summary,
            recommendations=recommendations
        )

    def _analyze_basic_structure(self):
        """基本構造の分析"""
        body = self.soup.find('body')
        text_content = body.get_text(strip=True) if body else ""
        self.summary['総文字数'] = len(text_content)
        self.summary['総要素数'] = len(self.soup.find_all())
        self.summary['画像数'] = len(self.soup.find_all('img'))
        self.summary['リンク数'] = len(self.soup.find_all('a'))

        # DOCTYPE チェック
        if not str(self.soup).strip().lower().startswith('<!doctype html>'):
            self.issues.append(Issue(
                category="コード品質",
                severity="medium",
                title="DOCTYPE宣言が不適切",
                description="HTML5のDOCTYPE宣言が正しく記述されていません",
                impact="ブラウザが互換モードで動作し、予期しない表示崩れが発生する可能性があります",
                fix="ファイルの先頭に `<!DOCTYPE html>` を追加してください"
            ))

        # html lang属性
        html_tag = self.soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            self.issues.append(Issue(
                category="アクセシビリティ",
                severity="high",
                title="言語指定が未設定",
                description="<html>タグにlang属性がありません",
                impact="スクリーンリーダーが正しく読み上げできず、検索エンジンの評価も下がります",
                fix="<html>タグに `lang=\"ja\"` を追加してください",
                element=str(html_tag)[:100] if html_tag else None
            ))

    def _analyze_seo(self):
        """SEO分析"""
        # titleタグ
        title = self.soup.find('title')
        if not title or not title.string or len(title.string.strip()) == 0:
            self.issues.append(Issue(
                category="SEO",
                severity="critical",
                title="タイトルタグが未設定",
                description="<title>タグがないか、空です",
                impact="検索結果に表示されず、SEO評価が著しく低下します。訪問者数に直結する重大な問題です",
                fix="<head>内に `<title>適切なページタイトル（30-60文字）</title>` を追加してください"
            ))
        elif len(title.string) < 20:
            self.issues.append(Issue(
                category="SEO",
                severity="medium",
                title="タイトルが短すぎます",
                description=f"現在のタイトル: 「{title.string}」（{len(title.string)}文字）",
                impact="SEO効果が低く、検索結果でのクリック率が低下します",
                fix="30-60文字程度の、キーワードを含んだ具体的なタイトルに変更してください"
            ))
        else:
            self.summary['タイトル'] = title.string[:50]

        # meta description
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            self.issues.append(Issue(
                category="SEO",
                severity="high",
                title="ディスクリプションが未設定",
                description="meta descriptionタグがありません",
                impact="検索結果に適切な説明が表示されず、クリック率が大幅に低下します",
                fix="<head>内に `<meta name=\"description\" content=\"ページの説明（120-160文字）\">` を追加してください"
            ))
        elif len(meta_desc.get('content', '')) < 80:
            self.issues.append(Issue(
                category="SEO",
                severity="medium",
                title="ディスクリプションが短い",
                description=f"現在: {len(meta_desc.get('content', ''))}文字",
                impact="検索結果での訴求力が弱く、競合サイトに負ける可能性があります",
                fix="120-160文字程度の、ページ内容を魅力的に説明する文章に変更してください"
            ))

        # 見出し構造
        h1_tags = self.soup.find_all('h1')
        if len(h1_tags) == 0:
            self.issues.append(Issue(
                category="SEO",
                severity="high",
                title="H1タグが存在しません",
                description="ページにH1見出しがありません",
                impact="ページの主題が不明確になり、SEO評価が低下します",
                fix="ページの最も重要な見出しを `<h1>` タグでマークアップしてください"
            ))
        elif len(h1_tags) > 1:
            self.issues.append(Issue(
                category="SEO",
                severity="medium",
                title="H1タグが複数あります",
                description=f"H1タグが{len(h1_tags)}個検出されました",
                impact="ページの主題が曖昧になり、SEO効果が分散します",
                fix="H1タグは1ページに1つだけにしてください。他の見出しはH2以降を使用してください",
                element=", ".join([h1.get_text()[:30] for h1 in h1_tags[:3]])
            ))

        self.summary['見出し構造'] = f"H1:{len(self.soup.find_all('h1'))} H2:{len(self.soup.find_all('h2'))} H3:{len(self.soup.find_all('h3'))}"

        # OGP
        og_title = self.soup.find('meta', attrs={'property': 'og:title'})
        og_desc = self.soup.find('meta', attrs={'property': 'og:description'})
        og_image = self.soup.find('meta', attrs={'property': 'og:image'})

        missing_ogp = []
        if not og_title: missing_ogp.append('og:title')
        if not og_desc: missing_ogp.append('og:description')
        if not og_image: missing_ogp.append('og:image')

        if missing_ogp:
            self.issues.append(Issue(
                category="SEO",
                severity="medium",
                title="OGP設定が不完全",
                description=f"不足: {', '.join(missing_ogp)}",
                impact="SNSでシェアされた時に、適切な情報が表示されず、クリック率が低下します",
                fix=f"<head>内に不足しているOGPタグを追加してください。FacebookやTwitterでのシェア時に重要です"
            ))

    def _analyze_accessibility(self):
        """アクセシビリティ分析"""
        # 画像のalt属性
        images = self.soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]

        if images_without_alt:
            self.issues.append(Issue(
                category="アクセシビリティ",
                severity="high",
                title=f"alt属性のない画像が{len(images_without_alt)}個あります",
                description="画像に代替テキストが設定されていません",
                impact="視覚障害者が内容を理解できず、SEO評価も下がります。法的リスクもあります",
                fix="すべての<img>タグに `alt=\"画像の説明\"` を追加してください。装飾画像の場合は `alt=\"\"` としてください",
                element=str(images_without_alt[0])[:100] if images_without_alt else None
            ))

        # フォームのlabel
        inputs = self.soup.find_all('input', attrs={'type': ['text', 'email', 'tel', 'password']})
        inputs_without_label = []
        for inp in inputs:
            input_id = inp.get('id')
            if not input_id or not self.soup.find('label', attrs={'for': input_id}):
                if not inp.find_parent('label'):
                    inputs_without_label.append(inp)

        if inputs_without_label:
            self.issues.append(Issue(
                category="アクセシビリティ",
                severity="medium",
                title=f"ラベルのないフォーム要素が{len(inputs_without_label)}個あります",
                description="入力フィールドにlabelが関連付けられていません",
                impact="フォームの使いやすさが低下し、コンバージョン率に悪影響を与えます",
                fix="各inputに `<label for=\"入力欄のid\">ラベル名</label>` を追加するか、labelタグで囲んでください"
            ))

    def _analyze_performance(self):
        """パフォーマンス分析"""
        css_files = self.soup.find_all('link', attrs={'rel': 'stylesheet'})
        js_files = self.soup.find_all('script', src=True)

        self.summary['CSSファイル数'] = len(css_files)
        self.summary['JSファイル数'] = len(js_files)

        if len(css_files) > 5:
            self.issues.append(Issue(
                category="パフォーマンス",
                severity="medium",
                title="CSSファイルが多すぎます",
                description=f"{len(css_files)}個のCSSファイルが読み込まれています",
                impact="ページ読み込み速度が遅くなり、離脱率が上がります。特にモバイルで顕著です",
                fix="CSSファイルを統合して3ファイル以下にするか、インライン化を検討してください"
            ))

        if len(js_files) > 8:
            self.issues.append(Issue(
                category="パフォーマンス",
                severity="medium",
                title="JavaScriptファイルが多すぎます",
                description=f"{len(js_files)}個のJSファイルが読み込まれています",
                impact="ページの表示速度が大幅に低下し、ユーザー体験を損ないます",
                fix="JSファイルを統合・圧縮し、必要最小限にしてください。defer/async属性の活用も検討してください"
            ))

        # 遅延読み込み
        images = self.soup.find_all('img')
        images_with_loading = [img for img in images if img.get('loading') == 'lazy']

        if len(images) > 5 and len(images_with_loading) < len(images) * 0.5:
            self.issues.append(Issue(
                category="パフォーマンス",
                severity="low",
                title="画像の遅延読み込みが未実装",
                description="多くの画像がありますが、lazy loadingが設定されていません",
                impact="初期表示が遅くなり、ユーザーの待ち時間が増加します",
                fix="ファーストビュー外の画像に `loading=\"lazy\"` 属性を追加してください"
            ))

    def _analyze_design(self):
        """デザイン品質分析"""
        # viewport設定
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            self.issues.append(Issue(
                category="デザイン",
                severity="critical",
                title="viewport設定がありません",
                description="モバイル対応のviewportメタタグが未設定です",
                impact="スマートフォンで正しく表示されず、ユーザーの50%以上を失う可能性があります",
                fix="<head>内に `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">` を追加してください"
            ))

        # favicon
        favicon = self.soup.find('link', attrs={'rel': lambda x: x and 'icon' in x.lower()})
        if not favicon:
            self.issues.append(Issue(
                category="デザイン",
                severity="low",
                title="faviconが未設定",
                description="サイトアイコンが設定されていません",
                impact="ブラウザのタブやブックマークで識別しにくく、プロフェッショナルな印象が薄れます",
                fix="<head>内に `<link rel=\"icon\" href=\"/favicon.ico\">` を追加してください"
            ))

    def _analyze_security(self):
        """セキュリティ分析"""
        # HTTPSチェック
        if not self.is_file and self.url.startswith('http://'):
            self.issues.append(Issue(
                category="セキュリティ",
                severity="critical",
                title="HTTPで配信されています",
                description="サイトがHTTPSではなくHTTPで提供されています",
                impact="通信が暗号化されず、個人情報漏洩のリスクがあります。ブラウザの警告も表示されます",
                fix="SSL証明書を取得し、HTTPSでの配信に切り替えてください。Let's Encryptなら無料です"
            ))

        # 外部リンクのrel="noopener"
        external_links = [a for a in self.soup.find_all('a', target='_blank')
                         if a.get('href', '').startswith('http')]

        links_without_noopener = [
            a for a in external_links
            if not a.get('rel') or 'noopener' not in a.get('rel', [])
        ]

        if links_without_noopener:
            self.issues.append(Issue(
                category="セキュリティ",
                severity="medium",
                title=f"安全でない外部リンクが{len(links_without_noopener)}個あります",
                description="target=\"_blank\"のリンクにrel=\"noopener\"がありません",
                impact="タブナビング攻撃のリスクがあり、セキュリティ脆弱性になります",
                fix="外部リンクに `rel=\"noopener noreferrer\"` を追加してください"
            ))

    def _analyze_code_quality(self):
        """コード品質分析"""
        # インラインスタイルの多用
        elements_with_style = self.soup.find_all(style=True)
        if len(elements_with_style) > 10:
            self.issues.append(Issue(
                category="コード品質",
                severity="medium",
                title="インラインスタイルが多すぎます",
                description=f"{len(elements_with_style)}個の要素にstyle属性が直接記述されています",
                impact="メンテナンス性が低く、修正作業に時間がかかります。デザイン変更のコストが増大します",
                fix="スタイルをCSSファイルにまとめて、クラスベースのスタイリングに変更してください"
            ))

        # 古いHTML要素
        deprecated_tags = ['center', 'font', 'marquee', 'blink']
        found_deprecated = []
        for tag in deprecated_tags:
            if self.soup.find(tag):
                found_deprecated.append(tag)

        if found_deprecated:
            self.issues.append(Issue(
                category="コード品質",
                severity="high",
                title="非推奨のHTMLタグが使用されています",
                description=f"使用されている非推奨タグ: {', '.join(found_deprecated)}",
                impact="モダンブラウザで正しく表示されない可能性があり、プロフェッショナルではありません",
                fix=f"これらのタグを削除し、CSSで代替してください"
            ))

    def _calculate_category_scores(self) -> Dict[str, int]:
        """カテゴリ別スコアの計算"""
        categories = ["SEO", "アクセシビリティ", "パフォーマンス", "デザイン", "セキュリティ", "コード品質"]
        scores = {}

        for category in categories:
            category_issues = [i for i in self.issues if i.category == category]
            deduction = sum([i.get_score_impact() for i in category_issues])
            scores[category] = max(0, 100 - deduction)

        return scores

    def _calculate_total_score(self, category_scores: Dict[str, int]) -> int:
        """総合スコアの計算（重み付き平均）"""
        weights = {
            "SEO": 0.25,
            "アクセシビリティ": 0.20,
            "パフォーマンス": 0.20,
            "デザイン": 0.15,
            "セキュリティ": 0.15,
            "コード品質": 0.05
        }

        weighted_sum = sum([category_scores[cat] * weights[cat] for cat in category_scores])
        return int(weighted_sum)

    def _calculate_grade(self, score: int) -> str:
        """グレード判定"""
        if score >= 90: return "S"
        elif score >= 80: return "A"
        elif score >= 70: return "B"
        elif score >= 60: return "C"
        else: return "D"

    def _generate_recommendations(self) -> List[str]:
        """優先対応事項の生成"""
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        high_issues = [i for i in self.issues if i.severity == "high"]

        recommendations = []

        for issue in critical_issues[:3]:
            recommendations.append(f"【最優先】{issue.title} - {issue.fix}")

        for issue in high_issues[:3]:
            recommendations.append(f"【重要】{issue.title} - {issue.fix}")

        return recommendations[:5]
