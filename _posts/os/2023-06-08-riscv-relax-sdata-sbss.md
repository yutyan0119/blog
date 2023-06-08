---
layout: post
author: Yuto Nakamura
tags: [自作OS, RISC-V]
description: 
ogp_img:
title: RISC-Vにおける.sbss, .sdataとgpレジスタについて
latex: false
date: 2023-06-08 19:25:00 +0900
---

リンカスクリプト、よくわからないことが非常に多いのですが、その中でも特によくわからないのが、`.sbss`、`.sdata`です。なんのために存在し、`.bss`、`.data`セクションと何が違うのか、についてメモしておきます。gpレジスタはその中で面白い働きをしています。

## .bss/.dataセクションとは
リンカスクリプトの役割については、以下の資料を見てもらうのが良いと思いますが、`.bss`、`.data`セクションはそれぞれ、変数の格納領域として使用され、
- .data: 初期値を持つ変数
- .bss: 初期値を持たないグローバル変数

をそれぞれ格納します。

[https://speakerdeck.com/tnishinaga/security-camp-2018-baremetal-seminar-material?slide=113](https://speakerdeck.com/tnishinaga/security-camp-2018-baremetal-seminar-material?slide=113)

規約上、`.bss`セクションは、ゼロクリアされていることを、保証しなければなりません。


### .bssセクションの初期化
したがって、ベアメタルプログラミングを行う際には、（それがOSか否かは問わず）.bssセクションをゼロクリアします。
これが、前回の記事で次回触れると言っていた`clear_bss`の実装です。

```c
void clear_bss() {
    extern unsigned int* __bss_start, __bss_end;
    unsigned int start = (unsigned int)__bss_start;
    unsigned int end = (unsigned int)__bss_end;
    while (start < end) {
        *(unsigned int*)start = 0;
        start ++;
    }
}
```
このうち、`__bss_start`、`__bss_end`はリンカスクリプトで定義されているシンボルです。これらは、それぞれ、`.bss`セクションの先頭、終端を指しています。
`extern`キーワードを使用することで、このファイル内に定義がなくとも、リンカスクリプトで定義されているシンボルを使用することができます。

```text
    .bss : {
      __bss_start = .;
      *(.bss .bss.*);
      . = ALIGN(16);
      *(.sbss .sbss.*);
      __bss_end = .;
      . = ALIGN(4096);
      . = . + 16384;
      stack_top = .;
    }
```

[http://yutyan.dev/os-task-create](http://yutyan.dev/os-task-create)

ちなみに、.bssセクションをクリアしている保証がない前提でコンパイルするオプションもあり、それが`-fno-zero-initialized-in-bss`です。

## .sbss, .sdataセクションについて

sは「small」を意味します。つまり、これらのセクションは小さなデータ項目を格納するために使われるようです。（どの程度の小さいかは、おそらくアーキテクチャ依存）

.sdataセクションは小さなデータ項目を格納するために使用されます。アーキテクチャによっては、小さなデータ項目の読み書きを最適化するための特別な指令がある場合があります。それらの指令を利用して、プログラムのパフォーマンスを改善することが可能になります。.sbssセクションは小さな初期化されていないデータ項目を格納するために使用されます。

RISC-Vにおいては、gp(global pointer)レジスタを使用して、これらの小さいデータへのアクセスを最適化するようです。

### 最適化の例
SiFiveのブログから、最適化の例を引用します。
[https://www.sifive.com/blog/all-aboard-part-3-linker-relaxation-in-riscv-toolchain](https://www.sifive.com/blog/all-aboard-part-3-linker-relaxation-in-riscv-toolchain)
以下のようなコードを考えます。このコードは、グローバル変数へのアクセスを3回も行っています。

```c
/* Global Variables: */
Boolean         Bool_Glob;
char            Ch_1_Glob,
                Ch_2_Glob;

Proc_4 () {
  Boolean Bool_Loc;

  Bool_Loc = Ch_1_Glob == 'A';
  Bool_Glob = Bool_Loc | Bool_Glob;
  Ch_2_Glob = 'B';
} /* Proc_4 */
```
このコードをアセンブルすると、以下のようなアセンブリコードになります。

```text
0000000040400826 <Proc_4>:
    40400826:   3fc00797                auipc   a5,0x3fc00
    4040082a:   f777c783                lbu     a5,-137(a5) # 8000079d <Ch_1_Glob>
    4040082e:   3fc00717                auipc   a4,0x3fc00
    40400832:   f7272703                lw      a4,-142(a4) # 800007a0 <Bool_Glob>
    40400836:   fbf78793                addi    a5,a5,-65
    4040083a:   0017b793                seqz    a5,a5
    4040083e:   8fd9                    or      a5,a5,a4
    40400840:   3fc00717                auipc   a4,0x3fc00
    40400844:   f6f72023                sw      a5,-160(a4) # 800007a0 <Bool_Glob>
    40400848:   3fc00797                auipc   a5,0x3fc00
    4040084c:   04200713                li      a4,66
    40400850:   f4e78a23                sb      a4,-172(a5) # 8000079c <Ch_2_Glob>
    40400854:   8082                    ret
```

見るとわかるように、`auipc`命令を使用して、グローバル変数のアドレスを計算しています。4回アドレスを計算していますが、それぞれで計算されているアドレスは12bitのオフセット内に収まっています。そこで、以下のようなリンカスクリプトを用意します。

```text
/* We want the small data sections together, so single-instruction offsets
   can access them all, and initialized data all before uninitialized, so
   we can shorten the on-disk segment size.  */
.sdata          :
{
  __global_pointer$ = . + 0x800;
  *(.srodata.cst16) *(.srodata.cst8) *(.srodata.cst4) *(.srodata.cst2) *(.srodata .srodata.*)
  *(.sdata .sdata.* .gnu.linkonce.s.*)
}
_edata = .; PROVIDE (edata = .);
. = .;
__bss_start = .;
.sbss           :
{
  *(.dynsbss)
  *(.sbss .sbss.* .gnu.linkonce.sb.*)
  *(.scommon)
```

このリンカスクリプトでは、.sdataと.sbssを隣り合うようにして、オフセットを利用したメモリアクセス命令でアクセスできるようにしています。
`__global_pointer$`が、`.sdata`の先頭から`0x800`先を指しています。これによって12bitのオフセットで、`.sdata`の先頭にアクセスすることが出来ます。リンカは、このシンボルが定義されていると、この値がgpレジスタに入っていると仮定し、その±12bitオフセット以内のアクセスを最適化に使用することが出来るようになります。以下は、初期化時に`gp`を設定するアセンブリコードです。

```text
.option push
.option norelax
1:auipc gp, %pcrel_hi(__global_pointer$)
  addi  gp, gp, %pcrel_lo(1b)
.option pop
```

ここでは、`norelax`を設定しています。そうしないと、リンカーは`mv gp, gp`といった最適化をしてしまいます。
このgpを利用して最適化すると、アセンブリが以下のようになります。

```text
00000000400003f0 <Proc_4>:
    400003f0:   8651c783                lbu     a5,-1947(gp) # 80001fbd <Ch_1_Glob>
    400003f4:   8681a703                lw      a4,-1944(gp) # 80001fc0 <Bool_Glob>
    400003f8:   fbf78793                addi    a5,a5,-65
    400003fc:   0017b793                seqz    a5,a5
    40000400:   00e7e7b3                or      a5,a5,a4
    40000404:   86f1a423                sw      a5,-1944(gp) # 80001fc0 <Bool_Glob>
    40000408:   04200713                li      a4,66
    4000040c:   86e18223                sb      a4,-1948(gp) # 80001fbc <Ch_2_Glob>
    40000410:   00008067                ret
```
確かに、メモリへのアクセスの前にアドレスをむやみやたらと計算せずに、オフセットを使用して美しいやり方でアクセスしています。こういうやり方で、`.sdata`及び、`.sbss`セクションには、なるべく少ない命令でアクセスできるように、小さいデータを詰め込むわけです。ちなみにと言ってはなんですが、現時点での自作OSは、`-mno-relax`により、これらの最適化は一旦行わないようにしています。


## まとめ
`.sbss`及び`.sdata`セクションの意味とそのgpとの関係について、最適化が関わっていることに触れながらまとめました。最適化する際はこういうことを考えているんだなということがわかり、面白かったです。

---
{: data-content="footnotes"}
