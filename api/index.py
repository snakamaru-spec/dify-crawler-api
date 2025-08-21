from http.server import BaseHTTPRequestHandler
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data)
            start_url = body.get('url')

            if not start_url:
                self._send_response({"error": "URL is required"}, status=400)
                return

            if not re.match(r'(?:http|https)://', start_url):
                start_url = 'https://' + start_url

            base_domain = urlparse(start_url).netloc
            to_visit = {start_url}
            visited = set()
            total_images_count = 0
            max_pages = 50

            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue
                try:
                    response = requests.get(current_url, timeout=10, headers={'User-Agent': 'Dify-Crawler/1.0'})
                    if response.status_code == 200:
                        visited.add(current_url)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        total_images_count += len(soup.find_all('img'))
                        for link in soup.find_all('a', href=True):
                            absolute_url = urljoin(current_url, link['href'])
                            parsed_url = urlparse(absolute_url)
                            if (parsed_url.netloc == base_domain and 
                                parsed_url.scheme in ['http', 'https'] and 
                                absolute_url not in visited):
                                to_visit.add(absolute_url)
                except requests.RequestException:
                    continue
            
            result = {
                "page_count": len(visited),
                "image_count": total_images_count
            }
            self._send_response(result)

        except Exception as e:
            self._send_response({"error": str(e)}, status=500)

    def _send_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))