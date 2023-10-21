import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

res = core.akarin.Expr(src, ["X 235 256 * 16 256 * - width / * 16 256 * +", "X 240 256 * 16 256 * - width / * 16 256 * +"], format=vs.YUV420P16)

res.set_output(0)
res.std.ShufflePlanes(0, vs.GRAY).set_output(1)