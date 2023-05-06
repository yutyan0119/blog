---
layout: post
author: Yuto Nakamura
tags: [ChatGPT, Rust]
description: 
ogp_img: /assets/images/ogp_image/OGP画像をいい感じでつくってくれるアプリをRustで作った With ChatGPT.png
title: OGP画像をいい感じでつくってくれるアプリをRustで作った With ChatGPT
latex: true
date: 2023-05-06 18:00:00 +0900
---

ブログを作ったらそれを共有したくなるもの。RustでOGP画像をパッと生成してくれるアプリを作ったので紹介します。ちなみにほとんどChatGPT(GPT-4)に任せました。凄い。あと最後にはGitHub Actionsで自動的にこれを実行し、ブログに反映します。

## 目標
はてなブログのこんなやつとか
![](https://ogimage.blog.st-hatena.com/13574176438099786264/4207112889917689517/1663223194){: width="50%"}
Zennのこんなやつ
![](https://res.cloudinary.com/zenn/image/upload/s--JbHy5XdW--/c_fit%2Cg_north_west%2Cl_text:notosansjp-medium.otf_55:TangNano9k%25E3%2581%25ABRISC-V%25E3%2582%2592%25E5%25AE%259F%25E8%25A3%2585%25E3%2581%2597%25E3%2581%259F%2Cw_1010%2Cx_90%2Cy_100/g_south_west%2Cl_text:notosansjp-medium.otf_37:yutyan%2Cx_203%2Cy_98/g_south_west%2Ch_90%2Cl_fetch:aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3plbm4tdXNlci11cGxvYWQvYXZhdGFyLzk2NDViZGU1ZmYuanBlZw==%2Cr_max%2Cw_90%2Cx_87%2Cy_72/og-base.png){: width="50%"}
を自分でも作って、自分のブログで使いたいと思った。一つの画像を用意してそれをサイト全体で使い回すのもありっちゃありだが、やはり記事ごとにタイトルを反映して生成したいので、プログラミングで解決することにした。

両者の共通点は
1. 枠がある
2. その中に角丸長方形の白い領域がある
3. その中にタイトル文字が生成される

という点だったので、少なくともこれが出来ることを条件とした。

## 結果
GitHubに実装を公開している。
[https://github.com/yutyan0119/ogp-creater](https://github.com/yutyan0119/ogp-creater)

こんな画像が生成される。
![](/assets/images/ogp_image/RustでSHA3を実装した.png){: width="50%"}

## 実装過程

方針としては**ChatGPT**全振り。何故かというと、Rustで画像を扱ったことがないから。定番のクレートすらしらないので、とりあえずChatGPTに任せてみることに。
とりあえず、こんな感じで要件を伝える
```text
RustでOGP画像を自動生成するようなコードを書きたいです。
画像の仕様についてお伝えします。1200x630 pxの画像です。背景を白にしてください。
右下にicon.pngという画像（1280x1280px）を入れたいです。
中心の630 x 630pxに引数から取った文字を入れたいです。
どのようにしたら実現できますか？
```
すると、`image`と`rusttype`という2つのクレートを使用して、画像を生成するコードを出してきた。（長いので一部省略）

```rust
use image::{DynamicImage, GenericImageView, ImageBuffer, Rgba};
use rusttype::{point, Font, Scale};

fn main() {
    let text = "Hello, world!"; // 引数から取得する文字列
    let icon_path = "icon.png"; // アイコン画像のパス
    create_ogp_image(text, icon_path);
}

fn create_ogp_image(text: &str, icon_path: &str) {
    let (width, height) = (1200, 630);

    // 白い背景の画像を生成
    let mut image = ImageBuffer::from_fn(width, height, |_x, _y| Rgba([255, 255, 255, 255]));

    // アイコン画像を読み込み、右下に配置
    let icon = image::open(icon_path).unwrap().resize(128, 128, image::imageops::FilterType::Lanczos3);
    //...

    // フォントの読み込み
    let font_data = include_bytes!("DejaVuSans.ttf"); // 利用するフォントファイルのパス
    let font = Font::try_from_bytes(font_data as &[u8]).unwrap();

    // 文字列を中心に配置
    let scale = Scale::uniform(50.0);
    let text_width = text.chars().map(|c| font.glyph(c).scaled(scale).h_metrics().advance_width).sum::<f32>();
    //...

    // 文字列の描画
    for (i, c) in text.chars().enumerate() {
       // ...
    }

    // 画像をファイルに保存
    image.save("ogp_image.png").unwrap();
}
```

このコードは`copy_from`がないと怒られるので、それを伝えると`image::imageops::overlay`を使ってねと言ってきた。

```rust
// アイコン画像を読み込み、右下に配置
let icon = image::open(icon_path).unwrap().resize(128, 128, image::imageops::FilterType::Lanczos3);
let icon_width = icon.width();
let icon_height = icon.height();
overlay(&mut image, &icon, width - icon_width, height - icon_height);
```
さらに、Fontに`height`というメソッドはないよといったら、縦方向のサイズを取得するには`font.v_metrics(scale).ascent - font.v_metrics(scale).descent`を使ってねと言ってきた。

```rust
let v_metrics = font.v_metrics(scale);
let text_height = v_metrics.ascent - v_metrics.descent + v_metrics.line_gap;
```

これでひとまずコンパイルは通ったが、文字が正しく描画されない。仕方ないので少し調べたところ、`imageproc::drawing::draw_text_mut`[^1]がうまくいきそうなので、それにコードを変更したところうまくいった。ので、これを伝えておく。

次に、textの左端がx = 285, 右恥が x = 915になるように伝えた。
すると下のようにテキスト幅を計算して、適切なスケールに文字を変換してくれるようになった。凄い。

```rust
let target_width = 630.0;
let default_scale = Scale::uniform(50.0);
let text_width_default_scale: f32 = text
    .chars()
    .map(|c| font.glyph(c).scaled(default_scale).h_metrics().advance_width)
    .sum::<f32>();
let scale_factor = target_width / text_width_default_scale;
let scale = Scale::uniform(50.0 * scale_factor);
let text_width = text.chars().map(|c| font.glyph(c).scaled(scale).h_metrics().advance_width).sum::<f32>();
let v_metrics = font.v_metrics(scale);
let text_height = v_metrics.ascent - v_metrics.descent + v_metrics.line_gap;
let start_x = 285.0;
let start_y = (height as f32 - text_height) / 2.0;
```
次に、フレームの描画をするように言った。
```text
最後に、画像にフレームを付けたいと思います。色は黒で大丈夫です。
左右50px
上100px
下30px
でお願いしたいです

### ここまでだと、ただの線を出力するだけだったので、しっかりと要件を伝えた。

枠は塗りつぶしたいです。また、角をまるくしたいです。おそらくですが、この場合画像生成時に背景を黒くし、その上に1100×500pxの角丸長方形を載せたほうが良いかもしれません。
```

```rust
  // 黒い背景の画像を生成
    let mut image: ImageBuffer<Rgba<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |_x, _y| Rgba([0, 0, 0, 255]));

    // 角丸の白い長方形を描画
    let white = Rgba([255, 255, 255, 255]);
    let rounded_rect = imageproc::rect::Rect::at(50, 100).of_size(1100, 500);
    let corner_radius = 10.0;
    draw_filled_rounded_rect_mut(&mut image, rounded_rect, corner_radius, white);
```
残念ながら、`draw_filled_rounded_rect_mut`なる関数は存在しない…ので伝えると、こんなメソッドを紹介してきた。

```rust
// 角丸の白い長方形を描画
    let white = Rgba([255, 255, 255, 255]);
    let corner_radius = 10;
    let rect = imageproc::rect::Rect::at(50, 100).of_size(1100, 500);

    // 角丸部分を描画
    draw_filled_circle_mut(&mut image, (rect.left() + corner_radius as i32, rect.top() + corner_radius as i32), corner_radius, white);
    draw_filled_circle_mut(&mut image, (rect.right() - corner_radius as i32, rect.top() + corner_radius as i32), corner_radius, white);
    draw_filled_circle_mut(&mut image, (rect.left() + corner_radius as i32, rect.bottom() - corner_radius as i32), corner_radius, white);
    draw_filled_circle_mut(&mut image, (rect.right() - corner_radius as i32, rect.bottom() - corner_radius as i32), corner_radius, white);

    // 長方形部分を描画
    let top_rect = imageproc::rect::Rect::at(rect.left(), rect.top() + corner_radius as i32).of_size(rect.width(), rect.height() - 2 * corner_radius as u32);
    let left_rect = imageproc::rect::Rect::at(rect.left() + corner_radius as i32, rect.top()).of_size(rect.width() - 2 * corner_radius as u32, rect.height());
    draw_filled_rect_mut(&mut image, top_rect, white);
    draw_filled_rect_mut(&mut image, left_rect, white);
```
丸を四隅に書き、それに対応するように長方形を描画している。一見すると長方形を2個生成していたよくわからなかったので、聞いたら、こんなアスキーアートで説明してきた。

```text
top_rect
╭───────────────╮
│               │
╰───────────────╯

left_rect
╭───╮
│   │
│   │
│   │
│   │
│   │
╰───╯
```

なるほど、`top_rect`は縦幅を半径分小さくして、横いっぱいに埋める長方形、`left_rect`は横幅を半径分小さくして、縦いっぱいに埋める長方形ということらしい。あたま良すぎないか？？？？

これで大体完成。あとはブログ名を上の真ん中に入れたり、左下にTwitterのIDを入れたりして、終わり。

タイトルが長いときには、それを分割したいので、それも伝えた。具体的には`scale`が70以下になっちゃうときは、半分に分けて、幅がより長くなる方が横幅630pxになるような`scale`を生成して、それを使うようにした。

```rust
let min_scale = 70.0;
if min_scale < scale.x {
    draw_text_mut(&mut image, Rgba([0, 0, 0, 255]), start_x as i32, start_y as i32, scale, &font, text);
} else {
    let split_index = text.chars().count() / 2;
    let (first_half, second_half) = text.chars().enumerate().fold((String::new(), String::new()), |(mut first, mut second), (i, c)| {
        if i < split_index {
            first.push(c);
        } else {
            second.push(c);
        }
        (first, second)
    });

    let first_half_width_default_scale = first_half.chars().map(|c| font.glyph(c).scaled(default_scale).h_metrics().advance_width).sum::<f32>();
    let second_half_width_default_scale = second_half.chars().map(|c| font.glyph(c).scaled(default_scale).h_metrics().advance_width).sum::<f32>();
    let max_half_width = first_half_width_default_scale.max(second_half_width_default_scale);
    let scale_factor = target_width / max_half_width;
    let new_scale = Scale::uniform(50.0 * scale_factor);

    let first_half_width = first_half.chars().map(|c| font.glyph(c).scaled(new_scale).h_metrics().advance_width).sum::<f32>();
    let second_half_width = second_half.chars().map(|c| font.glyph(c).scaled(new_scale).h_metrics().advance_width).sum::<f32>();
    let start_x_first = 285.0;
    let start_x_second = 285.0;
    let start_y_first = height as f32 / 2.0 - text_height * scale_factor;
    let start_y_second = height as f32 / 2.0;

    draw_text_mut(&mut image, Rgba([0, 0, 0, 255]), start_x_first as i32, start_y_first as i32, new_scale, &font, &first_half);
    draw_text_mut(&mut image, Rgba([0, 0, 0, 255]), start_x_second as i32, start_y_second as i32, new_scale, &font, &second_half);
}
```

ちゃんとこれで2列に別れる。例えば、この記事のOGPなんかがそう。
![](/assets/images/ogp_image/OGP画像をいい感じでつくってくれるアプリをRustで作った.png)

あとはこれのバイナリを生成して、このブログのリポジトリにもコピーしておいたので、投稿前にこれを実行するだけで良い。

## GitHub Actionsで自動化する
まず、markdownから、titleを取得して、それに合わせて`opg-creater`を実行するようなPythonを書く。なぜPythonかというと、GitHub Actionsでシェルスクリプトの次に実行しやすいため。ちなみに、これもChatGPTの手を借りた。正規表現はChatGPTの大の得意分野です。

```python
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
```

あとは、これを実行するようなworkflowを書く。

```yaml
name: OGP Image Generator

on:
  push:
    branches:
      - master
    paths:
      - '_posts/**/*.md'
      - '.github/scripts/ogp_image_gen.py'
      - '.github/workflows/ogp_image_gen.yml'

jobs:
  generate_ogp_image:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8

    - name: Generate OGP Image and Update Markdown
      run: python .github/scripts/ogp_gen.py

    - name: Commit and push changes
      run: |
        git config --local user.email "78634880+yutyan0119@users.noreply.github.com"
        git config --local user.name "yutyan0119"
        git add .
        git diff --quiet && git diff --staged --quiet || git commit -m "Automatically generated OGP images"
        git push
```

リポジトリの設定でActionsに書き込み権限を持たせておくと、Actions内での変更点をコミット/pushしてくれる。

## まとめ
最終的にはやっぱGitHub Actionsで自動化したいよね～と思いながら、GitHub Actionsでバイナリを実行して、それをpushして、markdown冒頭の`ogp_img`という値を書き換えかえた上で、githubに再度pushしないといけないので、一旦後回し。

結果として、少しはてブロに似た形になってしまったので、いつか怒られるかもしれない。怒られたら大人しくレイアウトを変えようと思います。

---
{: data-content="footnotes"}
[^1][Rustで画像に文字を描画する, https://zenn.dev/corocn/articles/69a6735c10ce4f](https://zenn.dev/corocn/articles/69a6735c10ce4f)