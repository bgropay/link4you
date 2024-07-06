import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import tldextract

session = requests.Session()

def collect_links_from_file(urls_file, download_dir):
    with open(urls_file, 'r') as file:
        urls = file.readlines()
        for url in urls:
            url = url.strip()
            try:
                collect_links(url, download_dir)
            except Exception as e:
                print(f"Error processing {url}: {e}")

def collect_links(album_url, download_dir):
    parsed_url = urlparse(album_url)
    if parsed_url.hostname != "www.erome.com":
        raise Exception(f"Host must be www.erome.com")

    r = session.get(album_url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        raise Exception(f"HTTP error {r.status_code}")

    soup = BeautifulSoup(r.content, "html.parser")
    videos = [video_source["src"] for video_source in soup.find_all("source")]
    urls = list(set(videos))  # Only collect video URLs
    existing_files = get_files_in_dir(download_dir)
    for file_url in urls:
        download(file_url, download_dir, album_url, existing_files)

def get_files_in_dir(directory):
    return [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]

def download(url, download_path, album=None, existing_files=[]):
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    if file_name in existing_files:
        print(f'[#] Skipping "{url}" [already downloaded]')
        return
    print(f'[+] Downloading "{url}"')
    extracted = tldextract.extract(url)
    hostname = "{}.{}".format(extracted.domain, extracted.suffix)
    with session.get(
        url,
        headers={
            "Referer": f"https://{hostname}" if album is None else album,
            "Origin": f"https://{hostname}",
            "User-Agent": "Mozilla/5.0",
        },
        stream=True,
    ) as r:
        if r.ok:
            with open(os.path.join(download_path, file_name), "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
        else:
            print(f'[ERROR] Download of  "{url}" failed')

if __name__ == "__main__":
    print("Menu:")
    print("1. Download a single URL")
    print("2. Download from a file containing multiple URLs")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == '1':
        url = input("Enter the URL to download: ").strip()
        download_dir = input("Enter the directory to save downloads: ").strip()
        folder_name = input("Enter the folder name to save downloads: ").strip()
        download_path = os.path.join(download_dir, folder_name)
        if not os.path.isdir(download_path):
            os.makedirs(download_path)
        try:
            collect_links(url, download_path)
        except Exception as e:
            print(f"Error processing {url}: {e}")
    elif choice == '2':
        urls_file = input("Enter the path to the file containing URLs: ").strip()
        download_dir = input("Enter the directory to save downloads: ").strip()
        folder_name = input("Enter the folder name to save downloads: ").strip()
        download_path = os.path.join(download_dir, folder_name)
        if not os.path.isdir(download_path):
            os.makedirs(download_path)
        try:
            collect_links_from_file(urls_file, download_path)
        except Exception as e:
            print(f"Error processing {urls_file}: {e}")
    else:
        print("Invalid choice. Please enter '1' or '2'.")
