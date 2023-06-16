---
layout: post
author: Yuto Nakamura
tags: [Blog, VLSI symposium]
description: 
ogp_img:
title: Symposium on VLSI Technology and Circuits参加記
latex: false
date: 2023-06-16 19:00:00 +0900
---

VLSI symposiumと呼ばれる学会に参加してきました。この学会は僕の研究分野の中ではISSCCの次に大きな国際学会です。京都とハワイで隔年開催され、今年は京都なため、幸いにも研究室の予算の中で見学させてもらうことができました。今回はその参加記です。特に印象に残った論文（発表）について書いていきます。

## VLSI symposiumとは
その名の通りVLSIについての学会です。1981年から開催されているようです。Technologyと、Circuitsにざっくりとセッションが分けられており、Technologyは半導体技術が中心で、Circuitsはその名の通りなんらかの目的を持った回路が中心です。もし僕がこの学会に論文を出すとしたらCircuitsになります（デジタル回路の研究）。

## 印象に残った論文（発表）
### 6/11
この日はWorkshopに参加。Workshop1では、「Open Source PDKs and EDAs, Community Experiences toward Democratization of Chip Design」ということで、Googleや、SkyWaterなどが先導する、Open Sourceなツールの紹介や実例についての話を聞くことができました。特に、「Design Experience: “The Journey of Two Novice LSI Enthusiasts: Tape-Out of CPU+RAM in Just One Month”」は同学年の日本人学生2名による発表ということもあり、刺激を受けました。俺もCPUを作るぞ。

ちなみにこの2人は今度の火曜日に行われる、RISC-V Day Tokyo 2023 Summer Conferenceでも発表します。是非聞きましょう。

[https://riscv.or.jp/risc-v-day-tokyo-2023-summer/](https://riscv.or.jp/risc-v-day-tokyo-2023-summer/)

### 6/12
この日はShortCourse1/2がありました。基本はShort Course1の「Advanced CMOS Technologies for 1 nm & Beyond」に参加しつつ、Short Course2の「Future Directions in Highspeed Wireline/Optical IO」も見ました。特に面白かったのは、Intelの「Advanced CMOS Transistor Scaling Towards 1nm Node and Beyond」（Short Course 1）と、AMDの「Beyond the Interconnect Challenges on the Way to Enabling Heterogenous Chiplets in Package」（Short Course 2）です。

前者は、1nmより更に向こうの微細化に備えた技術として、リーク電流対策の、「Gate All Around」を中心にどのような技術があるのかについて話を聞くことができました。恥ずかしながら、GAAについては初見だったため、分からない部分も多かったのですが、どんどんと半導体が立体的に複雑になっているなぁというのが理解できました。

後者は、Chipletについての話で、いわゆるUCIe（チップレットにおけるコア間通信の規格）がどのようにして策定され、どのような利点があるかについて聞くことができました。こういう企画がオープンに公開されるのは、産業の発展のためにとても有用だと思いますし、参考になりました。

### 6/13
学会はこの日からが本番です。Plenary Sessionにおける、Googleの人の、「A Six-Word Story on the Future of VLSI: AI-Driven, Software-Defined, and Uncomfortably Exciting」はGoogleのプレゼン力の高さについて知ることができたと同時に話も普通に面白く良かったです。そのあとは、HighlightSessionにいました。やはり、Intelの「E-Core Implementation in Intel 4 with PowerVia (Backside Power) Technology」は面白かったです。この前の日はBeyond 1nmの話でしたが、この日はPowerViaという20Aというプロセスルールで使用される裏面から電源を供給する手法です。実際の講演では、どのような成果が得られたかをグラフなどと共に示してくれてました。こちらで少し解説されています。

[https://news.mynavi.jp/article/20230609-2699628/](https://news.mynavi.jp/article/20230609-2699628/)

その後はProcessorsセッションを見学しました。このセクションは主にEdgeAIデバイスとしてのProcessorの発表が多かったです。同じEEICである黒田研の小菅先生による、「A 183.4nJ/inference 152.8mW Single-Chip Fully Synthesizable Wired-Logic DNN Processor for Always-On 35 Voice Commands Recognition Application」がやはり1番面白かったです。自分もこんな感じで発表したいなぁ…

[https://www.t.u-tokyo.ac.jp/press/pr2023-06-09-002](https://www.t.u-tokyo.ac.jp/press/pr2023-06-09-002)その前の「A 183.4nJ/inference 152.8mW Single-Chip Fully Synthesizable Wired-Logic DNN Processor for Always-On 35 Voice Commands Recognition Application」も面白かったです。こういうのを見ると、ハードウェアにどのようにして最適化させるかというものの一般論的なものが徐々に見えてくるため、勉強になるなと思いました。

その後はDigital Systemsセッションを見学しました。このセッションは自分の研究に近いことが多いため、どれもとても参考になりましたが、やはり中でも「A 4.8mW, 800Mbps Hybrid Crypto SoC for Post-Quantum Secure Neural Interfacing」は、

- 純粋に暗号プロセッサがどのようにして実装されているか
- 自分の研究を国際学会レベルまで引き上げるにはどうすれば良いか
- RISC-Vを研究に活用するにはどうすれば良いか

などが学べたため、この学会で最も参考になる発表でした。本当は著者の方とお話したかったのですが、時間がなく、断念しました。

### 6/14
この日は前の日ほどクリティカルなセッションはありませんでしたが、Advanced NNsセッションの「A 28 nm 66.8 TOPS/W Sparsity-Aware Dynamic-Precision Deep-Learning Processor for Edge Applications」は、RISC-V CoreをCacheとして活用していて、とても面白かったです。

### 6/15
この日はもっとクリティカルなセクションが少なかったのですが、純粋に面白い発表が多かったです。AMDの「AMD Instinct™ MI250X Accelerator Enabled by Elevated Fanout Bridge Advanced Packaging Architecture」などは学術的な意味というよりは純粋にCPUが好きな人間として、新しいチップがどのようにして作られているかを知ることができ、面白かったです。また、「How Harsh is Space?—Equations That Connect Space and Ground VLSI 」では、偶然にもこの春からEEISに所属することになった小林先生のお話を聞くことができ、面白かったです。宇宙での半導体のエラーは地球のそれに比べて2500倍になるらしく、大変だなぁというのが率直な感想でした。

また、リアルタイムに、電圧降下を補正するDeepLearningを動かすSoCの発表がとてもおもしろかったです。
[http://nu-vlsi.eecs.northwestern.edu/Proactive_PM_VLSI2023.pdf](http://nu-vlsi.eecs.northwestern.edu/Proactive_PM_VLSI2023.pdf)

### 6/16
この日は午前中だけの参加でした。セキュリティ関連の話をいくつか聞くことができ、面白かったです。

## その他学会中のイベントなど
毎日何かしら新しい出会いがあるのが学会の良いところだと思います。初日には、CPUを作った2人とお話することが出来ましたし、2日目には一緒に晩ごはんを食べるなどしました。

<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">VLSI symposium 1日目終了！<a href="https://twitter.com/Cra2yPierr0t?ref_src=twsrc%5Etfw">@Cra2yPierr0t</a> <a href="https://twitter.com/heppoko_yuki?ref_src=twsrc%5Etfw">@heppoko_yuki</a> のお二方とも会えてよかったです！！（個人的には東尋坊の話激ウケでした） <a href="https://t.co/R9cPKSxRGB">pic.twitter.com/R9cPKSxRGB</a></p>&mdash; ゆーちゃん (@yutyan_ut) <a href="https://twitter.com/yutyan_ut/status/1667887364038090754?ref_src=twsrc%5Etfw">June 11, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

他にも発表を聞いていたら偶然予備校時代の友人と会い、バンケットで話したり、その繋がりから知り合いが増えたりと、いいなぁと思いました。

また、TSMCのworkshopにも参加させてもらい、FinFET使うぞ～という気持ちを新たにすることが出来ました。

<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">ワクワク <a href="https://t.co/94V8ujF19P">pic.twitter.com/94V8ujF19P</a></p>&mdash; ゆーちゃん (@yutyan_ut) <a href="https://twitter.com/yutyan_ut/status/1668899329229336576?ref_src=twsrc%5Etfw">June 14, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

## おわりに
この学会に参加する機会を与えてくださった、弊研究室の先生に圧倒的感謝しかありません。学部生のペーペーの時期に、このような大きな国際学会に参加させてもらったことを今後に必ず活かし、次は自分がSpeakerとなって戻ってきたいと思います。

![](assets/images/2023-06-16-22-12-06.png)

学会でもらった数々の品

---
{: data-content="footnotes"}

[^1]: [https://labs.cybozu.co.jp/youth.html](https://labs.cybozu.co.jp/youth.html)