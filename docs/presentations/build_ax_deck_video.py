# AX 구축 플랫폼 발표 데모 영상 — 덱 16장 + 아나운서 내레이션(부드러운 편집)
# 슬라이드 PNG(1920x1080) + 문장별 TTS(쉼표 미세 쉼·문장 간격·페이드) → 슬라이드별 mp4
# → 크로스페이드 전환으로 이어붙이고 라우드니스 정규화.
import json, re, subprocess, wave, struct
from pathlib import Path
import sherpa_onnx

SP = Path(__file__).parent
FR = SP / "deck_video" / "frames"
AV = SP / "deck_video" / "av"
AV.mkdir(parents=True, exist_ok=True)
MODEL = SP / "tts-model"
SR = None
SPEED = 0.94          # 조금 느리게 — 아나운서 톤
SENT_GAP = 0.42       # 문장 사이 무음(초)
COMMA_GAP = 0.16      # 쉼표 뒤 미세 쉼(초)
FADE_MS = 14          # 문장 경계 페이드(ms)
XFADE = 0.5           # 슬라이드 전환 크로스페이드(초)
TAIL = 1.1            # 내레이션 끝 여운(초)

tts = sherpa_onnx.OfflineTts(
    sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=str(MODEL / "ko_KO-kss_low.onnx"),
                tokens=str(MODEL / "tokens.txt"),
                data_dir=str(MODEL / "espeak-ng-data"),
            ),
            num_threads=4,
        ),
        max_num_sentences=1,
    )
)

def fade(samples, sr):
    n = int(sr * FADE_MS / 1000); L = len(samples)
    for i in range(min(n, L)):
        samples[i] *= i / n; samples[L-1-i] *= i / n
    return samples

def synth(text, out_wav):
    """문장 단위로 합성하되, 쉼표에서 짧은 쉼을 넣어 낭독이 부드럽게 이어지게."""
    global SR
    pcm = []
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]
    for s in sents:
        # 쉼표/가운뎃점으로 끊어 각 조각을 합성 → 조각 사이 미세 쉼
        parts = [x.strip() for x in re.split(r"(?<=[,·])\s*", s) if x.strip()]
        for j, part in enumerate(parts):
            a = tts.generate(part, sid=0, speed=SPEED)
            SR = a.sample_rate
            pcm.extend(fade(list(a.samples), SR))
            if j < len(parts) - 1:
                pcm.extend([0.0] * int(SR * COMMA_GAP))
        pcm.extend([0.0] * int(SR * SENT_GAP))
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(x*32767)))) for x in pcm))
    return len(pcm) / SR

# 슬라이드별 내레이션 (아나운서 톤 — 부드럽게 이어지도록 쉼표를 살림)
NARR = [
 # 1 타이틀
 "안녕하십니까. 에이엑스 구축 플랫폼, 근거 있는 판단의 공장을 소개하겠습니다. "
 "이 시스템은 데이터가 모이고, 인공지능이 근거와 함께 제안하고, 사람이 승인하면, 시스템이 그대로 기록하는 구조로 만들어졌습니다. "
 "지금 서버1에서 이십사 시간 운영되고, 오두아이이알피 닷컴으로 공개되어 있으며, 서술은 클로드 오퍼스가 맡고 있습니다.",
 # 2 문제의식
 "왜 에이엑스인가. 대부분의 현장에는 데이터가 이미 충분히 있습니다. "
 "다만 엑셀과 포스, 장부와 오두 전산에 흩어져 한곳에 서지 못하고, 결정은 여전히 경험과 직관에 기대며, 대시보드는 숫자만 보여줄 뿐 왜와 무엇을 할지를 말해 주지 않습니다. "
 "그리고 담당자의 노하우는 조직의 자산으로 남지 않습니다. 이 네 가지 문제를 정면으로 다룹니다.",
 # 3 흐름
 "시스템의 흐름은 한 줄입니다. 엑셀과 장부, 오두의 데이터가 표준 데이터셋으로 모이고, 분석과 예측을 거쳐 지식그래프에 의미로 쌓이면, 인공지능이 판단 카드를 만들어 사람에게 승인을 요청합니다. "
 "제안은 인공지능이 하지만, 결정은 언제나 사람이 합니다. 승인하는 순간에만 시스템 값이 바뀌고, 전 과정이 감사 기록으로 남습니다.",
 # 4 아키텍처
 "구성은 엠제로부터 엠세븐까지 여덟 개 모듈과, 프로젝트 케이피아이 센터로 이루어집니다. "
 "수집과 표준화, 분석과 학습, 지식그래프와 엘엘엠 판단, 그리고 에이전트 관제까지. "
 "핵심 엔진과 보안은 그대로 두고, 화면 계층만 최근에 더 쉽게 재편했습니다.",
 # 5 차별점
 "이 플랫폼의 본질은 예쁜 대시보드가 아니라 근거의 공장이라는 점입니다. "
 "첫째, 화면의 모든 수치와 주장에 근거 출처가 붙고, 인용 없는 문장은 시스템이 차단합니다. "
 "둘째, 인공지능은 숫자를 만들지 못합니다. 수치는 그래프와 측정 엔진이 계산하고, 엘엘엠은 서술만 합니다. "
 "셋째, 결정은 언제나 사람이 합니다. 권한은 문서가 아니라 구조가 지킵니다.",
 # 6 오늘
 "이제 실제 화면을 보시겠습니다. 로그인하면 역할에 맞는 오늘 화면이 열립니다. "
 "승인을 기다리는 카드, 확인할 이름, 목표에 못 미친 케이피아이가 할 일 카드로 모이고, 하나를 누르면 바로 그 화면으로 이동합니다. 무엇이든 물어보는 질문창은 늘 열려 있습니다.",
 # 7 승인함
 "핵심은 승인함입니다. 인공지능 에이전트들이 만든 오늘의 제안이 카드로 기다립니다. "
 "카드마다 제안 수치와 예측 구간, 왜 그런지의 근거, 그리고 채택하지 않은 대안까지 한 장에 담겨 있습니다. "
 "왜 버튼을 누르면 원장 기록까지 근거를 따라 내려갈 수 있고, 승인하면 감사 로그와 파라미터에 그대로 기록됩니다.",
 # 8 KPI
 "성과는 프로젝트 케이피아이 화면에서 관리합니다. 프로젝트마다 목표와 기준선을 정하면, 야간 배치가 자동으로 측정을 누적하고, 지금 측정 버튼으로 즉시 갱신할 수도 있습니다. "
 "아직 데이터가 쌓이지 않은 지표는 정직하게 측정 전이라고 표시합니다. 지어낸 숫자는 없습니다.",
 # 9 질문
 "이번 주 폐기율이 왜 올랐는지, 자연어로 물으면 시스템이 답합니다. "
 "서술은 클로드 오퍼스가 맡지만, 수치는 반드시 그래프에서 가져오며, 모든 답변 문장에 근거가 인용됩니다. 근거 없는 대답은 나오지 않습니다.",
 # 10 업로드
 "자료 반입은 형식 그대로 올리면 됩니다. 엑셀이나 포스 파일을 올리면, 업로드, 매핑, 확인할 이름, 반영의 네 단계로 표준 데이터에 도달합니다. "
 "처음 보는 양식이라도 화면에서 직접 매핑할 수 있습니다.",
 # 11 여정
 "여기까지 오기 위한 구축 여정입니다. 이중 데이터베이스와 웹앱에서 시작해, 실제 오두 결선, 공개 서비스화, 보안과 정합, 유료 준비, 프로젝트 케이피아이, 화면 재구성, 그리고 시각 디자인까지. "
 "각 단계는 구현하고, 양쪽 데이터베이스에서 시험하고, 커밋하는 것으로 마무리했습니다. 실사용에서 나온 문제는 번호를 붙여 기록하고 고쳤습니다.",
 # 12 벤치마킹
 "벤치마킹도 정직하게 했습니다. 오두의 승인 워크플로, 삼성에스디에스의 대규모 에이아이, 팔란티어의 온톨로지와 근거 추적, 파워비아이의 자연어 질문. "
 "성공한 제품의 화면 문법은 흡수하되, 근거 강제와 수치 생성 금지, 그리고 사람의 결정이라는 원칙은 코어로 지켰습니다. 이것이 본질적인 차이입니다.",
 # 13 라이브
 "그리고 가장 중요한 것. 이 시스템은 지금 살아 있습니다. "
 "서버1에서 이십사 시간 가동되고, 오두아이이알피 닷컴으로 공개되어 폰으로도 접속이 확인되었습니다. 서술은 클로드 오퍼스로 전환했고, 복제 정합은 쉰두 사이클 무결하며, 테스트는 백사십구 건이 통과합니다. "
 "남은 것은 규모의 문제이지, 구축의 문제가 아닙니다.",
 # 14 디자인
 "화면은 더 쉽고 아름답게 다듬었습니다. 열네 개의 평면 메뉴를 네 개의 허브로 묶고, 역할별 홈과 할 일 중심으로 바꾸었으며, 디자인 토큰과 부드러운 그림자를 입혔습니다. "
 "모바일에서도 탭과 표가 편하도록 최적화해, 폰으로 승인하는 실사용 수준에 이르렀습니다.",
 # 15 로드맵
 "다음 단계는 분명합니다. 오두 읽기 전용 접속과 이십사 개월 판매 엑셀, 이 두 가지면 실데이터 온보딩이 시작됩니다. "
 "십이 주의 파일럿에서 결품과 폐기가 함께 줄어드는 것을 숫자로 보여드리고, 이후 유료 단계로 넘어갑니다. 모든 산출물은 고객의 자산으로 남습니다.",
 # 16 클로징
 "정리하겠습니다. 문서에 있으면 사람이 지켜야 하지만, 플랫폼이 되면 구조가 지킵니다. "
 "에이엑스 구축 플랫폼은 만들었다를 넘어, 실제로 운영되고 공개되고 측정되는 단계에 도달했습니다. 들어주셔서 감사합니다.",
]

frames = sorted(FR.glob("f-*.png"))
assert len(frames) == len(NARR), f"frames {len(frames)} vs narr {len(NARR)}"
segs = []; total = 0.0
for i, (png, text) in enumerate(zip(frames, NARR), 1):
    wav = AV / f"n{i:02d}.wav"
    dur = synth(text, wav); total += dur
    seg = AV / f"seg{i:02d}.mp4"
    pad = TAIL + (0.8 if i in (1, len(frames)) else 0.0)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", str(png), "-i", str(wav),
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "25",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-af", f"apad=pad_dur={pad}", "-shortest", str(seg)], check=True)
    segs.append(seg)
    print(f"slide {i}: {dur:.1f}s")

# 크로스페이드 전환으로 이어붙이기 (부드러운 편집)
def probe(f):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nk=1:nw=1", str(f)], capture_output=True, text=True)
    return float(r.stdout.strip())

durs = [probe(s) for s in segs]
cur = str(segs[0]); off = durs[0]
for i in range(1, len(segs)):
    out = AV / f"acc{i:02d}.mp4"
    off_v = max(0.05, off - XFADE)
    subprocess.run([
        "ffmpeg","-y","-loglevel","error","-i",cur,"-i",str(segs[i]),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={XFADE}:offset={off_v:.3f}[v];"
        f"[0:a][1:a]acrossfade=d={XFADE}[a]",
        "-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-r","25",
        "-c:a","aac","-b:a","192k", str(out)], check=True)
    cur = str(out); off = off + durs[i] - XFADE

final = SP / "deck_video" / "AX_구축_플랫폼_발표영상.mp4"
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",cur,
    "-c:v","copy","-c:a","aac","-b:a","192k",
    "-af","loudnorm=I=-16:TP=-1.5:LRA=11", str(final)], check=True)
print(f"완료 → {final}  (내레이션 합계 {total/60:.1f}분, 전환 포함 총 {off/60:.1f}분)")
