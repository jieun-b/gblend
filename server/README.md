# GBlend 로컬 서버 실행 가이드

이 문서는 GBlend Add-on과 함께 사용할 로컬 서버 실행 방법을 안내합니다.
GBlend는 CUDA 기반으로 동작하며, 각 기능은 개인 GPU 환경에서 독립적인 FastAPI 서버로 실행됩니다.

## 사전 요구사항

### 1. Docker 설치
   ```bash
   # Docker 설치 확인
   docker --version
   docker-compose --version
   ```

### 2. NVIDIA GPU 및 CUDA 지원
   - Gaussian 서버와 Grounded-SAM 서버는 CUDA가 필요합니다.
   - GPU 확인: `nvidia-smi`


## 서버별 상세 안내

각 서버는 기본적으로 `localhost` 포트(8000–8002)로 실행되며, Add-on 내부 `config.py` 설정에서 자동으로 연결됩니다.

### 서버 비교 요약

| 서버 | 포트 | CUDA | GPU | 주요 특징 |
|------|------|-----------|----------|-------------|
| **Gaussian** | 8000 | 11.6 | ✅ 필요 | 3D 학습용, 시간 오래 걸림 |
| **Grounded-SAM** | 8001 | 12.1 | ✅ 필요 | 이미지 추론, 빠름 |
| **Objaverse** | 8002 | 없음 | ❌ 불필요 | 모델 다운로드 및 캐싱 |
 

### 1. Gaussian Splatting 서버

COLMAP 데이터셋을 입력받아 3D Gaussian Splatting 모델을 학습하는 서버입니다. 
학습 완료 후 결과를 zip 파일 형태로 반환합니다.
 
#### 실행 방법

```bash
cd server/gaussian
docker build -t gaussian-server .
docker run -d --name gaussian-container --gpus all -p 8000:8000 gaussian-server
```

#### API

- **엔드포인트**: `POST /gaussian/`
- **입력**: COLMAP 데이터셋(`.zip`)
- **출력**: 학습 완료된 결과(`output.zip`)


### 2. Grounded-SAM-2 서버

이미지를 입력받아 바닥 영역을 자동 탐지하고 마스크 이미지를 생성하는 서버입니다. 
Grounding DINO와 SAM2 모델을 활용하여 바닥 영역을 정밀하게 분리합니다.
추가로, SAM1 기반의 이미지 세그멘테이션 기능과 MiDaS(DPT-Large) 기반의 깊이(Depth) 맵 추정 기능도 제공합니다.

#### 실행 방법

```bash
cd server/grounded_sam
docker build -t grounded-sam-server .
docker run -d --name grounded-sam-container --gpus all -p 8001:8001 grounded-sam-server
```

#### API

- **엔드포인트**: `POST /grounded_sam/`
- **입력**: 이미지 파일 (`.jpg`, `.png` 등)
- **출력**: 바닥 영역 마스크 (`mask.png`)

- **엔드포인트**: `POST /segment/`
- **입력**: 이미지 파일 (`.jpg`, `.png` 등)
- **출력**: 세그멘테이션 결과 이미지 (`segment.png`)

- **엔드포인트**: `POST /depth/`
- **입력**: 이미지 파일 (`.jpg`, `.png` 등)
- **출력**: 정규화된 Depth Map (`depth.png`)


### 3. Objaverse 서버

텍스트 쿼리를 입력받아 Objaverse 데이터셋에서 3D GLB 모델을 검색하고 다운로드하는 서버입니다. 
CLIP 모델을 이용해 텍스트 의미와 유사한 객체를 찾아 반환합니다.


#### 실행 방법

```bash
cd server/objaverse
docker build -t objaverse-server .
docker run -d --name objaverse-container -v $(pwd)/data:/home/data -p 8002:8002 objaverse-server
```

#### API

- **엔드포인트**: `GET /download_glb/?query=<검색어>`
- **입력**: 검색어 (예: `chair`, `car` 등)
- **출력**: 해당 객체의 GLB 3D 모델 파일
