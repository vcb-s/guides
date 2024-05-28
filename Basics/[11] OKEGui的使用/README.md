# 第十一章 OKEGui的使用

本章介绍 VCB-Studio 的压制生产力工具 OKEGui。

## 1. vpy脚本与项目配置文件的编写

VCB-Studio 的生产力工具 [OKEGui](https://github.com/vcb-s/OKEGui)，全名 One Key Encode Gui，用于全自动压片。你可以在[这里](https://github.com/AmusementClub/tools/releases)下载到已经打包好的版本，解压即用。在 OKEGui\examples 中提供了多个配置文件样例，可以作为参考。

OKE 的功能比较复杂，因此本小节只讲基本用法，剩下的高级功能放到后续小节讲解。

需要注意的是，OKE 的鲁棒性不是很好，只保证按规范进行操作的结果。

每个 OKE 任务需要总监准备 2 个文件，一个 vpy 脚本文件和一个项目配置文件。  
这 2 个文件需要放在同目录下，一般放在对应 BD 的根目录。

### (1). 预处理脚本文件（vpy）

vpy 脚本文件和正常脚本一样，但是会有几个由 OKEGui 读取的固定 tag。

#### (1) `#OKE:INPUTFILE`

这是唯一一个**必选 tag**，作用是指定输入文件。  

接下来一行必须是“变量 = 文件名”的格式，比如这样：

```py
#OKE:INPUTFILE
a = "00000.m2ts" # will be replaced
src = core.lsmas.LWLibavSource(a)
```

OKE 在执行任务的时候，会把文件名自动替换为指定的输入文件。

#### (2) `#OKE:DEBUG`

这是一个**可选 tag**，用于处理本组祖传的 debug 开关。  

```py
#OKE:DEBUG
Debug = 1
if Debug:
    res = mvf.Preview(res)
else: res = mvf.Depth(res,10)
```

写脚本的时候，`Debug=1`，输出 RGB；压制的时候，`Debug=0`，输出 YUV 10bit。

OKE 读取这个 tag，压制的时候将其替换为 `None`，保证压制时永远执行 `else` 分支。

#### (3) `#OKE:PROJECTDIR`

用来获取 vpy 脚本文件所在的绝对路径。

也是一个**可选 tag**，一般用于加载额外的脚本或滤镜。

加载名为 custom.py 的脚本：
```py
import sys
import os

#OKE:PROJECTDIR
projDir = '.'
sys.path.insert(1, projDir)
import custom
```

加载名为 `libcustom.dll` 的滤镜：
```py
import sys
import os

#OKE:PROJECTDIR
projDir = '.'
sys.path.insert(1, projDir) 
core.std.LoadPlugin(os.path.realpath(os.path.join(projDir, 'libcustom.dll')))
```

当然，需要确保额外加载的脚本和滤镜和 vpy 脚本同目录。

这个功能用的时候很少。

#### (4) `#OKE:MEMORY`

注意，这是一个**已经弃用**的**可选 tag**。

在一些旧脚本中，会见到：
```py
core.num_threads = 8
#OKE:MEMORY
core.max_cache_size = 8000
```
`num_threads` 指定运行时的线程。  
`max_cache_size` 指定运行时的内存。  

前者现在不推荐指定，让 VS 自己管理线程池比较好一点。

后者，在 VS API4 时代，已经不需要手动指定内存，都是让 VS 自动收敛。

如果设置这个 tag，OKE 会根据主界面“空闲内存数”，和现有的任务数，来设置 `max_cache_size`。

<img src="./media/image01.png" />

当然，现在不用这个 tag 了，“空闲内存数” 直接填任意小于 2000 的数就行。  
大于 2000 的话 OKE 会在启动任务的时候检查系统是否有那么多空闲内存，在压制中途加任务时会带来一些不必要的麻烦。

#### RP Checker

OKE 还提供 RPC（RP Checker） 功能。

在压制完成后，用成品和源跑一个 PRC，判断是否花屏 。

如果使用这个功能，需要在 vpy 脚本里输出作为 ref 的源视频：
```
res.set_output()
src8.set_output(1)
```

一般用 `src8` 或者 `src16` 即可，**源视频必须输出到1节点**。

另外还需要注意：

1. 必须有相同的帧率和帧数  
如果成品做了 IVTC/deinterlace/trim/splice 之类的操作，则为 RPC 准备的 clip 也需要做

2. 必须有相同的画面内容  
如果做了对画面改动较大的操作，例如 crop/textsub 等操作，则为 RPC 准备的 clip 也需要做

3. 分辨率和 bitdepth 不重要，因为 RPC 会自动转为与成品相同的规格

### (2). 项目配置文件（json 或 yaml）

项目配置文件，支持 json 和 yaml，下面以 json 为例。

大家可以参考 `OKEGui\examples\demo.json`，本小节只讲基础的部分。

需要注意，以下的 tag 名字是严格区分大小写的。另外 `bool` 类型的 tag 不能写 `1/0` 必须写 `true/false`。

+ `Version`

    **必须设置为 `3`**，此时会强制检查 VS 环境版本，即必须搭配我们的 portable 包使用。

+ `VSVersion`

    指定 portable VS 包的版本。

+ `ProjectName`

    项目名，可随意填写，用于在 OKE 里区分用的脚本。  
    一般写：`xx main`，`xx op`， `xx pv` 之类的。

+ `EncoderType`

    编码器类型，可以选 `x264`、`x265`、`svtav1`。

+ `Encoder`

    指定编码器路径，可以使用相对或绝对路径。  
    可以不指定，这时选用 OKE 自带的。  
    一般除非要测试新编码器，否则都用 OKE 自带的就行。

+ `EncoderParam`

    编码器参数，不需要写 `--y4m` 和 `--output`。

+ `ContainerFormat`

    压制成品封装容器，可以选 `mp4` 或 `mkv`。

+ `AudioTracks`

    这是一个列表，其中每一项表述源文件的一个音轨，源文件包含几条音轨，这个列表就必须有几项。

    每项有这些功能：

    - `OutputCodec`

        输出格式，可选 `flac`、`aac`、`ac3` 或 `dts`。  
        其中 `ac3` 和 `dts` 只能作为抽取原盘相同编码音轨使用，不支持重编码为这些格式。

    - `Bitrate`

        编码 aac 的码率，前一项为 `aac` 时有效，可以指定码率，默认为 `192`。

    - `MuxOption`

        封装格式，可选 `Default`、`Mka`、`External`、`ExtractOnly` 或 `Skip`。

        默认为 `Default`，表示正常封装。  
        `Mka` 表示额外封装在 MKA 文件中。  
        `External` 表示外挂，会给文件名加上 CRC32，这个实际中已经不会使用。  
        `ExtractOnly` 只做抽取。  
        `Skip` 直接不抽取。  

    - `Language`

        轨道语言，默认为 `jpn`，可选 `eng`、`chi` 等等。

    - `Name`

        轨道名称，多音轨时可以设置。  
        例如 `Main`、`Commentary`、`2.0ch`、`5.1ch` 等等。

+ `SubtitleTracks`

    字幕轨列表，其中每一项表述源文件的一个字幕，当源有 PGS 字幕时才会用。

    与音轨类似，有 `MuxOption`，`Language`，`Name` 子项。

+ `InputScript`

    输入 vpy 脚本的文件名。  
    注意，脚本文件**必须**和 json 文件放在**同一目录**下。

+ `InputFiles`

    这是一个可选的列表，其中每一项是一个字符串，用于指定待压制的源文件路径，例如 `"BDMV\\STREAM\\00000.m2ts"`。支持相对路径和绝对路径，相对路径以 json 文件所在目录为基准。

    在载入 json 时会有一个选择输入文件的步骤，如果填写了该字段，这些源文件会直接在这个界面显示出来；如果没有填写，则可以手动拖入源文件。

+ `Fps`

    脚本输出的帧率，可选 `1.0`、`23.976`、`24.000`、`25.000`、`29.970`、`50.000`、`59.940`。

    当帧率不是上述七种之一时，使用 `FpsNum` 和 `FpsDen` 指定。

+ `Rpc`

    表示是否在压制完成后执行 RPC，可选 `true` 或 `false`。  
    启用 RPC 时 vpy 脚本需要输出 ref 视频。

### (3). OKE运行任务

OKE 任务需要以一个完整视频为基本单位。遇到肉酱和连体，需要先转为 1 集一个 mkv 文件来压制。

用法比较简单：
<img src="./media/image02.jpg" />
<img src="./media/image03.png" />
<img src="./media/image04.png" />

如果需要多开，点击右下角“新建工作单元”。

如果载入任务出错，或者压制过程中出错，需要清掉所有任务，重新添加。

压制完成后，json 文件所在目录下会有一个名为 `output` 的目录。  
包含所有成品文件，如 MKV、MKA 和 MP4 等。  
如果花屏检查未通过，RPC 结果文件也将出现在 `output` 里。

还有一个 `X_` 目录，这里 `X` 是 json 所在盘符，会保存中间的临时文件。


## 2. 音轨的处理

除了前一小节提到的基础音轨功能，OKE 还提供以下功能：空音轨和重复音轨的检测、可选音轨、音轨重排序、有损音轨压制、默认轨道标志的处理。

### (1). 空音轨和重复音轨的检测

OKE 可以自动检测空音轨和重复音轨，在封装成品时将它们删去。在编写配置文件时，不用判断是否是空音轨和重复音轨，都当做正常封装来处理，OKE 会自动决定是否保留。

### (2). 可选音轨

在一些新番中，往往不再使用空音轨和重复音轨来处理评论音轨的问题，而是直接使用不同数量的音轨。这就造成，一个项目配置文件无法兼容所有集数的情况。

OKE 采用可选标签 `Optional` 来处理这个问题。对于每条音轨，都可以设置 Optional 标签。如果为 true，则在原盘不存在该条轨道时直接忽略，而不报错。

以下用法可以兼容一条主音轨，和一条主音轨加上一条评论音轨的情况。

```json
"AudioTracks" : [{
    "OutputCodec" : "flac",
    "Name" : "Main Audio"
},{
    "OutputCodec" : "aac",
    "Bitrate" : "192",
    "Name" : "Audio Commentary",
    "Optional" : true
}]
```

需要注意的是，如果有多条轨道均标记为 `Optional = true`，则要求它们要么都存在，要么都不存在。

### (3). 音轨重排序

默认情况下，成品音轨的封装顺序与原盘中的顺序相同，但少数情况下这种顺序并不是我们希望的。

OKE 提供了一种重新排序的方式，对于每条音轨，可以设置 `Order`。Order 是一个非负整数，OKE 会按照 Order 对音轨进行稳定的升序排序，即更小 Order 的轨道会在前面。

默认情况下，所有音轨有最大的 Order，因此如果希望将某一音轨提到最前面，只需要设置 `Order = 1` 即可。

### (4). 有损音轨压制

OKE 支持编码音轨为 AAC，但正常情况下只对无损音轨生效，有损音轨只能保持原状。根据整理规范，对于码率 >= 512kbps 的有损音轨，需要二压为更低码率的 AAC。

OKE 提供了有损音轨压制的方式，对于每条音轨，可以设置 `Lossy` 标签。如果为 true，则当源音轨为有损编码格式时也可重编码为 AAC。

需要注意的是，并非所有有损格式都能二压，比如 eac3 格式，目前不支持二压。

### (5). 默认轨道标志

OKE 会自动调整各音轨的默认轨道标志，只有正常封装的第一条音轨被标记为 `yes`，其他所有音轨，包括 mka 中的音轨都会被标记为 `no`。这样可以避免挂载 mka 时同时解码两条音轨，在部分播放环境下出错的问题。


## 3. 字幕的处理

与音轨类似，对于字幕轨，OKE 提供以下功能：空字幕轨的检测、可选字幕轨、字幕轨重排序、默认轨道标志的处理。

前三个功能与音轨完全相同，字幕轨也同样支持 Optional 和 Order 标签功能，不再赘述。

关于默认轨道标志，与音轨不同，原盘的字幕轨往往是日文或者英文，因此均默认标记为 `no`，这样播放时不会自动挂载字幕轨。

除了原盘的 PGS 字幕，OKE 也能识别 ass 和 srt 字幕，但是不支持封装，只能设置 `MuxOption = Skip` 来丢弃。这一功能在压制 webrip 时会用到。

## 4. 章节的处理

OKE能够自动处理以下 3 种形式的章节：
1. 输入文件为 `.m2ts`，且保持了原盘目录结构，OKE 会自动查找对应的 mpls，并提取章节封入成品。
2. 输入文件为 `.mkv`，且其中内封了章节，OKE 会自动提取章节并封入成品。
3. 外挂同名 `.txt` 章节文件，比如输入文件为 `00001.m2ts`，同目录下有同名章节 `00001.txt`，OKE 会自动提取章节并封入成品。

当某些情况同时成立时，外挂章节的优先级更高。

除了以上基础功能，OKE 还支持：指定章节语言、重命名章节标题、根据章节设置关键帧。

### (1). 指定章节语言

默认情况下，OKE 总是设置章节语言为 eng。有时我们会手动填写章节日文标题，此时需要设置语言为 jpn。可以通过给外挂 txt 字幕添加语言后缀来实现，比如输入文件为 `00001.m2ts`，同目录下章节命名为 `00001.jpn.txt`，这样 OKE 就会读取语言标签，并在封装时设置为 jpn。

### (2). 重命名章节标题

对于连体盘，经切割后，除了第一部分，后面部分的章节标题都不是从 `Chapter 01` 开始的。OKE 支持重命名章节标题，通过 `RenumberChapters` 来设置。在设置为 true 时，所给章节会从 `Chapter 01` 开始重新命名。

### (3). 根据章节设置关键帧

OKE 会利用章节在各个章节点处设置关键帧。具体方式为，根据章节确定章节点的帧号，生成 qpfile 给编码器，指定章节点为关键帧。

注意，这个功能会复写 qpfile 参数，因此自己在编码参数中设置的 qpfile 参数实际上无效。由于 qpfile 依赖于章节，需要特别注意章节的正确性，原则上必须在压制前修改章节，而不能在压制后修改。


## 5. VFR功能

OKE 支持动态帧率（VFR）视频的压制。在压制 VFR 时，不再需要指定帧率，但是需要设置 `TimeCode` 为 true 来开启 VFR 功能。

开启 VFR 压制时，OKE 需要获取时间码文件 `.tcfile`，并在封装时写入时间码。与外挂章节文件类似，将时间码文件放到输入文件同目录并改名匹配。比如输入文件为 `00001.m2ts`，同目录下时间码文件命名为 `00001.tcfile`。

事实上，由于 OKE 的压制流程中，在实际压制前会先运行 `vspipe -i` 来获取信息，我们可以在 vpy 脚本中实时生成 tcfile。

```python
#OKE:INPUTFILE
a="00000.m2ts"
...
# VFR splice
import pathlib
path = pathlib.Path(a)
res = mvf.VFRSplice([res_a, res_b], tcfile=str(path.with_suffix('.tcfile')))
```
