## Overview
WCAG Link Purpose Checker is a Python tool that automatically analyzes web pages for WCAG 2.4.4 compliance by identifying and evaluating link purposes using Selenium WebDriver and Claude AI. The tool provides detailed reports in JSON format, including XPath locations, link text, context, and compliance analysis.

## Installation
1. Clone the repository
```bash
git clone https://github.com/daishir0/wcag_link_purpose_checker.git
cd wcag_link_purpose_checker
```

2. Install Chrome and ChromeDriver
For Ubuntu/Debian:
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Install ChromeDriver
sudo apt-get install chromium-chromedriver
```

For other operating systems, please download and install:
- Google Chrome: https://www.google.com/chrome/
- ChromeDriver: https://chromedriver.chromium.org/downloads

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Configure the settings
```bash
cp config.sample.py config.py
```
Edit config.py with your settings:
- Set your Anthropic API key
- Adjust Chrome and ChromeDriver paths according to your environment
- Set DEBUG flag if needed

## Usage
Run the script with a target URL:
```bash
python wcag_link_purpose_checker.py https://example.com
```

The tool will output JSON-formatted results containing:
- XPath locations of links
- Link text and URL
- Context information (parent text, section heading, ARIA attributes)
- Compliance analysis (judgment, reason, and success techniques)

### Example Output
```json
{
  "links": [
    {
      "xpath": "//nav/ul/li[1]/a",
      "link_text": "会社概要",
      "url": "/about",
      "context": {
        "parent_text": "企業情報 会社概要",
        "section_heading": "企業情報",
        "aria_label": null,
        "aria_labelledby": null,
        "title": null
      },
      "analysis": {
        "judgment": "OK",
        "reason": "リンクテキスト単独で目的が明確",
        "success_techniques": [
          "G91: リンクの目的を説明したリンクテキストを提供する",
          "H30: a要素のリンクの目的を説明するリンクテキストを提供する"
        ]
      }
    }
  ]
}
```

## Notes
- Requires a valid Anthropic API key for Claude AI analysis
- Ensure proper Chrome and ChromeDriver versions match
- Links are processed in batches of 10 for efficient analysis
- The tool uses headless Chrome for rendering JavaScript-dependent content
- Analysis may take time depending on page size and number of links

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

# WCAGリンク目的チェッカー
## 概要
WCAGリンク目的チェッカーは、SeleniumウェブドライバーとClaude AIを使用して、ウェブページのWCAG 2.4.4準拠を自動的に分析し、リンクの目的を評価するPythonツールです。このツールは、XPathロケーション、リンクテキスト、コンテキスト、および準拠性分析を含む詳細なレポートをJSON形式で提供します。

## インストール方法
1. リポジトリのクローン
```bash
git clone https://github.com/daishir0/wcag_link_purpose_checker.git
cd wcag_link_purpose_checker
```

2. ChromeとChromeDriverのインストール
Ubuntu/Debian の場合:
```bash
# Chromeのインストール
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# ChromeDriverのインストール
sudo apt-get install chromium-chromedriver
```

その他のOSの場合は、以下からダウンロードしてインストール:
- Google Chrome: https://www.google.com/chrome/
- ChromeDriver: https://chromedriver.chromium.org/downloads

3. Python依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 設定の構成
```bash
cp config.sample.py config.py
```
config.pyを編集して設定:
- Anthropic APIキーの設定
- 環境に応じてChromeとChromeDriverのパスを調整
- 必要に応じてDEBUGフラグを設定

## 使い方
対象URLを指定してスクリプトを実行:
```bash
python wcag_link_purpose_checker.py https://example.com
```

ツールは以下を含むJSON形式の結果を出力します:
- リンクのXPathロケーション
- リンクテキストとURL
- コンテキスト情報（親要素のテキスト、セクション見出し、ARIA属性）
- 準拠性分析（判定、理由、成功手法）

### 実行例
```json
{
  "links": [
    {
      "xpath": "//nav/ul/li[1]/a",
      "link_text": "会社概要",
      "url": "/about",
      "context": {
        "parent_text": "企業情報 会社概要",
        "section_heading": "企業情報",
        "aria_label": null,
        "aria_labelledby": null,
        "title": null
      },
      "analysis": {
        "judgment": "OK",
        "reason": "リンクテキスト単独で目的が明確",
        "success_techniques": [
          "G91: リンクの目的を説明したリンクテキストを提供する",
          "H30: a要素のリンクの目的を説明するリンクテキストを提供する"
        ]
      }
    }
  ]
}
```

## 注意点
- Claude AI分析のために有効なAnthropic APIキーが必要です
- ChromeとChromeDriverのバージョンが一致していることを確認してください
- リンクは効率的な分析のために10個ずつのバッチで処理されます
- JavaScriptに依存するコンテンツのレンダリングにヘッドレスChromeを使用します
- ページのサイズとリンク数によって分析に時間がかかる場合があります

## ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。詳細はLICENSEファイルを参照してください。
