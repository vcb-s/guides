import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

mask = core.tcanny.TCanny(src, sigma=4.5, planes=[0])
mask = core.std.Expr(mask, ['', '128', '128'])

mask.set_output(0)
src.set_output(1)