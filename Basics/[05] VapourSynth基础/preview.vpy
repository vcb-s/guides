import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = "00010.m2ts"
src8 = core.lsmas.LWLibavSource(a)
src8.set_output()