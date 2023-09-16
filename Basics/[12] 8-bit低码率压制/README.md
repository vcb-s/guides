# 第十二章 8-bit低码率压制

## 1. 8-bit下的抗色带处理

8-bit 低码率通常用于字幕组内嵌成品的压制，其受众往往对画质要求不高，因此压制重点放在尽可能缩小体积的前提下保留画质。

既然都低码率了，自然码率要花在刀刃上。暗场平面的色带是最容易出现，也最容易被观察到的瑕疵，而 8-bit 下由于精度问题，几乎一定会出现色带，因此抗色带处理是 8-bit 低码率压制中的关键。当然，低码率下纹理和线条也会被涂抹地比较厉害，但一般观众也不容易看出，可以忽略。

之前的章节提过，抗色带的基本手段就是加噪，一个自然的想法是借助 dither 的力量。dither 的算法多种多样，预览效果不错，但编码器往往不吃这套。就算加了高质量 dither，也会被编码器抹掉，还会留下丑陋的噪点尸体。

所以这种情况下，我们只有一种选择，`ordered dither`。ordered dither 虽然丑陋，但是占体积小，并且难以被编码器抹平。如果我们需要把一个 16bit 视频降到 8bit 输出给编码器，可以这样写：

```python
res = mvf.Depth(src16, 8, dither=0, ampo=1.5)
```

mvf 默认用的是 fmtc，可以查看文档。`dither=0`，就是 ordered dither。`ampo` 指定 ordered dither 的静态噪点强度。

<img src="./media/image01 dither.png" />

如果你觉得噪点比较难看，也可以选择加点动噪：
```python
res = mvf.Depth(src16, 8, dither=0, ampo=1.5, ampn=0.5)
```
这里 `ampn` 为随机的动态噪点强度。


到了这一步，我们已经解决了大部分问题，但是注意到，这样全图的 ordered dither 并不是我们想要的。因为人眼只能注意到暗场的色带，亮场就不需要加上 ordered dither，这样可以省去一部分码率。

VS 中提供了一个内置滤镜来根据亮度划分区域，`std.Binarize`。

我们可以使用以下代码来做一个最简单的亮度 mask，将亮度 96 以上的区域置为最大值，而以下的区域置为最小值：
```python
core.std.Binarize(clip, 96, planes=0)
```

于是我们就可以用这样的方法，对亮场做 rounding，对暗场做 ordered dithering。
```python
bright = mvf.Depth(src16, 8, dither=1)
dark = mvf.Depth(src16, 8, dither=0, ampo=1.5)
luma_mask = core.std.Binarize(bright, 96, planes=0)
res = core.std.MaskedMerge(dark, bright, luma_mask, first_plane=True)
```

这里我们小小的引入一点后续章节才会讲到的 mask 内容。我们知道 `std.Merge(clipa, clipb, weight)` 可以根据 weight 融合两个 clip。而如果 weight 不是固定的，而是每个位置的像素都有一个独立的 weight，那么这些所有 weight 也构成一个 clip，这个 clip 就是一个 mask。这样通过一个 mask 来进行 clip 的融合，就是 `std.MaskedMerge(clipa, clipb, mask)` 的功能。

这里使用的 std.Binarize 生成的是最简单的二值化 mask，今后我们还会遇到更复杂的，甚至是连续的 mask，当然这里二值化的 mask 也够用了。


以上就是 8-bit 的抗色带处理，总结来说：
1. 加噪可以一定程度上干扰肉眼辨识色带。
2. 而在码率预算捉襟见肘的情况下，我们为了防止色带出现，会采用 ordered dither 的方法，通过调整 ampo, ampn 来调整 dither 噪点强度，同时辅以 mask 来处理。


## 2. 720p的制作

如果成品是 1080p，那么做完上面的抗色带操作，就可以送入编码器压制了。但有时字幕组也会需要压制 720p 的版本，这时就需要在 VS 中进行 downscale 处理。

在缩小时，为了避免亮度损失问题，需要使用 `gamma-aware downscale`，对 Y 平面转到线性光下缩小。

```python
gray = core.std.ShufflePlanes(src16, 0, colorfamily=vs.GRAY)
gray = core.fmtc.transfer(gray, transs='709', transd='linear', fulls=False, fulld=False)
gray = core.fmtc.resample(gray, 1280, 720)
gray = core.fmtc.transfer(gray, transs='linear', transd='709', fulls=False, fulld=False)
UV = core.fmtc.resample(src16, 1280, 720)
down = core.std.ShufflePlanes([gray,UV], [0,1,2], vs.YUV)
```

这里首先分理出 Y 平面 gray，然后转到线性光，进行缩小。这里缩小使用 fmtc.resample 的默认算法 spline36，非常适合图像缩小。

UV 平面则是将源整体缩小，避免分平面时的 chroma placement 处理。最后合并 Y 和 UV，得到最终缩小后的结果。


## 3. 添加字幕

通常 8-bit 低码率都是字幕组内嵌版本，需要加上字幕。不管先前做过哪些处理，字幕一定要在整个流程的最后加入。字幕滤镜前面章节已经介绍过，这里不再赘述，只提几个实际制作中的要点。

首先是字幕文件名的问题，如果只是压制单集，手动指定不会有太大问题，但如果一季度批量压制，每次改就显得非常繁琐。

一般来说我们利用 OKE 的改名机制，将字幕改为与输入视频同名，只有后缀不同，然后通过以下方式自动替换：

```python
#OKE:INPUTFILE
a = R'00000.mkv'
...
b = a.replace('.mkv','.chs.ass')
res = core.xyvsf.TextSub(res, b)
```

另一个麻烦的问题是字体，在压制前必须保证已经安装所有需要的字体，否则无法正确渲染。通常会使用两个小工具：[FontLoaderSub](https://bbs.acgrip.com/thread-3848-1-1.html) 和 [ListAssFonts](https://bbs.acgrip.com/thread-1894-1-1.html)。

FontLoaderSub 可以分析字幕使用的字体，并临时挂载，避免在系统中安装过多的字体。需要将 FontLoaderSub 放到字体包目录下，第一次运行建立字体数据库，之后拖入字幕即可临时挂载字体。

如下图，[ok] 是加载成功的字体，显示路径说明是临时加载的。

<img src="./media/image02 FontLoaderSub.png" />

点击 `菜单` 按钮，可以选择 `导出字体`，导出所有临时加载的字体到指定目录。注意不能导出系统已经安装的字体。

ListAssFonts 也可以分析字幕使用的字体，但是分析更加精准。FontLoaderSub 会报出定义了样式但实际不使用的字体，而 ListAssFonts 只会给出实际使用的字体。另外，ListAssFonts 还会对字幕格式做一些检查，比如样式的语法、字体是否缺字等。但是注意，ListAssFonts 不能检测出 FontLoaderSub 临时挂载的字体，会认为它们缺失。

如下图，黑色是系统已有的字体，红色是缺少的字体。

<img src="./media/image03 ListAssFonts.png" />

勾选 `Save Fonts`，并选择 `Select ASS/SSA Folder` 中指定目录，可以导出系统已经安装的字体。

通过这俩配合，就能导出所有安装和未安装的字体，这在没有字体包时候会非常有用。

当然，和字幕组合作时，对方都会给出字体包，可以用 FontLoaderSub 临时挂载，或者直接安装，但无论使用哪种都需要验证压制之前已经安装/挂载好所有需要的字体。


## 4. 压制参数

8-bit 低码率通常定位都是兼容移动端的，因此使用 x264 来编码。另一方面，x265-8bit 表现实在太差，没有使用价值，都用 hevc 了，还是 10-bit 吧。

8-bit 低码率需要注意这样几个参数：

`--fgo 1或者2`
当然，这里的 fgo 不是你想的那个 fgo，它其实是 film grain optimization，可以把码率暴力分配给噪点。
`--psy-trellis 0.2~0.3`
就是 --psy-rd 的第二个参数，效果与 fgo 类似。

`--psy-rd 0`
这时候别用 psy-rd 了，这东西是会“保留复杂度”而不是“保留噪点”，它会把噪点搅拌压碎，很难看。
`--qcomp 0.7`
这个不给高的话，动态和一些静止场面会比较难看，也可以关闭 mbtree 来代替。

给一个参考编码参数：
```
--preset veryslow --crf 18 --threads 16 --deblock -1:-1 --keyint 600 --min-keyint 1 --bframes 8 --ref 4 --qcomp 0.6 --no-mbtree --rc-lookahead 70 --aq-strength 0.8 --me tesa --psy-rd 0:0 --chroma-qp-offset -1 --fgo 1 --no-fast-pskip --aq-mode 3 --colorprim bt709 --transfer bt709 --colormatrix bt709 --chromaloc 0 --range tv
```

注意这里用了 `--fgo 1, --psy-rd 0:0, --no-mbtree`。当然这里还有一些可以改进的地方，在低码率下，可以适当开启 `deblock`，开到 `0:-1` 或者 `0:0` 都可以。`--keyint 600` 其实稍微有点大，最大约为 25s 一个关键帧，对于静态镜头较多的番拖进度会比较困难，可以减少到 360 甚至 240 比较合适。`--crf 18` 可以根据番剧实际情况，调整到 18~21 左右都行。
