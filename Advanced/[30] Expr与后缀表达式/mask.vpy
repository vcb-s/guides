import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

# 0-719 720-1919
# 0-1199 1200-1919
# (689,0) (1169,1080) 2.25 * X - Y = 1550.25
# (750,0) (1230,1080) 2.25 * X - Y = 1687.5

src_y = core.std.ShufflePlanes(src, 0, vs.GRAY)
res = core.akarin.Expr(src_y, "2.25 X * Y - tmp! tmp@ 1550.25 <= 65535 tmp@ 1687.5 >= 0 tmp@ 1550.25 - 137.25 / 1 swap - 65535 * ? ?", format=vs.GRAY16)

res.set_output(0)
src.set_output(1)