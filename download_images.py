import os
import re
import time
import requests

def download_images():
    products_file = r'C:\Users\Darrell\Downloads\archford_products_full.py'
    target_dir = 'static/images/items/'
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"Reading products file: {products_file}")
    with open(products_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to find all matching image URLs
    # Pattern: https://archford.com/Content/images/items/*.jpg
    url_pattern = r'https://archford\.com/Content/images/items/[^/"]+\.jpg'
    urls = re.findall(url_pattern, content)
    
    # Use a set to get unique URLs
    unique_urls = list(dict.fromkeys(urls))
    total_urls = len(unique_urls)
    print(f"Found {len(urls)} URLs, {total_urls} unique.")
    
    downloaded_count = 0
    skipped_count = 0
    
    for i, url in enumerate(unique_urls):
        # Extract item ID from URL (e.g., A01-003 from .../A01-003.jpg)
        filename = url.split('/')[-1]
        item_id = filename.replace('.jpg', '')
        local_path = os.path.join(target_dir, filename)
        
        if os.path.exists(local_path):
            skipped_count += 1
        else:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    downloaded_count += 1
                else:
                    print(f"\nFailed to download {url}: Status {response.status_code}")
            except Exception as e:
                print(f"\nError downloading {url}: {e}")
            
            # Respectful delay
            time.sleep(0.2)
            
        # Print progress every 50 images
        processed = i + 1
        if processed % 50 == 0 or processed == total_urls:
            print(f"Progress: {processed}/{total_urls} (Downloaded: {downloaded_count}, Skipped: {skipped_count})")

    print(f"\nFinished! Total: {total_urls}, Downloaded: {downloaded_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    download_images()
