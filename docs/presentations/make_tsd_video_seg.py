# 베이커리 T사 통합 발표영상 — 슬라이드 프레임 + 아나운서 TTS(문장별·쉼표 미세 쉼) → 슬라이드별 seg
import json, re, subprocess, wave, struct
from pathlib import Path
import sherpa_onnx

SP = Path(__file__).parent
FR = SP / "tsd_video" / "frames"
AV = SP / "tsd_video" / "av"; AV.mkdir(parents=True, exist_ok=True)
MODEL = SP / "tts-model"
SR=None; SPEED=0.94; SENT_GAP=0.42; COMMA_GAP=0.16; FADE_MS=14; TAIL=1.1
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=str(MODEL/"ko_KO-kss_low.onnx"), tokens=str(MODEL/"tokens.txt"),
            data_dir=str(MODEL/"espeak-ng-data")), num_threads=4), max_num_sentences=1))

def fade(x,sr):
    n=int(sr*FADE_MS/1000); L=len(x)
    for i in range(min(n,L)): x[i]*=i/n; x[L-1-i]*=i/n
    return x

def synth(text,out):
    global SR; pcm=[]
    for s in [s.strip() for s in re.split(r"(?<=[.?!])\s+",text) if s.strip()]:
        parts=[x.strip() for x in re.split(r"(?<=[,·])\s*",s) if x.strip()]
        for j,part in enumerate(parts):
            a=tts.generate(part,sid=0,speed=SPEED); SR=a.sample_rate
            pcm.extend(fade(list(a.samples),SR))
            if j<len(parts)-1: pcm.extend([0.0]*int(SR*COMMA_GAP))
        pcm.extend([0.0]*int(SR*SENT_GAP))
    with wave.open(str(out),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h",max(-32767,min(32767,int(v*32767)))) for v in pcm))
    return len(pcm)/SR

NARR=json.loads((SP/"tsd_narration.json").read_text())
frames=sorted(FR.glob("f-*.png"))
assert len(frames)==len(NARR), f"{len(frames)} vs {len(NARR)}"
total=0
for sc,png in zip(NARR,frames):
    n=sc["n"]; wav=AV/f"n{n:02d}.wav"; dur=synth(sc["text"],wav); total+=dur
    seg=AV/f"seg{n:02d}.mp4"; pad=TAIL+(0.8 if n in (1,len(NARR)) else 0.0)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(png),"-i",str(wav),
        "-c:v","libx264","-tune","stillimage","-pix_fmt","yuv420p","-r","25",
        "-vf","scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:a","aac","-b:a","192k","-ar",str(SR),"-af",f"apad=pad_dur={pad}","-shortest",str(seg)],check=True)
    print(f"slide {n}: {dur:.1f}s")
print(f"SEGS DONE total {total/60:.1f}min")
