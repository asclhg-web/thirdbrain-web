# seg01..seg20 → 단일 패스 xfade 체인 + loudnorm → 최종 mp4
import subprocess
from pathlib import Path
SP=Path(__file__).parent; AV=SP/"final_video"/"av"; X=0.5
segs=sorted(AV.glob("seg*.mp4")); assert len(segs)==20, len(segs)
def probe(f):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(f)],capture_output=True,text=True)
    return float(r.stdout.strip())
durs=[probe(s) for s in segs]
inputs=[]; [inputs.extend(["-i",str(s)]) for s in segs]
vf=[]; prev="[0:v]"; cum=durs[0]
for j in range(1,len(segs)):
    out=f"[v{j}]"; vf.append(f"{prev}[{j}:v]xfade=transition=fade:duration={X}:offset={cum-X:.3f}{out}")
    prev=out; cum=cum+durs[j]-X
vlast=prev
af=[]; prevA="[0:a]"
for j in range(1,len(segs)):
    out=f"[a{j}]"; af.append(f"{prevA}[{j}:a]acrossfade=d={X}{out}"); prevA=out
af.append(f"{prevA}loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
fc=";".join(vf+af)
final=SP/"final_video"/"AX_플랫폼_최종_발표영상.mp4"
print("total ~",round(cum/60,2),"min; encoding...")
subprocess.run(["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",fc,
    "-map",vlast,"-map","[aout]","-c:v","libx264","-pix_fmt","yuv420p","-r","25","-preset","veryfast",
    "-c:a","aac","-b:a","192k",str(final)],check=True)
print("DONE",final,final.stat().st_size//1024,"KB")
