# 📡 What's Your OTA?

SSAFY 13기 임베디드 관통 프로젝트  
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
- **수동 제어**: 터치 입력을 차량 모듈에 WebSocket으로 전달
- **음성 제어**: Google Cloud Speech API로 실시간 명령어 인식 및 전송
- **GUI 자동 실행**: systemd 서비스로 재부팅 시 앱 자동 실행

---

## 🧪 시스템 구조

```
[GUI (Raspberry Pi 5)] <-- OTA 업데이트 + 음성 인식
       │
       ├─ WebSocket 통신
       ▼
[차량 제어 모듈 (Raspberry Pi 4)] ← 모터 제어
```

---

## 🖼️ 데모 영상 및 예시

- GUI v0.0.1 → v0.0.2 OTA 적용 후 음성 제어 기능 추가
- 마이크 입력 → 음성 인식 결과 표시 → 차량 제어 명령 송신

---

## 🕒 스케줄 예시 (cron)

```bash
0 2 * * * /home/pi/myenv/bin/python /home/pi/052617/watcher.py >> /home/pi/052617/watcher.log 2>&1
```
- 매일 새벽 2시 GitHub 릴리즈 확인
- SIGUSR1 → 다운로드 창 팝업 → 업데이트 실행

---

## 📂 Repository

- OTA 감지 및 업데이트 코드: [github.com/jaysc5/OTA-Software-Update](https://github.com/jaysc5/OTA-Software-Update)
- 프로젝트 메인 저장소: [github.com/jaysc5/what-s-your-OTA](https://github.com/jaysc5/what-s-your-OTA)

---

## 🙋 팀원

양가은, 이봄, 최지수 (SSAFY 13기 임베디드 19반)
