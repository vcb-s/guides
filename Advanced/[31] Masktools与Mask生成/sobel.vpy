import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

matrix_x = [-1, 0, 1,  -2, 0, 2,  -1, 0, 1]
res_x = core.std.Convolution(src, matrix_x, saturate=False)

matrix_y = [-1, -2, -1,  0, 0, 0,  1, 2, 1]
res_y = core.std.Convolution(src, matrix_y, saturate=False)

res = core.akarin.Expr([res_x, res_y], "x y +")

sobel = core.std.Sobel(src)

res.set_output(0)
res_x.set_output(1)
res_y.set_output(2)
src.set_output(3)
sobel.set_output(4)