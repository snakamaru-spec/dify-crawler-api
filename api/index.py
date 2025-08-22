import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        API_KEY = os.getenv('SCRAPINGBEE_API_KEY')
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            target_url = body.get('url')

            if not target_url:
                self._send_response({"error": "URL is required"}, status=400)
                return
            
            if not API_KEY:
                self._send_response({"error": "ScrapingBee API key is not configured"}, status=500)
                return

            # --- ScrapingBee APIを呼び出す部分 ---
            response = requests.get(
                url='https://app.scrapingbee.com/api/v1/',
                params={
                    'api_key': API_KEY,
                    'url': target_url, 
                    'render_js': 'true', # JavaScriptを有効にする
                    # '#footer'を待つ設定を削除
                },
                timeout=120
            )

            if response.status_code >= 400:
                self._send_response({
                    "error": "Failed to fetch content from ScrapingBee",
                    "status_code": response.status_code,
                    "details": response.text
                }, status=500)
                return
            
            # --- 取得したHTMLを分析する部分 ---
            soup = BeautifulSoup(response.content, 'html.parser')
            
            image_count = len(soup.find_all('img'))
            
            urls = set()
            base_domain = urlparse(target_url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(target_url, href)
                parsed_url = urlparse(absolute_url)
                if parsed_url.netloc == base_domain:
                    clean_url = absolute_url.split('#')[0].split('?')[0]
                    urls.add(clean_url)
            
            urls.add(target_url.split('#')[0].split('?')[0])
            page_count = len(urls)

            result = {
                "page_count": page_count,
                "image_count": image_count,
                "pages_found": list(urls)
            }
            self._send_response(result)

        except Exception as e:
            self._send_response({"error": str(e)}, status=500)

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))