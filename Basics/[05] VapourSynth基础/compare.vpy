import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"D:\VCB-Studio Entry Test 2023\Q4 [E46686C4].m2ts"
src8 = core.lsmas.LWLibavSource(a)
src8 = mvf.Preview(src8)
src8.set_output(0)

b = R"D:\VCB-Studio Entry Test 2023\Q4_AV1 [41A7EDDA].mkv"
rip = core.lsmas.LWLibavSource(b)
rip = mvf.Preview(rip)
rip.set_output(1)