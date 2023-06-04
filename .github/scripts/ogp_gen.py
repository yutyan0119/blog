import os
import re
import subprocess
from pathlib import Path

POSTS_PATH = "_posts"
OGP_IMAGES_PATH = "assets/images/ogp_image"
MD_PATTERN = r"^---\n(?:.*\n)*?title:\s*(.*?)\n(?:.*\n)*?---"

def generate_ogp_image(title):
    sanitized_title = title.replace(" ", "-")
    # OGP画像を生成するコマンドを実行
    ogp_creater_path = os.path.abspath("./ogp-creater")
    subprocess.run([ogp_creater_path, title], cwd=OGP_IMAGES_PATH)

    # 生成されたOGP画像のパスを返す
    return f"{OGP_IMAGES_PATH}/{sanitized_title}.png"

def update_md_file(file_path, ogp_image_path):
    with open(file_path, "r") as md_file:
        content = md_file.read()

    # 既存のOGP画像パスを検索
    updated_content = re.sub(
        r"(^---\n(?:.*\n)*?)ogp_img:.*(\n(?:.*\n)*?---)",
        rf"\1ogp_img: {ogp_image_path}\2",
        content,
        flags=re.MULTILINE
    )

    if content != updated_content:
        with open(file_path, "w") as file:
            file.write(updated_content)

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
