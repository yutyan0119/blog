---
layout: post
author: Yuto Nakamura
tags: [自作OS, RISC-V]
description: 
ogp_img: /assets/images/ogp_image/QEMUの起動オプションを調べてみる.png
title: QEMUの起動オプションを調べてみる
latex: false
date: 2023-06-02 20:30:00 +0900
---

[前回の記事](https://yutyan.dev/hinaos-started)では、HinaOSをQEMUで実際に動かしてみました。

今回は、HinaOSのMakefileがQEMUをどのように実行しているのかを調べて、実際にプログラムを実行する際の目安とします。

[HinaOS](https://github.com/nuta/microkernel-book)は、[『自作OSで学ぶマイクロカーネルの設計と実装』(秀和システム、ISBN: 978-4-7980-6871-8)](https://www.hanmoto.com/bd/isbn/9784798068718)で紹介されている教育向けマイクロカーネルOSです。実際の本は以下の画像のリンク先から購入できます。とても良い本なので是非。

<a href="https://www.amazon.co.jp/%E8%87%AA%E4%BD%9COS%E3%81%A7%E5%AD%A6%E3%81%B6%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB%E3%81%AE%E8%A8%AD%E8%A8%88%E3%81%A8%E5%AE%9F%E8%A3%85-%E6%80%92%E7%94%B0%E6%99%9F%E4%B9%9F/dp/4798068713?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=2HONPIDEFVA5M&keywords=%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB&qid=1685622228&sprefix=%E3%83%9E%E3%82%A4%E3%82%AF%E3%83%AD%E3%82%AB%E3%83%BC%E3%83%8D%E3%83%AB%2Caps%2C175&sr=8-4&linkCode=li2&tag=yutyan0119-22&linkId=afcffafb202ab4c3198b8456c0ef448a&language=ja_JP&ref_=as_li_ss_il" target="_blank"><img border="0" src="https://gist.githubusercontent.com/nuta/e45864405fbdc8618af4b08de534e42c/raw/bd3df82e7039902818c8fc0d394b69250cc78fc9/cover.jpg" width="200" ></a><img src="https://ir-jp.amazon-adsystem.com/e/ir?t=yutyan0119-22&language=ja_JP&l=li2&o=9&a=4798068713" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />

## 実行時のコマンドを確認する
`-n`オプションをつけて、`make`すると、実行せずに実行時のコマンドを確認できます。

```bash
make -n run
```

すると大量のコマンドが表示されます。例えば最初はbuildディレクトリを作り、その後、`main.c`, `prntk.c`, ...とたくさんのファイルをコンパイルし、最後に、リンクして`elf`を生成していることがわかります。生成したのちに、最後の最後に実行されるQEMUコマンドは以下です。(実際にはない改行を付け足しています)

```bash
qemu-system-riscv32 -smp 1 -nographic -serial mon:stdio \
 --no-reboot -m 128 -machine virt,aclint=on \
 -bios none -global virtio-mmio.force-legacy=true \
 -drive file=build/hinafs.img,if=none,format=raw,id=drive0 \
 -device virtio-blk-device,drive=drive0,bus=virtio-mmio-bus.0 \
 -device virtio-net-device,netdev=net0,bus=virtio-mmio-bus.1 \
 -object filter-dump,id=fiter0,netdev=net0,file=virtio-net.pcap \
 -netdev user,id=net0 -kernel build/hinaos.elf
```

各オプションについて見ていきます

- `-smp 1` : CPUの数を指定します。今回は1つです。
- `-nographic` : グラフィックを表示しません。
- `-serial mon:stdio` : シリアルポートを標準入出力に接続します。monはmonitorの略です。
- `--no-reboot` : シャットダウン時に再起動しないようにします。
- `-m 128` : メモリサイズを128MBにします。
- `machine virt,aclint=on` : マシンタイプを`virt`にします。`aclint=on`はACLINTを有効にするオプションです。ACLINTについてはよくわかっていませんが、おそらく、複数のスレッドがあるときの割り込みの扱いをどうするかを指定しているのだと思います。詳しくは[ここ](https://github.com/riscv/riscv-aclint/blob/main/riscv-aclint.adoc)を見てください。
  - `virt`は、仮想のプラットフォームです。特定のハードウェアを再現する必要性がない場合に使用されます。RISC-VのQEMUでは、現在のところ、opentitan, sifive_e, sifive_u, spike, virtのマシンタイプが存在するようです。
- `-bios none` : BIOSは今回指定しません
- `-global virtio-mmio.force-legacy=true` : 仮想デバイスの設定です。`virtio-mmio`は仮想デバイスの一種です。`force-legacy=true`は、仮想デバイスのレガシーモードを強制的に有効にするオプションです。正直あんまりよくわかっていない…
- `-drive file=build/hinafs.img,if=none,format=raw, id=drive0` : ディスクイメージを指定します。`if=none`は、ディスクイメージを仮想デバイスに接続しないことを意味します。`format=raw`は、ディスクイメージのフォーマットをrawに指定します。rawは、これで、直接イメージが書き込まれます。また、このドライブの名前を`drive0`とします。
- `-device virtio-blk-device,drive=drive0,bus=virtio-mmio-bus.0` : `virtio-blk-device`は、仮想デバイスの一種で、ストレージデバイスを仮想化しています。`drive=drive0`は、先ほど指定したディスクイメージを接続します。`bus=virtio-mmio-bus.0`は、仮想デバイスを接続するバスを指定します。
- `-device virtio-net-device, netdev=net0, bus=virtio-mmio-bus.1` : `virtio-net-device`は、仮想デバイスの一種で、Ethernetカードを仮想化しています。`netdev=net0`は、netdevのIDを指定しています。`bus=virtio-mmio-bus.1`は、仮想デバイスを接続するバスを指定します。
- `object filter-dump, id=filter0, netdev=net0, file=virtio-net.pcap` : `filter-dump`は、パケットをキャプチャするためのフィルタを設定します。`id=filter0`は、フィルタのIDを指定します。`netdev=net0`は、フィルタを適用するネットワークバックエンドを指定します。`file=virtio-net.pcap`は、キャプチャしたパケットを保存するファイルを指定します。
- `-netdev user,id=net0` : ネットワークバックエンドを指定します。`user`は、ホストマシンのネットワークを使用します。`id=net0`で、ネットワークバックエンドのIDを指定します。
- `-kernel build/hinaos.elf` : カーネルイメージを指定します。

<aside class="msg message">
<span class="msg-symbol">🧐</span>
<div class="msg-content">
virtioは準仮想化デバイスのことです。各種仕様は、<a href="https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html">こちら</a>を参照してください。正直僕もまだよくわかっていないです。
</div>
</aside>

これら、オプションはQEMUの[docs](https://www.qemu.org/docs/master/system/invocation.html)の他、`help`コマンドでこんな感じで見ることが出来ます。


```bash
$ qemu-system-riscv32 --help | grep netdev
-netdev user,id=str[,ipv4=on|off][,net=addr[/mask]][,host=addr]
```

また、各プロパティも見れます。

```bash
$ qemu-system-riscv32 -netdev help
Available netdev backend types:
socket
stream
dgram
hubport
tap
user
l2tpv3
bridge
vhost-user
vhost-vdpa
```

それぞれのプロパティを詳しく見るには、こうやります

```bash
$ qemu-system-riscv32 -object filter-dump,help
filter-dump options:
  file=<string>
  insert=<string>
  maxlen=<uint32>
  netdev=<string>
  position=<string>
  queue=<NetFilterDirection>
  status=<string>
```

## まとめ
自分のプログラムをQEMU上で動かす際の方法を知るための準備として、HinaOSがQEMUでどのように起動されているかをオプションから調べてみました。仮想ストレージや、イーサネットはしばらく使うことはないかもしれませんが、かなり勉強になりました。

<iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=yutyan0119-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=4798068713&linkId=08da4deb959756c25c458b74a811b511"></iframe>

---
{: data-content="footnotes"}
