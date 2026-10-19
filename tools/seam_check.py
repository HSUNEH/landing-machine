"""이음새 검사: 생성된 클립의 첫/끝 프레임이 입력 스틸(first_frame/last_frame)에 붙었는지 본다.

usage: python3 tools/seam_check.py <clip.mp4> <first.png> [<last.png>]

- 스틸은 클립 해상도로 cover-fit(중앙 크롭) 후 비교한다. 출력이 정확한 16:9가 아닐 수 있어서
  (Seedance 480p = 864x496) 늘려서 비교하면 수치가 10dB 가까이 떨어진다.
- 기준: 첫 프레임 >= 30dB면 고정. 끝 프레임은 ~28dB 이상이면 같은 구도로 착지(크로스페이드가 나머지를 덮는다).
  PSNR은 보조 지표이고 최종 판단은 구도 육안 비교다(docs/refs/scroll-world.md §7).
- 첫/끝 프레임 PNG를 클립 옆에 <clip>_f0.png / <clip>_fN.png 로 남긴다 → 다음 레그/커넥터 입력으로 쓴다.
"""
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat


def ffmpeg(*args):
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("ffmpeg not found on PATH (brew install ffmpeg)")
    subprocess.run([exe, "-v", "error", "-y", *args], check=True)


def psnr(a, b):
    sq = ImageStat.Stat(ImageChops.difference(a, b)).sum2
    mse = sum(sq) / (a.size[0] * a.size[1] * 3)
    return 99.0 if mse == 0 else 10 * math.log10(255**2 / mse)


def main():
    clip = Path(sys.argv[1])
    first = Path(sys.argv[2])
    last = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    f0 = clip.with_name(clip.stem + "_f0.png")
    fn = clip.with_name(clip.stem + "_fN.png")
    ffmpeg("-i", str(clip), "-frames:v", "1", str(f0))
    ffmpeg("-sseof", "-0.1", "-i", str(clip), "-update", "1", "-frames:v", "1", str(fn))

    a0 = Image.open(f0).convert("RGB")
    an = Image.open(fn).convert("RGB")
    fit = lambda p: ImageOps.fit(Image.open(p).convert("RGB"), a0.size, Image.LANCZOS)

    s_first = fit(first)
    print(f"size {a0.size[0]}x{a0.size[1]}")
    print(f"frame0 ~ first : {psnr(a0, s_first):5.1f} dB")
    if last:
        print(f"frameN ~ last  : {psnr(an, fit(last)):5.1f} dB")
    print(f"frameN ~ first : {psnr(an, s_first):5.1f} dB (control)")
    print(f"wrote {f0.name}, {fn.name}")


if __name__ == "__main__":
    main()
