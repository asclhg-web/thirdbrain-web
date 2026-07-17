"""T21 헬스체크 — GPU 컨테이너/호스트에서 실행: python3 docker/healthcheck_gpu.py"""
import shutil
import subprocess


def main():
    checks = []
    smi = shutil.which("nvidia-smi")
    checks.append(("nvidia-smi", bool(smi)))
    if smi:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True, text=True)
        print("GPU:", out.stdout.strip())
    try:
        import torch  # noqa
        checks.append(("torch", True))
        checks.append(("torch.cuda", torch.cuda.is_available()))
    except ImportError:
        checks.append(("torch", False))
    for name, ok in checks:
        print(("✅" if ok else "❌"), name)
    return all(ok for _, ok in checks)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
