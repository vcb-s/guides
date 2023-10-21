import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

ref = core.rgvs.RemoveGrain(src, 20)

matrix = [f'x[{x},{y}] ' for x in range(-1, 2) for y in range(-1, 2)]

res = core.akarin.Expr(src, f"{''.join(matrix)} " + "+ " * 8 + "9 /")
print(f"{''.join(matrix)} " + "+ " * 8 + "9 /")

cmp = core.akarin.Expr([res, ref], "x y = 255 0 ?", format=vs.YUV420P8)

res.set_output(0)
src.set_output(1)
cmp.set_output(2)