---
layout: post
author: Yuto Nakamura
tags: [自作OS, RISC-V]
description: 
ogp_img: /assets/images/ogp_image/QEMU(RISC-V-virt)でHello-world!.png
title: QEMU(RISC-V virt)でHello world!
latex: false
date: 2023-06-03 12:00:00 +0900
---

今回から、いよいよ実際にベアメタルプログラミングをしていきます。まずは、Hello worldを出力してみようと思います。

## virt machineのUARTの利用
QEMUで使用できるRISC-Vマシンの1つに、`virt`というものがあります。これは、RISC-Vの仮想マシンで、UARTが利用出来ます。
ここで利用できるUARTは16550Aというタイプのものらしいです。簡単な仕様の解説は[ここ](https://www.lammertbies.nl/comm/info/serial-uart)にありますが、今回はそこまで深掘りしないで、とりあえず「Hello world!」を表示させることに注力します。

<aside class="msg alert">
<span class="msg-symbol">🤔</span>
<div class="msg-content">
OSのような大きなソフトウェアや、初めてのジャンルのものを扱うときには、深掘りせずにスキップするというのも必要な気がします。とりあえず動かしてみて、その後で深掘りするというのが良いのかもしれません。
</div>
</aside>

UARTで文字を送信する方法はいたって簡単で、`0x10000000`番地に文字を書き込むだけです。memory mapによって、この番地に書き込むとUARTに文字が送信されるようになっています。また、このアドレスは[ソースコード上でも確認出来ます。](https://github.com/qemu/qemu/blob/848a6caa88b9f082c89c9b41afa975761262981d/hw/riscv/virt.c#LL89C8-L89C8)

いかに、main関数とuartを利用してprintするコードを示します。

```c
# define UARTADR 0x10000000

void print_uart0(const char *s) {
    volatile unsigned int * const UART0DR = (unsigned int *)UARTADR;
    while (*s != '\0') {
        *UART0DR = (unsigned int)(*s);
        s++;
    }
}

int main(){
    print_uart0("Hello world!\n");
    return 0;
}

```

`volatile`は、コンパイラによってアドレスが勝手に最適化されないようにするためのものです。これがないと勝手にアドレスが変わる可能性があるので、ちゃんと書いておきましょう。あとは、`UART0ADR`に文字を書き込んでいくだけです。

普通のプログラムならこれだけで終わりですが、OSの入っていないマシンを扱うときにはいくつか前準備が必要です。いわゆるベアメタルプログラミングというやつです。ベアメタルプログラミングについては[セキュリティ・キャンプ2018の資料](https://speakerdeck.com/tnishinaga/security-camp-2018-baremetal-seminar-material?slide=15
)がわかりやすいので、そちらを見ることをおすすめします。

今回の場合、UARTでとりあえず文字が送信出来たら良いので、起動処理はかなり単純です。アセンブラでbootという名前の関数ををつくり、その中では、スタックポインタを設定して、main関数を呼び出すだけです。main関数が終了したら無限ループに入ります。

```c
.section ".boot", "ax"

.global boot
boot:
  addi x1, zero, 0
  la sp, stack_top
  jal main
  
  # loop forever
  j .
```

`sp`は、スタックの現在の最も若いアドレス（つまり最も新しいデータの入っている）を示すレジスタです。これに、`stack_top`という変数を代入しています。`stack_top`は、リンカスクリプト（後述）で定義します。最後に、`main`を呼び出しています。`main`から返ってきたら、無限ループに入ります。

`.section ".boot", "ax"` は、セクションを定義しています。セクションとは、プログラムのメモリ上の配置を指定際のラベルみたいなものです。`ax`は、セクションの属性を指定しています。`a`は、セクションがアラインされるように配置されることを示します。`x`は、セクションが実行可能であることを示します。

`.global boot`は、`boot`というラベルをグローバルなラベルとして定義しています。これは、他のファイルからも参照できるようにするためのものです。

今回使用するvirtマシンではメモリの`0x80000000`番地からプログラムが実行されるようになっています。そのため、`0x80000000`番地にプログラムを配置する必要があります。では`0x80000000`番地にプログラムを配置するにはどうするかというと、リンカスクリプトというものを使用して、リンカ（プログラムのメモリ配置を行うプログラム）に指示を出します。以下に、今回使用するリンカスクリプトを示します。

```c
OUTPUT_ARCH("riscv")
ENTRY(boot)

SECTIONS
{
    . = 0x80000000;
    .text : {
      __text = .;
      KEEP(*(.boot));
      . = ALIGN(4);
      *(.text .text.*);
      . = ALIGN(4096);
      __text_end = .;
    }

    __data = .;
    .rodata : {
        *(.rodata .rodata.*);
        . = ALIGN(4);
        *(.srodata .srodata.*);
        . = ALIGN(4096);
        __rodata_end = .;
    }
    .data : {
        . = ALIGN(4);
        *(.data .data.*);
        . = ALIGN(16);
        *(.sdata .sdata.*);
    }
    .bss : {
      __bss = .;
      *(.bss .bss.*);
      . = ALIGN(16);
      *(.sbss .sbss.*);
      __bss_end = .;
      . = ALIGN(4096);
      stack_top = .;
      . = . + 16384;
    }

    . = ALIGN(4096);
    __data_end = .;
}
```

まず、`SECTIONS`の冒頭で、現在のメモリアドレスを`0x80000000`に設定しています。そこから.textセクションが始まります。ここにはプログラムの命令が入ります。この最も1番上に`KEEP(*(.boot));`としておくことで、.bootセクションに入れた先程のアセンブラのプログラムが冒頭に来てくれるようになります。そのあとは*.textや.text.*といったセクションを配置しています。.rodataセクションは、プログラムの実行中に書き換えることができないデータを配置するセクションです。.dataセクションは、プログラムの実行中に書き換えることができる初期値ありのデータを配置するセクションです。.bssセクションは、プログラムの実行中に書き換えることができるデータのうち、グローバル変数で初期値が指定されていないため、初期値が0であるものを配置するセクションです。今回のプログラムで使用するstackは.bssセクションの中に配置しています。

これで、準備が完了したので、プログラムをビルドしてみます。

```bash
riscv32-unknown-elf-gcc -T kernel/link.ld \
  kernel/rv32/boot.S kernel/main.c -o hello \
  -mabi=ilp32 -fno-stack-protector \
  -fno-zero-initialized-in-bss -ffreestanding \
  -fno-builtin -nostdlib -nodefaultlibs \ 
  -nostartfiles -mstrict-align -march=rv32i \
  -Wall -Wextra
```

QEMUで実行するまえに、ビルドしたプログラムをobjdumpで見てみます。確かに、`ox80000000`番地に最初のプログラムが配置され、そのあとにmainに飛んでいることがわかります。

```bash
riscv32-unknown-elf-objdump -S hello
```

```bash
hello:     file format elf32-littleriscv


Disassembly of section .text:

80000000 <__text>:
80000000:       00000093                li      ra,0
80000004:       00002117                auipc   sp,0x2
80000008:       ffc10113                add     sp,sp,-4 # 80002000 <__bss>
8000000c:       064000ef                jal     80000070 <main>
80000010:       0000006f                j       80000010 <__text+0x10>

80000014 <print_uart0>:
80000014:       fd010113                add     sp,sp,-48
80000018:       02812623                sw      s0,44(sp)
8000001c:       03010413                add     s0,sp,48
80000020:       fca42e23                sw      a0,-36(s0)
80000024:       100007b7                lui     a5,0x10000
80000028:       fef42623                sw      a5,-20(s0)
8000002c:       0240006f                j       80000050 <print_uart0+0x3c>
80000030:       fdc42783                lw      a5,-36(s0)
80000034:       0007c783                lbu     a5,0(a5) # 10000000 <__text-0x70000000>
80000038:       00078713                mv      a4,a5
8000003c:       fec42783                lw      a5,-20(s0)
80000040:       00e7a023                sw      a4,0(a5)
80000044:       fdc42783                lw      a5,-36(s0)
80000048:       00178793                add     a5,a5,1
8000004c:       fcf42e23                sw      a5,-36(s0)
80000050:       fdc42783                lw      a5,-36(s0)
80000054:       0007c783                lbu     a5,0(a5)
80000058:       fc079ce3                bnez    a5,80000030 <print_uart0+0x1c>
8000005c:       00000013                nop
80000060:       00000013                nop
80000064:       02c12403                lw      s0,44(sp)
80000068:       03010113                add     sp,sp,48
8000006c:       00008067                ret

80000070 <main>:
80000070:       ff010113                add     sp,sp,-16
80000074:       00112623                sw      ra,12(sp)
80000078:       00812423                sw      s0,8(sp)
8000007c:       01010413                add     s0,sp,16
80000080:       800017b7                lui     a5,0x80001
80000084:       00078513                mv      a0,a5
80000088:       f8dff0ef                jal     80000014 <print_uart0>
8000008c:       00000793                li      a5,0
80000090:       00078513                mv      a0,a5
80000094:       00c12083                lw      ra,12(sp)
80000098:       00812403                lw      s0,8(sp)
8000009c:       01010113                add     sp,sp,16
800000a0:       00008067                ret
```

また、readelfでセクションの情報を見てみます。

```bash
riscv32-unknown-elf-readelf -a hello
```

```bash
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           RISC-V
  Version:                           0x1
  Entry point address:               0x80000000
  Start of program headers:          52 (bytes into file)
  Start of section headers:          12892 (bytes into file)
  Flags:                             0x0
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         3
  Size of section headers:           40 (bytes)
  Number of section headers:         10
  Section header string table index: 9

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        80000000 001000 001000 00  AX  0   0 16
  [ 2] .rodata           PROGBITS        80001000 002000 001000 00   A  0   0  4
  [ 3] .data             PROGBITS        80002000 003000 000000 00  WA  0   0  1
  [ 4] .bss              NOBITS          80002000 003000 004000 00  WA  0   0  1
  [ 5] .riscv.attributes RISCV_ATTRIBUTE 00000000 003000 00001c 00      0   0  1
  [ 6] .comment          PROGBITS        00000000 00301c 00000f 01  MS  0   0  1
  [ 7] .symtab           SYMTAB          00000000 00302c 000160 10      8  11  4
  [ 8] .strtab           STRTAB          00000000 00318c 00007f 00      0   0  1
  [ 9] .shstrtab         STRTAB          00000000 00320b 00004f 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  D (mbind), p (processor specific)

There are no section groups in this file.

Program Headers:
  Type           Offset   VirtAddr   PhysAddr   FileSiz MemSiz  Flg Align
  RISCV_ATTRIBUT 0x003000 0x00000000 0x00000000 0x0001c 0x00000 R   0x1
  LOAD           0x001000 0x80000000 0x80000000 0x02000 0x02000 R E 0x1000
  LOAD           0x003000 0x80002000 0x80002000 0x00000 0x04000 RW  0x1000

 Section to Segment mapping:
  Segment Sections...
   00     .riscv.attributes 
   01     .text .rodata 
   02     .data .bss 

There is no dynamic section in this file.

There are no relocations in this file.

The decoding of unwind sections for machine type RISC-V is not currently supported.

Symbol table '.symtab' contains 22 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 80000000     0 SECTION LOCAL  DEFAULT    1 .text
     2: 80001000     0 SECTION LOCAL  DEFAULT    2 .rodata
     3: 80002000     0 SECTION LOCAL  DEFAULT    3 .data
     4: 80002000     0 SECTION LOCAL  DEFAULT    4 .bss
     5: 00000000     0 SECTION LOCAL  DEFAULT    5 .riscv.attributes
     6: 00000000     0 SECTION LOCAL  DEFAULT    6 .comment
     7: 00000000     0 FILE    LOCAL  DEFAULT  ABS ccjI8v5c.o
     8: 80000000     0 NOTYPE  LOCAL  DEFAULT    1 $xrv32i2p1
     9: 00000000     0 FILE    LOCAL  DEFAULT  ABS main.c
    10: 80000014     0 NOTYPE  LOCAL  DEFAULT    1 $xrv32i2p1
    11: 80002000     0 NOTYPE  GLOBAL DEFAULT    2 __rodata_end
    12: 80000014    92 FUNC    GLOBAL DEFAULT    1 print_uart0
    13: 80000000     0 NOTYPE  GLOBAL DEFAULT    1 boot
    14: 80002000     0 NOTYPE  GLOBAL DEFAULT    4 __bss_end
    15: 80006000     0 NOTYPE  GLOBAL DEFAULT    4 __data_end
    16: 80002000     0 NOTYPE  GLOBAL DEFAULT    4 stack_top
    17: 80001000     0 NOTYPE  GLOBAL DEFAULT    1 __text_end
    18: 80000070    52 FUNC    GLOBAL DEFAULT    1 main
    19: 80001000     0 NOTYPE  GLOBAL DEFAULT    1 __data
    20: 80000000     0 NOTYPE  GLOBAL DEFAULT    1 __text
    21: 80002000     0 NOTYPE  GLOBAL DEFAULT    4 __bss

No version information found in this file.
Attribute Section: riscv
File Attributes
  Tag_RISCV_stack_align: 16-bytes
  Tag_RISCV_arch: "rv32i2p1"
```

狙った通りのセクション配置や、各種変数の配置が確認できます。では、QEMUで実行してみます。

```bash
$ qemu-system-riscv32 -smp 1 -nographic -serial mon:stdio --no-reboot -m 128 -machine virt,aclint=on -bios none -kernel hello
Hello world!
```
ちゃんと動きました。

最後に、ビルドするためのMakefileを書いておきます。

```text
PREFIX=riscv32-unknown-elf-
CC=$(PREFIX)gcc
LD=$(PREFIX)ld
AS=$(PREFIX)as

BASE_CFLAGS=-fno-stack-protector -fno-zero-initialized-in-bss -ffreestanding
OPT_CFLAGS=-fno-builtin -nostdlib -nodefaultlibs -nostartfiles -mstrict-align
WARN_CFLAGS=-Wall -Wextra
ARCH_CFLAGS=-march=rv32i

CFLAGS=$(BASE_CFLAGS) $(OPT_CFLAGS) $(WARN_CFLAGS) $(ARCH_CFLAGS)
ASFLAGS=-march=rv32i
LDFLAGS=-Tkernel/rv32/link.ld

C_SRC=$(wildcard kernel/*.c kernel/rv32/*.c)
S_SRC=$(wildcard kernel/*.S kernel/rv32/*.S)
OBJ_FILES=$(C_SRC:.c=.o) $(S_SRC:.S=.o)

kernel/kernel: $(OBJ_FILES)
	$(LD) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -c -o $@ $<

clean:
	rm -rf $(OBJ_FILES) kernel/kernel

run: kernel/kernel
	qemu-system-riscv32 -smp 1 -nographic -serial mon:stdio --no-reboot -m 128 -machine virt,aclint=on -bios none -kernel kernel/kernel

.PHONY: clean run
```

これで一旦ﾖｼ!

## まとめ
UARTを使用してHello Worldしました。ベアメタルだとここまでにも一苦労ですね。
今日までの進捗は以下のGitHubにて公開しています。

[https://github.com/yutyan0119/FlightTrailOS](https://github.com/yutyan0119/FlightTrailOS)

どうでも良いですが、開発予定のOSは「FlightTrailOS」という名前にしました。最初からコミットを追えるようにして、軌跡を追えるようにという意味です。Flightがついているのは気分です。

<iframe sandbox="allow-popups allow-scripts allow-modals allow-forms allow-same-origin" style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t=yutyan0119-22&language=ja_JP&o=9&p=8&l=as4&m=amazon&f=ifr&ref=as_ss_li_til&asins=4798068713&linkId=08da4deb959756c25c458b74a811b511"></iframe>

---
{: data-content="footnotes"}
