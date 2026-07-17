"""T23 — 음성 대화 클라이언트 (푸시투토크).

흐름: [Enter] 녹음 → STT(faster-whisper 서버) → /api/ask(사서) → TTS 발화
각 단계 지연(ms)을 로그로 남긴다. 목표: 왕복 3초 이내(GPU 서버 기준).

사용:
  python3 -m robot.voice_client            # 마이크 푸시투토크 (GPU 서버)
  python3 -m robot.voice_client --text     # 타자 모드 (마이크 없는 환경 검증용)

환경변수: STT_BASE_URL(기본 http://localhost:8801/v1), APP_URL(기본 http://localhost:8800)
TTS 우선순위(D-07 확정): piper(자연스러운 한국어, PIPER_MODEL 필요) → espeak-ng → 텍스트만.
STT 모델(D-08 확정): 기본 medium — 어르신 발화 인식률 우선, GPU에서 1초 안쪽.
"""
import argparse
import io
import os
import shutil
import subprocess
import time

import requests

STT_BASE = os.getenv("STT_BASE_URL", "http://localhost:8801/v1")
APP_URL = os.getenv("APP_URL", "http://localhost:8800")
RECORD_S = int(os.getenv("RECORD_SECONDS", "5"))


def record_wav(seconds: int = RECORD_S) -> bytes:
    """마이크에서 seconds초 녹음 → WAV 바이트. sounddevice 필요(GPU 서버: pip install sounddevice)."""
    import numpy as np
    import sounddevice as sd
    import wave

    sr = 16000
    print(f"🎙  {seconds}초 녹음 중...")
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="int16")
    sd.wait()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.asarray(audio).tobytes())
    return buf.getvalue()


def stt(wav: bytes) -> str:
    """OpenAI 호환 STT(faster-whisper-server, docker compose --profile gpu)."""
    r = requests.post(f"{STT_BASE}/audio/transcriptions",
                      files={"file": ("q.wav", wav, "audio/wav")},
                      data={"model": os.getenv("STT_MODEL", "Systran/faster-whisper-medium"),
                            "language": "ko"}, timeout=60)
    r.raise_for_status()
    return r.json().get("text", "").strip()


def ask(question: str) -> str:
    r = requests.post(f"{APP_URL}/api/ask", json={"question": question}, timeout=120)
    r.raise_for_status()
    return r.json().get("answer", "")


def tts(text: str) -> str:
    """발화. piper(PIPER_MODEL 설정 시) → espeak-ng → 텍스트만 (D-07: piper 확정)."""
    model = os.getenv("PIPER_MODEL", "")
    if model and shutil.which("piper"):
        wav = "/tmp/pb_tts.wav"
        subprocess.run(["piper", "-m", model, "-f", wav],
                       input=text.encode("utf-8"), capture_output=True)
        subprocess.run(["aplay", "-q", wav], capture_output=True)
        return "piper"
    if shutil.which("espeak-ng"):
        subprocess.run(["espeak-ng", "-v", "ko", "-s", "150", text],
                       capture_output=True)
        return "espeak-ng"
    return "text-only"


def one_turn(question: str | None = None) -> dict:
    """한 번의 대화 왕복. question이 None이면 마이크 녹음→STT."""
    lat = {}
    if question is None:
        t0 = time.time()
        wav = record_wav()
        lat["record_ms"] = int((time.time() - t0) * 1000)
        t0 = time.time()
        question = stt(wav)
        lat["stt_ms"] = int((time.time() - t0) * 1000)
        print(f"👂 인식: {question}")
    t0 = time.time()
    answer = ask(question)
    lat["ask_ms"] = int((time.time() - t0) * 1000)
    t0 = time.time()
    engine = tts(answer)
    lat["tts_ms"] = int((time.time() - t0) * 1000)
    total = sum(lat.values())
    print(f"🤖 {answer}")
    print(f"   ⏱ {lat} 합계 {total}ms (TTS: {engine})")
    return {"question": question, "answer": answer, "latency": lat}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", action="store_true", help="타자 모드(마이크/STT 생략)")
    args = ap.parse_args()
    mode = "타자" if args.text else "푸시투토크"
    print(f"피지컬브레인 음성 클라이언트 — {mode} 모드. 빈 입력이면 종료.")
    while True:
        if args.text:
            q = input("나> ").strip()
            if not q:
                break
            one_turn(q)
        else:
            if input("[Enter]=녹음 시작, q=종료 > ").strip() == "q":
                break
            one_turn(None)


if __name__ == "__main__":
    main()
