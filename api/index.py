from http.server import BaseHTTPRequestHandler
import json
from bs4 import BeautifulSoup

class handler(Base-HTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            # WaterCrawlからの出力を 'content' というキーで受け取る
            crawl_data = body.get('content', "")

            if not crawl_data:
                self._send_response({"error": "Content is required"}, status=400)
                return

            # BeautifulSoupを使ってHTMLとして解析
            soup = BeautifulSoup(crawl_data, 'html.parser')
            
            # 画像タグの総数を数える
            image_count = len(soup.find_all('img'))
            
            # WaterCrawlの出力からユニークなURLを探してページ数を数える
            urls = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href and href.startswith('http'):
                    urls.add(href.split('#')[0].split('?')[0])

            # ページ数はURLの数とする（ドキュメント自体も1とカウント）
            page_count = len(urls) if len(urls) > 0 else 1

            result = {
                "page_count": page_count,
                "image_count": image_count
            }
            self._send_response(result)

        except Exception as e:
            self._send_response({"error": str(e)}, status=500)

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))