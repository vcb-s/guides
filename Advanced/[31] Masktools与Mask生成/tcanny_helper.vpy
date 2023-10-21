import vapoursynth as vs
from vapoursynth import core
import havsfunc as haf
import mvsfunc as mvf

a = R"E:\BDMV\[BDMV] BOCCHI THE ROCK\ぼっち・ざ・ろっく！ vol.1\BD\BDMV\STREAM\00004.m2ts"
src = core.lsmas.LWLibavSource(a)

def TCannyHelper(clip, sigma=1.5, t_h=8.0, t_l=1.0, op=2, plane=0):
    bits = clip.format.bits_per_sample
    neutral = 2 ** (bits - 1)
    peak = (2 ** bits) - 1

    clip = mvf.GetPlane(clip, plane)

    mask_big = core.tcanny.TCanny(clip, sigma=sigma, t_h=t_l+1e-4, t_l=t_l, op=op)
    mask_small = core.tcanny.TCanny(clip, sigma=sigma, t_h=t_h+1e-4, t_l=t_h, op=op)

    mask = core.akarin.Expr([mask_big, mask_small], f"x {peak} = {neutral} 0 ? mask_l! y {peak} = {peak} mask_l@ ?")

    return mask

mask = TCannyHelper(src, sigma=1.5, t_h=8.0, t_l=1.0)
mask_res = core.tcanny.TCanny(src, sigma=1.5, t_h=8.0, t_l=1.0, op=2, planes=[0])

mask.set_output(0)
mvf.GetPlane(mask_res, 0).set_output(1)
src.set_output(2)