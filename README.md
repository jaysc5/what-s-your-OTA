# 📡 What's Your OTA?

SSAFY 13기 1학기 서울 19반 임베디드 관통 프로젝트  
Raspberry Pi 기반 자율주행 차량에 OTA(Over-The-Air) 업데이트 기능을 적용한 인포테인먼트 시스템 개발 프로젝트입니다.

---

## 🧭 프로젝트 개요

기존의 수동 제어/지도 보기 기능만 존재하던 차량 인포테인먼트 시스템에 OTA 업데이트를 통해 **음성 제어 기능을 동적으로 추가**할 수 있도록 설계하였습니다. Raspberry Pi 기반 인포테인먼트/차량 제어 모듈 간 통신, OTA 업데이트 자동화, 실시간 음성 인식 및 제어 GUI까지 통합 구현하였습니다.

---

## 🛠️ 기술 스택 및 개발 환경

| 항목 | 내용 |
|------|------|
| 하드웨어 | Raspberry Pi 4, Raspberry Pi 5, 터치스크린 모니터, Stepper Motor HAT |
| 언어 | Python 3.11.2 |
| 음성 인식 | Google Cloud Speech-to-Text API |
| GUI | PySide6 (Qt 기반) |
| 지도 표시 | Google Maps API + WebEngineView (HTML/JS 내장) |
| OTA 업데이트 | GitHub Releases + Python 크론 스케줄러 + Signal Handling |
| 기타 | WebSocket, systemd 서비스 자동 실행, cron, threading |

---

## 📦 주요 기능

### ✔ OTA 업데이트
- GitHub 최신 릴리즈 확인 → 업데이트 감지 시 사용자 정의 시그널(SIGUSR1) 전달
- GUI에서 다운로드 및 설치 진행
- 기존 버전 백업 및 새로운 버전 실행, 프로세스 종료까지 자동화

### ✔ 인포테인먼트 기능
- **지도 확인**: Google Maps API 기반 내장 브라우저 표시
- **수동 제어**: 터치 입력(직진, 후진, 좌회전, 우회전)을 차량 모듈에 WebSocket으로 전달
- **음성 제어**: Google Cloud Speech API로 실시간 명령어 인식 및 전송
- **GUI 자동 실행**: systemd 서비스로 재부팅 시 앱 자동 실행

---

## ⚙️ OTA 기능 구현 방법 상세 설명

### 🔍 1. 최신 업데이트 버전 출시 확인

- `watcher.py`는 GitHub의 최신 릴리즈 태그와 로컬에 저장된 버전을 매일 새벽 2시에 비교합니다.
- 이는 `cron` 탭에 등록된 다음 명령어를 통해 실행됩니다:

```bash
0 2 * * * /home/pi/myenv/bin/python /home/pi/052617/watcher.py >> /home/pi/052617/watcher.log 2>&1
```

- 새로운 버전이 감지되면 `SIGUSR1` 사용자 정의 시그널을 `mainwindow.py` 프로세스에 전송합니다.

---

### 🔧 2. 새로운 버전이 있는 경우 업데이트

- `mainwindow.py`는 시그널을 감지하면 `ota_signal.py`의 콜백 함수를 통해 GUI에 업데이트 창을 표시합니다.
- 사용자가 "시작" 버튼을 누르면 `updater.py`가 실행되어 다음의 순서로 OTA 업데이트가 진행됩니다:

1. 로컬의 버전 정보를 업데이트  
2. 기존 SW를 백업 폴더로 이동 후, GitHub에서 새로운 버전 SW 다운로드  
3. 새로운 SW를 백그라운드에서 실행  
4. 기존 GUI 앱 프로세스에 `SIGTERM`을 보내 종료

이 과정을 통해 인포테인먼트 시스템은 중단 없이 최신 기능(예: 음성 제어)을 수신하고 자동 반영할 수 있습니다.

---

## 🖼️ OTA 기능 업데이트 결과

- GUI v0.0.1 → v0.0.2 OTA 적용 후 음성 제어 기능 추가

---

## 📂 Repository

- OTA 감지 및 업데이트 코드: [github.com/jaysc5/OTA-Software-Update](https://github.com/jaysc5/OTA-Software-Update)
- 프로젝트 메인 저장소: [github.com/jaysc5/what-s-your-OTA](https://github.com/jaysc5/what-s-your-OTA)

