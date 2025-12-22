import requests
import os
from tqdm import tqdm
import zipfile

BASE_URL = "https://zenodo.org/record/4010759/files/"
DOWNLOAD_DIR = "ml/dataset/isl_words_raw"
EXTRACT_DIR = "ml/dataset/isl_words"

RECOMMENDED_DOWNLOADS = {
    "Pronouns": ["Pronouns_1of2.zip", "Pronouns_2of2.zip"],
    "Days_and_Time": ["Days_and_Time_1of3.zip", "Days_and_Time_2of3.zip", "Days_and_Time_3of3.zip"],
    "Colours": ["Colours_1of2.zip", "Colours_2of2.zip"],
    "Electronics": ["Electronics_1of2.zip", "Electronics_2of2.zip"],
    "Seasons": ["Seasons_1of1.zip"]
}

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as f, tqdm(
        desc=os.path.basename(dest_path),
        total=total_size,
        unit='B',
        unit_scale=True
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))

def extract_zip(zip_path, extract_to):
    print(f"Extracting {os.path.basename(zip_path)}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extracted successfully")

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    print("="*60)
    print("ISL Dataset Downloader")
    print("="*60)
    
    print("\nCategories to download:")
    total_files = 0
    for category, files in RECOMMENDED_DOWNLOADS.items():
        print(f"  - {category}: {len(files)} file(s)")
        total_files += len(files)
    
    print(f"\nTotal files: {total_files}")
    
    choice = input("\nProceed with download? (y/n): ")
    if choice.lower() != 'y':
        print("Download cancelled")
        return
    
    for category, files in RECOMMENDED_DOWNLOADS.items():
        print(f"\n{'='*60}")
        print(f"Downloading {category}")
        print(f"{'='*60}")
        
        for filename in files:
            url = BASE_URL + filename
            dest_path = os.path.join(DOWNLOAD_DIR, filename)
            
            if os.path.exists(dest_path):
                print(f"Already downloaded: {filename}")
            else:
                try:
                    download_file(url, dest_path)
                except Exception as e:
                    print(f"Error downloading {filename}: {e}")
                    continue
            
            try:
                extract_zip(dest_path, EXTRACT_DIR)
            except Exception as e:
                print(f"Error extracting {filename}: {e}")
    
    print("\n" + "="*60)
    print("Download complete!")
    print(f"Videos extracted to: {EXTRACT_DIR}")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Organize videos by word folders")
    print("2. Run: python ml/process_word_videos.py")
    print("3. Run: python ml/train_word_model_enhanced.py")

if __name__ == "__main__":
    main()
