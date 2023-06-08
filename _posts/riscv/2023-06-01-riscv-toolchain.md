---
layout: post
author: Yuto Nakamura
tags: [サイボウズ・ラボユース, 自作OS, RISC-V]
description: 
ogp_img: /assets/images/ogp_image/riscv-gnu-toolchainをビルドした.png
title: riscv-gnu-toolchainをビルドした
latex: false
date: 2023-05-31 23:55:00 +0900
---

[前回の記事](https://yutyan.dev/cybozu-labyouth)でお話したように、RISC-Vで動作する自作OSを作成することになりました。そのためには、RISC-Vのクロスコンパイラが必要になります。今回は、RISC-Vのクロスコンパイラであるriscv-gnu-toolchainをビルドします。

## なぜriscv-gnu-toolchainをビルドするのか
CPUにはアーキテクチャというものがあり、例えばx86-64だとか、Armだとか、今回のようなRISC-Vなどがあります。それぞれは、異なる命令セットを持っているため、たとえ、同じC言語のコードであったとしても、コンパイルした後の機械語は全く異なるものになります。今回の自作OSはRISC-V上で動かすため、RISC-Vに対応するコンパイラが必要です。それが、riscv-gnu-toolchainです。

## Buildしていく
公式リポジトリは[https://github.com/riscv-collab/riscv-gnu-toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)です。このREADMEを見ておけば、特に難しいことはありません。

```bash
# buildに必要な依存関係をインストールします
sudo apt-get install autoconf automake autotools-dev curl \
    python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential \
    bison flex texinfo gperf libtool patchutils bc zlib1g-dev \
    libexpat-dev ninja-build
# cloneします（時間がかかります。最新のものを使用するだけなら、--depth 1ですぐにcloneできます）
git clone --recursive https://github.com/riscv-collab/riscv-gnu-toolchain
# 移動します
cd riscv-gnu-toolchain
# build directoryを作成します
mkdir build
# build directoryに移動します
cd build
# configureします
../configure --prefix=/path/to/riscv --with-arch=rv32ima --with-abi=ilp32
# buildします
make -j $(nproc)
# installします
make install
```

これで、`~/opt/riscv/bin`に、RISC-Vのクロスコンパイラがインストールされました。

<aside class="msg message">
<span class="msg-symbol">🙄</span>
<div class="msg-content">
configureし、makeするというのは、大規模なソフトウェアあるあるなビルド手順です。
</div>
</aside>


`configure`ではいくつかのオプションを設定することで、本当にビルドしたいものを定めます。ここでは、`--prefix=/path/to/riscv`で、ビルドされたバイナリをインストールする場所を指定し、`--with-arch=rv32ima`で使用する命令セットを指定しました。`--with-abi=ilp32`は、ABIを指定しています。どんなデータ型が使用可能化をこれで指定しています。

詳しくは[SiFiveのブログ](https://www.sifive.com/blog/all-aboard-part-1-compiler-args)を見るのが良いと思います。

[https://www.sifive.com/blog/all-aboard-part-1-compiler-args](https://www.sifive.com/blog/all-aboard-part-1-compiler-args)

最後に、PATHを通しておきます。

```bash
# ~/.bashrcに以下を追記します
export PATH=$PATH:/path/to/riscv/bin
```

これで、`riscv32-unknown-elf-gcc`などが使えるようになり、一旦準備は完了です。

---
{: data-content="footnotes"}
