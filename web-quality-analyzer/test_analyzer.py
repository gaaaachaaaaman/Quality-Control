#!/usr/bin/env python3
from analyzer import WebQualityAnalyzer

print("🔍 Web Quality Analyzer Pro - テスト開始")
print("="*60)

try:
    # テスト実行（ローカルファイルを使用）
    print("テストファイル: test.html を分析中...\n")
    analyzer = WebQualityAnalyzer("test.html", is_file=True)
    report = analyzer.analyze()

    print(f"✅ テスト成功！")
    print(f"総合スコア: {report.total_score}/100")
    print(f"グレード: {report.grade}")
    print(f"検出された問題: {len(report.issues)}件")

    # カテゴリ別スコア表示
    print("\nカテゴリ別スコア:")
    for category, score in report.category_scores.items():
        print(f"  - {category}: {score}/100")

except Exception as e:
    print(f"❌ エラーが発生しました:")
    print(f"エラー内容: {str(e)}")
    import traceback
    traceback.print_exc()
