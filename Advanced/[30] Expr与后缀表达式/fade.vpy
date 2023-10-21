import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

src_a = src
src_b = src
n = 48

src_a_end = src_a[-n:]
src_b_begin = src_b[:n]

fade = core.akarin.Expr([src_a_end, src_b_begin], f"N {n-1} / y * 1 N {n-1} / - x * +")

res = src_a[:-n] + fade + src_b[n:]

fade.set_output(0)
src_a_end.set_output(1)
src_b_begin.set_output(2)
res.set_output(3)