import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src8 = core.lsmas.LWLibavSource(a)

res = core.akarin.Expr(src8, ["x 10 +", "x 128 - 1.1 * 128 +"])

res.set_output(0)
src8.set_output(1)