---
layout: post
author: Yuto Nakamura
tags: [自作OS, RISC-V]
description: 
ogp_img: /assets/images/ogp_image/【自作OS】まずは簡単なタスクの生成と切り替えを実装してみた.png
title: 【自作OS】まずは簡単なタスクの生成と切り替えを実装してみた
latex: false
date: 2023-06-08 00:30:00 +0900
---

今回は、[前回](https://yutyan.dev/qemu-helloworld)のHello Worldに続いて、タスクの生成、切り替えを簡易的に実装していこうと思います。
OSの機能は数しれずですが、タスクの管理はその中でも特に重要な部類に入ると個人的に思っています。
今回の記事の内容は[このPR](https://github.com/yutyan0119/FlightTrailOS/pull/1)でmainにマージされているので、それも参照しつつ見てください。

<!-- [![](https://opengraph.githubassets.com/39be8ae302d7b804fd6389d7c4e34fa927515654f59ca5fc3c4aef81b82a1ef1/yutyan0119/FlightTrailOS/pull/1)](https://github.com/yutyan0119/FlightTrailOS/pull/1) -->
[https://github.com/yutyan0119/FlightTrailOS/pull/1](https://github.com/yutyan0119/FlightTrailOS/pull/1)

## RISC-VのABIについて
ABIとは、アプリケーションバイナリインターフェイスの略で、関数の呼び出し規約や、データ型の大きさなどを指定しています。基本的に今回作成するOSの範囲内では、lip32dと呼ばれるものを使用します。コンパイラ側でこれを前提にコンパイルされるため、自分でアセンブラを書く際にも、これを考慮しないといけません。

以下に、ABI規約に基づいた、レジスタの表を示します。

| レジスタ名 | ABI名  | 用途                                  | 保存           |
| ---------- | ------ | ------------------------------------- | -------------- |
| x0         | zero   | 常にゼロ                              | -              |
| x1         | ra     | 戻りアドレス                          | 呼び出し側     |
| x2         | sp     | スタックポインタ                      | 呼び出された側 |
| x3         | gp     | グローバルポインタ                    | -              |
| x4         | tp     | スレッドポインタ                      | -              |
| x5-x7      | t0-t2  | 一時的レジスタ                        | 呼び出し側     |
| x8         | fp/s0  | フレームポインタ (または保存レジスタ) | 呼び出された側 |
| x9         | s1     | 保存レジスタ                          | 呼び出された側 |
| x10-x11    | a0-a1  | 関数引数/戻り値                       | 呼び出し側     |
| x12-x17    | a2-a7  | 関数引数                              | 呼び出し側     |
| x18-x27    | s2-s11 | 保存レジスタ                          | 呼び出された側 |
| x28-x31    | t3-t6  | 一時的レジスタ                        | 呼び出し側     |

ここで、保存とは、ある関数からある関数を呼び出した際に、元の関数でのレジスタの値をどちらが保存しておくかを表しています。これについてもう少しわかりやすく表にすると、以下のようになります。

| ABI名  | 用途             | 保存           |
| ------ | ---------------- | -------------- |
| ra     | 戻りアドレス     | 呼び出し側     |
| a0-a7  | 関数引数(戻り値) | 呼び出し側     |
| t0-t6  | 一時的レジスタ   | 呼び出し側     |
| sp     | スタックポインタ | 呼び出された側 |
| s0-s11 | 保存レジスタ     | 呼び出された側 |

例えば以下のような流れを考えます。
1. mainを実行する
2. mainの中でcalcを実行する
3. calcの中でsqrtを実行する
4. calcに戻る
5. mainに戻る

この場合、calc関数はraに、main関数の戻るべき命令へのアドレスを持っていますが、sqrt関数に移った際に、当然ながらraには、calc関数の戻るべき命令へのアドレスが入ってしまいます。したがって、calc関数では、sqrt関数を呼び出す前にraの値を保存しておかないといけません。同様のことが、a0-a7やt0-t6のレジスタについても言え、呼び出し側保存と書いてあるレジスタは、呼び出す前にメモリに保存されることが要求されます。

![](images/os-create-task/os-ra.drawio.png "raの使われ方"){: width="75%"}

一方で、spやs0-s11については、呼び出された側が、呼び出されたときの状況に最後に戻すことを要求されます。そのため、呼び出された側の関数で一旦レジスタの値を保存し、また関数に戻ってきたときはそれを自分のレジスタに戻すということが要求されます。

また、関数の引数については、第一引数から順にa0, a1, ..., a7に入ります。仮にそれ以上の引数がある場合はスタック領域を使用するようです。

## タスク生成
OSにおいて、タスクは色々な情報を持ちます。タスクに当てられるIDや、スケジューリング（タスクの実行を平等にするもの）のための実行時間や優先度、実行状態などがこれにあたります。
今回は超簡単にタスクを生成するだけなので、IDを持つだけとします。加えてタスクに割り当てられるスタック領域に関する情報をまとめて、以下のような構造体にすることにしました。

```c
typedef struct task_info {
    int pid; //ID
    unsigned int stack[4096]; //確保されるスタック領域
    unsigned int sp; //スタックポインタ
} task_info;
```

タスクを生成するときには、`stack`の末尾アドレスを`sp`に保存し、タスク実行時にこれをspレジスタに移すことで、呼び出された側がspレジスタの値を保存しておくという守り事を守ります。
他に呼び出された側で保存すべきレジスタであるs0-s11については、`sp`の要素として生成時に値を0にして確保することにします。また、タスクを実行する際にはraにそのタスクのアドレスを入れておいて、最後に`ret`することで実行する命令の位置をraから与えることが出来るため、これも`stack`に入れておきます。これを実装したのが以下です。

```c
void task_create(task_info* task, void (*entry)(void), int pid) {
    task->pid = pid;
    //タスクのスタックポインタを設定
    task->sp = (unsigned int)&(task->stack[4096]);
    // stack pointerをずらしながら、レジスタの初期値を設定していく
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s11
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s10
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s9
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s8
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s7
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s6
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s5
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s4
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s3
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s2
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s1
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = 0; // s0
    task->sp -= sizeof(unsigned int);
    *((unsigned int*)(task->sp)) = (unsigned int)entry; // ra
    return;
}
```

ここで
```c
*((unsigned int*)(task->sp)) = 0;
```

とは、`task->sp`の値をポインタとしたときの、その位置の値を0にするという意味です。分かりづらいですが、実際には以下のようになっているとも言えます。

```c
void task_create(task_info* task, void (*entry)(void), int pid) {
    task->pid = pid;
    //タスクのスタックポインタを設定
    task->sp = (unsigned int)&(task->stack[4096]);
    // stack pointerをずらしながら、レジスタの初期値を設定していく
    task->stack[4095] = 0; //s11
    //...
    task->stack[4084] = 0; //s0
    task->stack[4083] = (unsigned int)entry;
    return;
}
```

気をつけておきたいのは`stack`配列に保存されるのは、`unsigned int`の値ですが、この値自体は、アドレスを示しているということです。

## タスクを実行する
タスクを実行する際には、`task->stack`に保存しておいた、先程の各値を順番にレジスタに配置していきます。

```c
/* 
includeファイルに以下のようにして定義しておくことで、
C言語のコードから呼び出すことができる

spにスタックポインタのアドレスが入っている場所のアドレスを与えることで、
a0にアドレスが入れられて、タスクのload時に使用することが出来る。
*/
void task_load_rv32(unsigned int* sp);
```

```as
# a0にはspの現在の位置の値が入っているので、それを取り出す
# そこから順番に値を取り出す。格納した順番と逆に取り出すことが出来る
task_load_rv32:
    lw  sp,  (a0)
    lw   ra,  0*4(sp)
    lw   s0,  1*4(sp)
    lw   s1,  2*4(sp)
    lw   s2,  3*4(sp)
    lw   s3,  4*4(sp)
    lw   s4,  5*4(sp)
    lw   s5,  6*4(sp)
    lw   s6,  7*4(sp)
    lw   s7,  8*4(sp)
    lw   s8,  9*4(sp)
    lw   s9,  10*4(sp)
    lw   s10, 11*4(sp)
    lw   s11, 12*4(sp)
    addi sp,  sp, 13*4
    ret
```
![](images/os-create-task/os-task-create.drawio.png)
ここまで来たら実際にタスクを生成して実行してみましょう。

```c
#include "task.h"
#include "switch.h"

task_info task_list[2];

#define UARTADR 0x10000000

void print_uart0(const char *s) {
    volatile unsigned int *const UART0DR = (unsigned int *)UARTADR;
    while (*s != '\0') {
        *UART0DR = (unsigned int)(*s);
        s++;
    }
}

void clear_bss() {
    extern unsigned int* __bss_start, __bss_end;
    unsigned int start = (unsigned int)__bss_start;
    unsigned int end = (unsigned int)__bss_end;
    while (start < end) {
        *(unsigned int*)start = 0;
        start ++;
    }
}

void task_1() {
    while (1) {
        print_uart0("task_1\n");
    }
}

int main() {
    // bss領域を初期化する（次回の記事で触れます）
    clear_bss();
    print_uart0("Hello world!\n");
    // 最初のタスクを生成する
    task_create(&task_list[0], task_1, 0);
    // タスクのスタックのアドレスが入っている場所のアドレスを渡す
    task_load_rv32(&task_list[0].sp);
    return 0;
}
```

これで、いつもどおりmakeすると、ひたすらtask_1が表示されます。Includeファイルを指定したりする必要があるため、少しだけMakefileに変更が有りますが、このコミットを見ていただければわかります。

<!-- [![](https://opengraph.githubassets.com/f9a176d059c55f5a4a39397c51fc5305ffb89c9e78835702ce34c4b7d71f067e/yutyan0119/FlightTrailOS/commit/6b4989d546511fbce24e0cebf91ade2c2e5ceebc)](https://github.com/yutyan0119/FlightTrailOS/commit/6b4989d546511fbce24e0cebf91ade2c2e5ceebc#diff-bafde732323b99ea1ed9054d972a49d03089ad81537e87ac24ca63ac8ad066e9) -->

[https://github.com/yutyan0119/FlightTrailOS/commit/6b4989d546511fbce24e0cebf91ade2c2e5ceebc#diff-bafde732323b99ea1ed9054d972a49d03089ad81537e87ac24ca63ac8ad066e9](https://github.com/yutyan0119/FlightTrailOS/commit/6b4989d546511fbce24e0cebf91ade2c2e5ceebc#diff-bafde732323b99ea1ed9054d972a49d03089ad81537e87ac24ca63ac8ad066e9)

## タスクの切り替え
タスクを切り替える際には、現在実行しているタスクが持っているレジスタのうち、呼び出された側が保存しなければならないレジスタについてをタスクスタック領域に退避し、逆に切り替わる側のタスクの情報を切り替わる側のタスクのスタックからレジスタに入れることが必要です。また、raの値についてもスタックに保存しておく必要があります。これは、呼び出された側のタスクが終了した際に、呼び出し側のタスクに戻るために必要な情報です。

![タスクの保存](images/os-create-task/os-task-save.png){: width="75%"}
![タスクのロード](images/os-create-task/os-task-load.png){: width="75%"}

```c
/* 
includeファイルに以下のようにして定義しておくことで、
C言語のコードから呼び出すことができる

a0に切り替え前タスクのスタックポインタが入っている場所のポインタが
a1に切り替え後タスクのスタックポインタが入っている場所のポインタが入れられる
*/
void task_switch_rv32(unsigned int* old_sp, unsigned int new_sp);
```

```as
# a0には切り替え元のspアドレスが入っている
# a1には切り替え先のspアドレスが入っている

task_switch_rv32:
# レジスタを保存する分だけスタックを確保する
    addi sp,  sp, -13*4

# スタックにレジスタを保存する
    sw   ra,  0*4(sp)
    sw   s0,  1*4(sp)
    sw   s1,  2*4(sp)
    sw   s2,  3*4(sp)
    sw   s3,  4*4(sp)
    sw   s4,  5*4(sp)
    sw   s5,  6*4(sp)
    sw   s6,  7*4(sp)
    sw   s7,  8*4(sp)
    sw   s8,  9*4(sp)
    sw   s9,  10*4(sp)
    sw   s10, 11*4(sp)
    sw   s11, 12*4(sp)

# スタックポインタをa0の指すスタックに保存する    
    sw   sp,  (a0)

# スタックポインタをa1から復元する
    lw   sp,  (a1)

# レジスタを復元する
    lw   ra,  0*4(sp)
    lw   s0,  1*4(sp)
    lw   s1,  2*4(sp)
    lw   s2,  3*4(sp)
    lw   s3,  4*4(sp)
    lw   s4,  5*4(sp)
    lw   s5,  6*4(sp)
    lw   s6,  7*4(sp)
    lw   s7,  8*4(sp)
    lw   s8,  9*4(sp)
    lw   s9,  10*4(sp)
    lw   s10, 11*4(sp)
    lw   s11, 12*4(sp)

# スタックを解放する
    addi sp,  sp, 13*4

# raの指す命令の場所へ戻る
    ret
```

最後に、タスクの切り替えを実際に動かしてみます。
```c
void task_1() {
    while (1) {
        print_uart0("task_1\n");
        task_switch(&task_list[0], &task_list[1]);
    }
}

void task_2() {
    while (1) {
        print_uart0("task_2\n");
        task_switch(&task_list[1], &task_list[0]);
    }
}

int main() {
    // bss領域を初期化する（次回の記事で触れます）
    clear_bss();
    print_uart0("Hello world!\n");
    // タスクを生成する
    task_create(&task_list[0], task_1, 0);
    task_create(&task_list[1], task_2, 1);
    // タスクのスタックのアドレスが入っている場所のアドレスを渡す
    task_load_rv32(&task_list[0].sp);
    return 0;
}
```
これでtask_1とtask_2が順番に表示されることがわかりました。これだけだと本当にスタック領域が移動されているか分かりづらいので、整数をプリントするようにして、確かにタスクの情報が残っていることを確認するようにしましょう。以下のコミットのようにすれば、整数が変わることがわかります。
<!-- [![](https://opengraph.githubassets.com/256668d55b6c6ebb707a65545e8841ad9aed519f9d9f7007171f8586a546a48d/yutyan0119/FlightTrailOS/commit/333670d5714d87adab598bc0ca7715fbb3420ff6)](https://github.com/yutyan0119/FlightTrailOS/commit/333670d5714d87adab598bc0ca7715fbb3420ff6) -->

[https://github.com/yutyan0119/FlightTrailOS/commit/333670d5714d87adab598bc0ca7715fbb3420ff6](https://github.com/yutyan0119/FlightTrailOS/commit/333670d5714d87adab598bc0ca7715fbb3420ff6)

![](https://pbs.twimg.com/media/FyAiHy8aIAIcLq3?format=png&name=360x360)

## gdbを利用したデバッグについて
今回から、若干ややこしいプログラムを実行したため、デバッガが必要になる場面がありました。そんなときに使ったいくつかのTipsについてここにメモしておきます。

### デバッガについて
gdb-multiarchを使用します。
```bash
sudo apt install gdb-multiarch
```
でインストール出来ます。

### デバッグ用のビルドと実行
コンパイル時にデバッグ情報を埋め込まないと、gdbで1行ずつの実行や変数の中身を見ることが出来ません。そこで、`-g -O0`オプションを付けてコンパイルします。
前者はデバッグ情報を埋め込むオプション、後者は最適化を無効にするオプションです。実行は以下のようにします。

```bash
qemu-system-riscv32 -smp 1 -nographic -serial mon:stdio --no-reboot -m 128 -machine virt,aclint=on -bios none -kernel kernel/kernel -S -gdb tcp::1234
```

`-S`で、CPUを最初の命令でストップし、`-gdb tcp::1234`でgdbの接続を待ち受けるようにします。gdbを起動して、以下のようにします。

```bash
gdb-multiarch kernel/kernel
(gdb) target remote localhost:1234
```

### gdbの使い方
#### ブレークポイントの設定
```bash
(gdb) b main
```
これで、mainで止まるようになります。`b`の後に関数名を指定すると、その関数の先頭で止まります。`b`の後にファイル名と行番号を指定すると、その行で止まります。

#### ブレークポイントまで実行
```bash
(gdb) c
```
これで、ブレークポイントまで実行します。

#### 1行ずつ実行
```bash
(gdb) n
```
もしくは
```bash
(gdb) s
```
これで、1行ずつ実行します。`n`は関数の中に入らないのに対し、`s`は関数の中に入ります。

#### 変数の中身を見る
```bash
(gdb) p 変数名
```
これで、変数の中身を見ることが出来ます。C言語の場合、ポインタの中身を見るときは、`*`をつけることで見れます。どうように、アドレスも`&`をつけることで見ることが出来ます。
また、16進数で見たい場合は、`p/x 変数名`で見ることが出来ます。

#### レジスタの中身を見る
```bash
(gdb) info registers
```
QEMUでも使える例のコマンドです。

#### アセンブラを見る
```bash
(gdb) disassemble
```
これで現在の位置のアセンブラを見ることが出来ます。

#### 1命令ずつ実行
```bash
(gdb) si
```
これで、1命令ずつ実行します。C言語のソースの場合、1行ずつ実行することが出来ますが、アセンブラの場合、1行ずつ進めることは出来ないため、これを利用して、1命令ずつ実行し、変数の中身を見たりすることで、デバッグをしていきます。

## まとめ
自作OSのはじめの1歩として、簡単なタスクの生成と切り替えを行いました。もちろんこれだけでOSと言うには無理がありますが、良い一歩になったと思います。また、gdbを使ったデバッグについても、少し触れました。次回は、タスクのスケジューリングを行っていくつもりです。

---
{: data-content="footnotes"}
