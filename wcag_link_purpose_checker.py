import sys
import time
import json
import anthropic
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import ANTHROPIC_API_KEY, CHROME_BINARY_PATH, CHROME_DRIVER_PATH, DEBUG

def get_page_source(url):
    """
    ChromeDriverを使用してページにアクセスし、JavaScriptが実行された後のソースを取得
    """
    # Chromeのオプション設定
    options = Options()
    options.headless = True
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--enable-logging')
    options.add_argument('--log-level=1')
    options.add_argument("--headless")

    # ChromeDriverの設定
    service = Service(executable_path=CHROME_DRIVER_PATH)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # ページにアクセス
        driver.get(url)
        
        # ページの最下部までスクロール
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 最下部までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 新しいコンテンツがロードされるのを待つ
            time.sleep(2)
            
            # 新しい高さを取得
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # スクロールしても高さが変わらなければ終了
            if new_height == last_height:
                break
            last_height = new_height
        
        # 最終的なページソースを取得
        page_source = driver.page_source
        return page_source
    finally:
        driver.quit()

def extract_link_info(html_content):
    """
    BeautifulSoupを使用してリンク情報を抽出
    """
    soup = BeautifulSoup(html_content, 'lxml')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        # リンク情報を収集
        link_info = {
            "element": str(a_tag),  # 要素全体のHTML
            "xpath": generate_xpath(a_tag),  # XPathを生成
            "link_text": a_tag.get_text(strip=True),
            "url": a_tag.get('href', ''),
            "context": {
                "parent_text": a_tag.parent.get_text(strip=True) if a_tag.parent else "",
                "section_heading": get_nearest_heading(a_tag),
                "aria_label": a_tag.get('aria-label', None),
                "aria_labelledby": a_tag.get('aria-labelledby', None),
                "title": a_tag.get('title', None)
            }
        }
        links.append(link_info)
    
    return links

def generate_xpath(element):
    """
    要素のXPathを生成
    """
    components = []
    child = element
    for parent in element.parents:
        siblings = parent.find_all(child.name, recursive=False)
        if len(siblings) > 1:
            index = siblings.index(child) + 1
            components.append(f"{child.name}[{index}]")
        else:
            components.append(child.name)
        child = parent
        if parent.name == 'body':
            break
    components.reverse()
    return '//' + '/'.join(components)

def get_nearest_heading(element):
    """
    最も近い見出し要素のテキストを取得
    """
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    current = element
    while current:
        if current.name in heading_tags:
            return current.get_text(strip=True)
        # 前の要素を探索
        prev = current.find_previous(heading_tags)
        if prev:
            return prev.get_text(strip=True)
        current = current.parent
    return None

def analyze_links_batch(links_batch):
    """
    リンクのバッチを分析
    """
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
    )

    # フォーマット例
    format_example = '''{
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
}'''

    # リンク情報をJSON形式に変換
    links_json = json.dumps({"links": links_batch}, ensure_ascii=False, indent=2)
    
    print(f"Anthropicに{len(links_batch)}件のリンクを送信中...")
    
    prompt = f"""# あなたは日本語を使うWebアクセシビリティテストのプロです。以下のリンク情報について、WCAG2.4.4で判定を行い、各リンクの目的の明確さを評価するタスクを持っています。

# 達成基準 2.4.4 の判定基準：
リンクの目的が以下のいずれかの方法で理解できること：
1. リンクのテキスト単独で判断可能
2. プログラムによる解釈が可能なリンクのコンテキストから判断可能

# 達成方法のリスト：
- G91: リンクの目的を説明したリンクテキストを提供する
- H30: a要素のリンクの目的を説明するリンクテキストを提供する
- H24: イメージマップのarea要素にテキストによる代替を提供する
- G189: リンクテキストを変更するコントロールを提供する
- SCR30: リンクテキストを変更するためにスクリプトを使用する
- G53: リンクテキストとそれが含まれている文中のテキストとを組み合わせて、リンクの目的を特定する
- H33: title属性を用いて、リンクテキストを補足する
- C7: リンクテキストの一部を非表示にするためにCSSを使用する
- ARIA7: リンクの目的を示すためにaria-labelledbyを使用する
- ARIA8: リンクの目的を示すためにaria-labelを使用する
- H77: リンクテキストとそれが含まれているリスト項目とを組み合わせて、リンクの目的を特定する
- H78: リンクテキストとそれが含まれている段落とを組み合わせて、リンクの目的を特定する
- H79: リンクテキストとそれが含まれているデータセル及び関連づけられた見出しセルとを組み合わせて、リンクの目的を特定する
- H81: 入れ子になったリストの中でリンクの目的を特定する

# 以下のフォーマット例を参考に、各リンクを解析し、その評価結果をJSON形式で出力してください。

フォーマット例###
{format_example}

リンク情報###
{links_json}"""

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        response_text = str(message.content)
        print("\n=== Claudeの分析結果 ===")
        print(response_text)
        print("=====================\n")
        
        # 応答の処理前に少し待機
        time.sleep(1)
        
        # 最初の { から最後の } までを抽出
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            json_str = json_str.replace("'", '"').replace('\\n', '\n').strip()
            
            if DEBUG:
                print("=== 整形後のJSON文字列 ===")
                print(json_str)
                print("=====================")
            
            return json.loads(json_str)
    except Exception as e:
        if DEBUG:
            print(f"Error parsing JSON: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python wcag_link_purpose_checker.py url")
        sys.exit(1)

    url = sys.argv[1]
    
    # URLからファイル名を生成
    filename = url.replace('https://', '').replace('http://', '') \
                 .replace('/', '_').replace(':', '_').replace('?', '_') \
                 .replace('&', '_').replace('=', '_').replace(' ', '_') \
                 .rstrip('_') + '.txt'
    
    try:
        print("ページソースを取得中...")
        page_source = get_page_source(url)
        
        print("リンク情報を抽出中...")
        all_links = extract_link_info(page_source)
        
        print(f"合計 {len(all_links)} 件のリンクを検出")
        
        # リンクを10個ずつのバッチに分割
        batch_size = 10
        link_batches = [all_links[i:i + batch_size] for i in range(0, len(all_links), batch_size)]
        
        print(f"全{len(link_batches)}バッチに分割して処理を開始")
        
        # 各バッチを分析
        all_results = []
        for i, batch in enumerate(link_batches):
            print(f"\nバッチ {i+1}/{len(link_batches)} を処理中...")
            
            result = analyze_links_batch(batch)
            if result and 'links' in result:
                all_results.extend(result['links'])
                print(f"バッチ {i+1} の処理が完了")
                
                # 各リンクの判定結果のサマリーを表示
                print("\n=== このバッチの判定結果サマリー ===")
                for link in result['links']:
                    print(f"・{link['link_text'][:30]}... => {link['analysis']['judgment']}")
                print("=====================\n")
                
                # 次のバッチを処理する前に少し待機
                time.sleep(1)
        
        print("全バッチの処理が完了しました")
        
        # 最終結果の作成
        final_result = {"links": all_results}
        
        # 結果の出力
        print(json.dumps(final_result, ensure_ascii=False, indent=2))

        # 結果をファイルに出力
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果を {filename} に保存しました")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()