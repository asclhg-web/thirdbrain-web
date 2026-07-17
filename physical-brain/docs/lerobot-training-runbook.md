# LeRobot 학습 런북 (T24) — GPU 서버 도착 즉시 실행

전제: `bash docker/gpu-setup.sh` 전 항목 ✅, LeKiwi 조립 완료(책 15장),
데이터셋 스펙은 `docs/dataset-spec.md`.

## 0. 환경 (최초 1회, ~20분)

```bash
# 전용 콘다 환경 (도커보다 텔레옵 장치 접근이 단순)
conda create -y -n lerobot python=3.10 && conda activate lerobot
git clone https://github.com/huggingface/lerobot.git && cd lerobot
pip install -e ".[feetech]"        # SO-101/LeKiwi 서보 지원
python -c "import torch; print(torch.cuda.is_available())"   # True 확인
```

## 1. 텔레옵 점검 (10분)

```bash
python -m lerobot.teleoperate \
  --robot.type=lekiwi --robot.port=/dev/ttyACM0 \
  --teleop.type=so101_leader --teleop.port=/dev/ttyACM1
```
리더암을 움직여 팔로워가 따라오면 OK. 포트는 `ls /dev/ttyACM*`로 확인.

## 2. 데이터 수집 (스킬당 반나절)

```bash
python -m lerobot.record \
  --robot.type=lekiwi --robot.port=/dev/ttyACM0 \
  --teleop.type=so101_leader --teleop.port=/dev/ttyACM1 \
  --dataset.repo_id=$USER/pb_pick_pillbox_v1 \
  --dataset.num_episodes=50 --dataset.fps=30 \
  --dataset.single_task="약 선반에서 약통을 집는다"
```
수집 직후 `docs/dataset-spec.md`의 품질 체크리스트 수행.

## 3. 학습 (RTX 4090 기준 스킬당 3~6시간)

```bash
python -m lerobot.scripts.train \
  --dataset.repo_id=$USER/pb_pick_pillbox_v1 \
  --policy.type=act --output_dir=outputs/pick_pillbox_v1 \
  --steps=100000 --batch_size=8
# 모니터링: 별도 셸에서 nvidia-smi -l 5 / wandb(선택)
```

## 4. 평가 → 합격 기준

```bash
python -m lerobot.record \
  --robot.type=lekiwi --robot.port=/dev/ttyACM0 \
  --policy.path=outputs/pick_pillbox_v1/checkpoints/last/pretrained_model \
  --dataset.repo_id=$USER/eval_pick_pillbox_v1 --dataset.num_episodes=10
```
- 합격: 10회 중 8회 이상 성공(스펙의 성공 판정 기준). 미달이면 데이터 +50 에피소드 후 재학습.

## 5. 앱 연동 — 정책 실행 노드

로봇(젯슨/서버)에서 `pb/cmd/#`를 구독해 학습된 정책을 실행하고 결과를 회신:
`robot/fake_robot.py`의 `_work()`에서 `time.sleep` 자리를
`policy.select_action()` 루프로 바꾸면 그대로 실물 노드가 된다
(토픽 규약: `docs/robot-adapter-v1.md`). 브로커는 mosquitto:

```bash
sudo apt install -y mosquitto && pip install paho-mqtt
```

## 부록 — 자연스러운 한국어 TTS (음성 클라이언트용)

```bash
pip install piper-tts
# 한국어 모델 1회 다운로드 후:
echo "약 드실 시간이에요" | piper -m ko_KR-...-medium.onnx -f out.wav && aplay out.wav
```
`robot/voice_client.py`의 `tts()`에서 espeak-ng 대신 piper 호출로 교체 가능.
