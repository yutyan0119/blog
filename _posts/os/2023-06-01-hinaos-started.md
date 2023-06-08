---
layout: post
author: Yuto Nakamura
tags: [自作OS, RISC-V]
description: 
ogp_img: /assets/images/ogp_image/QEMUをビルドしてHinaOSを動かした.png
title: QEMUをビルドしてHinaOSを動かした
latex: false
date: 2023-06-01 22:35:00 +0900
---

今回は、QEMUをビルドして、他の人の自作OSを実行してみようというものです。少しだけ躓くポイントがあるので、解消ポイントも書いておきます。RISC-V対応OSを自作しようと思っていたら、どストライクな本が発売されていました。[『自作OSで学ぶマイクロカーネルの設計と実装』(秀和システム、ISBN: 978-4-7980-6871-8)](https://www.hanmoto.com/bd/isbn/9784798068718)で紹介されている[HinaOS](https://github.com/nuta/microkernel-book)は、教育向けマイクロカーネルOSです。RISC-Vに対応しており、マルチコア対応やファイルシステムの実装などが特徴です。自分のRISC-V対応OSにもかなり参考になるものと思っています。参考にするにはまず動かしてどんなことが出来るのか見てみようということで、実際に動かしてみます。実際の本は以下の画像のリンク先から購入できます。とても良い本なので是非。

<a href="https://www.amazon.co.jp/%E8%87%AA%E4%BD%9COS%E3%81%A7%E5%AD%A6%E3%81%B6%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB%E3%81%AE%E8%A8%AD%E8%A8%88%E3%81%A8%E5%AE%9F%E8%A3%85-%E6%80%92%E7%94%B0%E6%99%9F%E4%B9%9F/dp/4798068713?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=2HONPIDEFVA5M&keywords=%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB&qid=1685622228&sprefix=%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB%2Caps%2C175&sr=8-4&linkCode=li2&tag=yutyan0119-22&linkId=afcffafb202ab4c3198b8456c0ef448a&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="https://gist.githubusercontent.com/nuta/e45864405fbdc8618af4b08de534e42c/raw/bd3df82e7039902818c8fc0d394b69250cc78fc9/cover.jpg" width="200" ></a>

[https://github.com/nuta/microkernel-book](https://github.com/nuta/microkernel-book)

ただ動かすだけでは面白みが無いと思うので、QEMUの勉強を兼ねて、QEMUのビルドからやっていこうと思います。QEMUは、仮想マシンをエミュレートするソフトウェアです。今回は、RISC-Vの仮想マシンをエミュレートするために使用します。

<aside class="msg message">
<span class="msg-symbol">🥰</span>
<div class="msg-content">
QEMUをビルドするのは、自分もOSを作ったらQEMU上で動くことを考慮して少しでも使い方を知っておこうという点からです。
</div>
</aside>

## QEMUのビルド（これだとOSの起動に失敗します）
せっかくなので、最新の安定版である、8.0.0をビルドします。まず、ソースコードをダウンロードしてきます。

```bash
wget https://download.qemu.org/qemu-8.0.0.tar.xz
tar xvJf qemu-8.0.0.tar.xz
cd qemu-8.0.0
```

次にいつも通り`configure`したいのですが、オプションがよくわからないので、`configure --help`を見てみます。

```bash
./configure --help
```

すると以下のように丁寧なオプションの説明が出てきます（後半は省略）。今回はprefixとtarget-listでriscv32-softmmuを設定するだけで良さそうです。

```bash
Usage: configure [options]
Options: [defaults in brackets after descriptions]

Standard options:
  --help                   print this message
  --prefix=PREFIX          install in PREFIX [/usr/local]
  --target-list=LIST       set target list (default: build all)
                           Available targets: aarch64-softmmu alpha-softmmu
                           arm-softmmu avr-softmmu cris-softmmu hppa-softmmu
                           i386-softmmu loongarch64-softmmu m68k-softmmu
                           microblaze-softmmu microblazeel-softmmu mips-softmmu
                           mips64-softmmu mips64el-softmmu mipsel-softmmu
                           nios2-softmmu or1k-softmmu ppc-softmmu ppc64-softmmu
                           riscv32-softmmu riscv64-softmmu rx-softmmu
                           s390x-softmmu sh4-softmmu sh4eb-softmmu
                           sparc-softmmu sparc64-softmmu tricore-softmmu
                           x86_64-softmmu xtensa-softmmu xtensaeb-softmmu
                           aarch64-linux-user aarch64_be-linux-user
                           alpha-linux-user arm-linux-user armeb-linux-user
                           cris-linux-user hexagon-linux-user hppa-linux-user
                           i386-linux-user loongarch64-linux-user
                           m68k-linux-user microblaze-linux-user
                           microblazeel-linux-user mips-linux-user
                           mips64-linux-user mips64el-linux-user
                           mipsel-linux-user mipsn32-linux-user
                           mipsn32el-linux-user nios2-linux-user
                           or1k-linux-user ppc-linux-user ppc64-linux-user
                           ppc64le-linux-user riscv32-linux-user
                           riscv64-linux-user s390x-linux-user sh4-linux-user
                           sh4eb-linux-user sparc-linux-user
                           sparc32plus-linux-user sparc64-linux-user
                           x86_64-linux-user xtensa-linux-user
                           xtensaeb-linux-user
  --target-list-exclude=LIST exclude a set of targets from the default target-list

Advanced options (experts only):
  --cross-prefix=PREFIX    use PREFIX for compile tools, PREFIX can be blank []
  --cc=CC                  use C compiler CC [cc]
  --host-cc=CC             use C compiler CC [cc] for code run at
...
```

```bash
./configure --prefix=/path/to/qemu --target-list=riscv32-softmmu
make -j$(nproc)
make install
```

これで、QEMUのビルドは完了です。`/path/to/qemu/bin`に`qemu-system-riscv32`が生成されているはずです。
最後に、`~/.bashrc`に以下のようにパスを通しておきます。

```bash
export PATH=$PATH:/path/to/qemu/bin
```

## HinaOSの環境構築（QEMU以外）
QEMU以外に関しては、[README](https://github.com/nuta/microkernel-book/blob/main/README.md)に従っておきましょう。ただし、Pythonの環境を破壊しないように、ここではvenvを使用します。

```bash
sudo apt update
sudo apt install llvm clang lld python3-pip python3-venv gdb-multiarch git
git clone https://github.com/nuta/microkernel-book.git
cd microkernel-book
# 仮想環境を作成
python3 -m venv .env
# 仮想環境を有効化
source .env/bin/activate
# 仮想環境に必要なパッケージをインストール
pip install -r requirements.txt
# HinaOSのビルド
make -j$(nproc)
```

驚くことに、一瞬でビルドが終わります。実行してみると、以下のようなエラーが出ます。

```bash
qemu-system-riscv32: -netdev user,id=net0: network backend 'user' is not compiled into this binary
make: *** [Makefile:176: run] Error 1
```

## QEMUの再ビルド

なんか、network backend 'user'がないとか言われています。よくわからないので、調べてみるとstack overflowに[解決策](https://stackoverflow.com/questions/75641274/network-backend-user-is-not-compiled-into-this-binary)がありました。どうやら、QEMUをビルドするときに`--enable-slirp`をつける必要があるようです。というわけで、QEMUを再ビルドします。

```bash
./configure --prefix=/path/to/qemu --target-list=riscv32-softmmu --enable-slirp
```

また、エラーが出ます。

```bash
E: Unable to locate package libslirp
```

libslirpがないみたいなので、入れてあげましょう。ubuntuでは、libslirp-devというパッケージになっているようです。

```bash
sudo apt install libslirp-dev
```

<aside class="msg message">
<span class="msg-symbol">🧐</span>
<div class="msg-content">
<a href="https://gitlab.freedesktop.org/slirp/libslirp">libslirp</a>は仮想マシン上でTCP-IPのエミュレートを行うライブラリみたいです。
</div>
</aside>

もう一回、QEMUをビルドします。

```bash
./configure --prefix=/path/to/qemu --target-list=riscv32-softmmu --enable-slirp
make -j$(nproc)
make install
```

これで、HinaOSも動くようになるはずです。

## HinaOSを動かしてみる

```bash
make run
```

いい感じですね。`cat`や`ls`も動くみたいです。

```text
    UPDATE  build/consts.mk
       GEN  build/compile_commands.json

Kernel Executable: build/hinaos.elf (3733 KiB)
BootFS Image:      build/bootfs.bin (3016 KiB)
HinaFS Image:      build/hinafs.img (131072 KiB)
      QEMU  build/hinaos.elf
Booting HinaOS...
[kernel] free memory: 803bd000 - 88000000 (124MiB)
[kernel] MMIO memory: 10001000 - 10002000 (4KiB)
[kernel] MMIO memory: 10002000 - 10003000 (4KiB)
[kernel] created a task "vm" (tid=1)
[kernel] bootelf: 32000000 - 3200c8ac r-x (50 KiB)
[kernel] bootelf: 3200d000 - 3234148a r-- (3281 KiB)
[kernel] bootelf: 32342000 - 32789118 rw- (4380 KiB)
[kernel] CPU #0 is ready
[vm] bootfs: found following 9 files
...
[fs] successfully loaded the file system
[vm] service "fs" is up
[fs] ready

Welcome to HinaOS!

shell> ls
[shell] Contents of /:
[fs] block 7 is not in cache, reading from disk
[shell] [FILE] "hello.txt"
shell> c
shell> cat hello.txt
[fs] block 6 is not in cache, reading from disk
[shell] Hello World from HinaFS!
```

## QEMUでregisterの状態を見てみる。
`Ctrl-A + C`でQEMUのモニタに入ります。こんな感じで、レジスタの状態を見ることができます。

```bash
(qemu) info registers
CPU#0
 V      =   0
 pc       800098b2
 mhartid  00000000
 ...
 x0/zero  00000000 x1/ra    800098a2 x2/sp    803b0e70 x3/gp    00000000
 x4/tp    803ac3d0 x5/t0    803a0e00 x6/t1    803a0d60 x7/t2    00000000
 x8/s0    803b0e80 x9/s1    803ac3f8 x10/a0   00040022 x11/a1   0000c0be
 x12/a2   000012ab x13/a3   000012ab x14/a4   00000000 x15/a5   803a0da0
 x16/a6   803a0e20 x17/a7   803a0de0 x18/s2   80011404 x19/s3   803a4560
 x20/s4   80054094 x21/s5   00448000 x22/s6   00000006 x23/s7   80054088
 x24/s8   00000016 x25/s9   80054034 x26/s10  00000006 x27/s11  807ae000
 x28/t3   00000000 x29/t4   00000000 x30/t5   00000000 x31/t6   00000000
 f0/ft0   0000000000000000 f1/ft1   0000000000000000 f2/ft2   0000000000000000 f3/ft3   0000000000000000
 f4/ft4   0000000000000000 f5/ft5   0000000000000000 f6/ft6   0000000000000000 f7/ft7   0000000000000000
 f8/fs0   0000000000000000 f9/fs1   0000000000000000 f10/fa0  0000000000000000 f11/fa1  0000000000000000
 f12/fa2  0000000000000000 f13/fa3  0000000000000000 f14/fa4  0000000000000000 f15/fa5  0000000000000000
 f16/fa6  0000000000000000 f17/fa7  0000000000000000 f18/fs2  0000000000000000 f19/fs3  0000000000000000
 f20/fs4  0000000000000000 f21/fs5  0000000000000000 f22/fs6  0000000000000000 f23/fs7  0000000000000000
 f24/fs8  0000000000000000 f25/fs9  0000000000000000 f26/fs10 0000000000000000 f27/fs11 0000000000000000
 f28/ft8  0000000000000000 f29/ft9  0000000000000000 f30/ft10 0000000000000000 f31/ft11 0000000000000000
 ```

他にも、色々なコマンドが使えます。詳しくは[こちら](https://www.qemu.org/docs/master/system/monitor.html)を参照してください。
抜け出すときは`Ctrl-A + X`です。

## まとめ
QEMUをビルドして、RISC-V対応のHinaOSを動かすことが出来ました。OSの勉強を進めつつ、自分のOSの要件定義や、設計を進めていきたいと思います。



<iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=yutyan0119-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=4798068713&linkId=08da4deb959756c25c458b74a811b511"></iframe>

---
{: data-content="footnotes"}
