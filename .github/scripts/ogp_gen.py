import os
import re
import subprocess
from pathlib import Path

POSTS_PATH = "_posts"
OGP_IMAGES_PATH = "assets/images/ogp_image"
MD_PATTERN = r"^---\n(?:.*\n)*?title:\s*(.*?)\n(?:.*\n)*?---"

def generate_ogp_image(title):
    # OGP画像を生成するコマンドを実行
    ogp_creater_path = os.path.abspath(OGP_IMAGES_PATH + "/ogp-creater")
    subprocess.run([ogp_creater_path, title], cwd=OGP_IMAGES_PATH)

    # 生成されたOGP画像のパスを返す
    return f"{OGP_IMAGES_PATH}/{title}.png"

def update_md_file(file_path, ogp_image_path):
    with open(file_path, "r") as md_file:
        content = md_file.read()

    # 既存のOGP画像パスを検索
    ogp_img_pattern = r"ogp_img:(.*)"
    existing_ogp_img = re.search(ogp_img_pattern, content)

    # 既存のOGP画像パスがあれば更新、なければ追加
    if existing_ogp_img:
        content = re.sub(ogp_img_pattern, f"ogp_img: {ogp_image_path}", content)
    else:
        content = content.replace("---", f"---\nogp_img: {ogp_image_path}", 1)

    with open(file_path, "w") as md_file:
        md_file.write(content)

def main():
    md_files = list(Path(POSTS_PATH).rglob("*.md"))
    
    for md_file in md_files:
        with open(md_file, "r") as file:
            content = file.read()

        title_match = re.search(MD_PATTERN, content)
        if title_match:
            title = title_match.group(1)
            # OGP画像を生成
            print(title)
            ogp_image_path = generate_ogp_image(title)
            ogp_image_path = "/" + ogp_image_path
            print(ogp_image_path)
            # # 記事のMarkdownファイルを更新
            update_md_file(md_file, ogp_image_path)

if __name__ == "__main__":
    main()
