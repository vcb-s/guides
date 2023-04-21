import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

matrix_1 = [0, 1, 0,  1, -4, 1,  0, 1, 0]
res_1 = core.std.Convolution(src, matrix_1, saturate=True)

matrix_2 = [1, 1, 1,  1, -8, 1,  1, 1, 1]
res_2 = core.std.Convolution(src, matrix_2, saturate=True)

res_1.set_output(1)
res_2.set_output(2)
src.set_output(3)
core.std.Convolution(src, [0, -1, 0,  -1, 5, -1,  0, -1, 0], saturate=True).set_output(4)