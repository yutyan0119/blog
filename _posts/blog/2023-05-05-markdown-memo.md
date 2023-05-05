---
layout: post
author: Yuto Nakamura
tags: [overview, メモ]
description: 
ogp_img: /assets/images/favicon/mylogo.png
---

ここに説明書きを書くことが出来る。上のdescriptionを書いていないときは、こちらの文章がOGPに表示される。脚注を書くことが出来る。[^1]
これは特定の場所[math](#math)へのリンクである。

# Sample heading 1
## Sample heading 2
### Sample heading 3
#### Sample heading 4
##### Sample heading 5
###### Sample heading 6

## List

Unordered:

- hoge
- fuga

Ordered:

1. yes
1. no
1. yes

## 引用

こんな感じで引用を書くことが出来る

> 春はあけぼの。やうやう白くなりゆく山ぎは、すこしあかりて、紫だちたる 雲のほそくたなびきたる。

## Thematic breaks (<hr>)

こんな感じで区切り線を入れることが出来る

---

これが区切り線


## Tables

表を表示することも出来る

|title| date| category|
|:---|:---:|---:|
|title1| 2020/01/01| category1|
|title2| 2020/01/02| category2|
|title3| 2020/01/03| category3|

## Code highlighting

```rust
fn main() {
    println!("Hello, world!");
}
```

インラインのコードも表示できる `println!("Hello, world!");`。

## math

$$ \sum_{i=1}^n a_i=0 $$

## 画像表示
![hoge](/assets/images/favicon/mylogo.png){: align="center" width="150px" height="150px"}

---
{: data-content="footnotes"}

[^1]: これが脚注
