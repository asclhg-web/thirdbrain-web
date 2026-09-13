# 이미 만든 seg01..seg16.mp4 → 단일 패스 xfade 체인으로 부드럽게 이어붙이고 정규화
import subprocess
from pathlib import Path

SP = Path(__file__).parent
AV = SP / "deck_video" / "av"
X = 0.5
segs = sorted(AV.glob("seg*.mp4"))
assert len(segs) == 16, len(segs)

def probe(f):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nk=1:nw=1", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())

durs = [probe(s) for s in segs]
inputs = []
for s in segs:
    inputs += ["-i", str(s)]

# 비디오 xfade 체인
vf = []
prev = "[0:v]"
cum = durs[0]
for j in range(1, len(segs)):
    off = cum - X
    out = f"[v{j}]"
    vf.append(f"{prev}[{j}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{out}")
    prev = out
    cum = cum + durs[j] - X
vlast = prev
# 오디오 acrossfade 체인
af = []
prevA = "[0:a]"
for j in range(1, len(segs)):
    out = f"[a{j}]"
    af.append(f"{prevA}[{j}:a]acrossfade=d={X}{out}")
    prevA = out
alast = prevA
# 라우드니스 정규화를 복합 필터 안에서 처리(‑af와 복합필터 병용 불가)
af.append(f"{alast}loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
alast = "[aout]"

fc = ";".join(vf + af)
final = SP / "deck_video" / "AX_구축_플랫폼_발표영상.mp4"
cmd = ["ffmpeg","-y","-loglevel","error", *inputs,
    "-filter_complex", fc,
    "-map", vlast, "-map", alast,
    "-c:v","libx264","-pix_fmt","yuv420p","-r","25","-preset","veryfast",
    "-c:a","aac","-b:a","192k",
    str(final)]
print("total video ~", round(cum/60, 2), "min; encoding...")
subprocess.run(cmd, check=True)
print("DONE", final, final.stat().st_size // 1024, "KB")
