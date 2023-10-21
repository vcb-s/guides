import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

left = 480
right = 1920 - 480
top = 270
bottom = 1080 - 270
res = core.akarin.Expr(src, [f"X {left} >= X {right} < and Y {top} >= and Y {bottom} < and 65535 0 ?", f"X {left // 2} >= X {right // 2} < and Y {top // 2} >= and Y {bottom // 2} < and 65535 0 ?"], format=vs.YUV420P16)

res.set_output(0)
src.set_output(1)