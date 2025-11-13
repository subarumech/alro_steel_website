import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

def sanitize_filename(url):
    """Create a safe filename from URL"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename or '.' not in filename:
        filename = 'image_' + re.sub(r'[^\w\-_]', '_', parsed.path) + '.jpg'
    return filename

def extract_images(url, output_dir='images'):
    """Extract all images from a webpage"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        downloaded = []
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue
            
            img_url = urljoin(url, src)
            
            try:
                img_response = requests.get(img_url, headers=headers, timeout=10, stream=True)
                img_response.raise_for_status()
                
                filename = sanitize_filename(img_url)
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded.append((img_url, filename))
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
        
        print(f"\nTotal images downloaded: {len(downloaded)}")
        return downloaded
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == '__main__':
    url = 'https://www.alro.com/'
    print(f"Extracting images from {url}...")
    extract_images(url)

