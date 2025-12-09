# GBlend

GBlend는 Gaussian Splatting 기반 3D 씬을 Blender에서 합성 데이터 생성에 활용할 수 있도록 만든 경량 애드온입니다.

👉 [Demo Video](https://youtu.be/rguLeDei1Rk)

## Installation

1. Blender 4.x 다운로드  
2. [Download Add-on (v0.1.0)](https://github.com/jieun-b/gblend/releases/download/v0.1.0/addon.zip)  
3. Blender → Edit > Preferences → Add-ons → Install  
4. `addon.zip` 선택  
5. GBlend 활성화  

## Requirements

GBlend의 전체 기능을 사용하려면 아래 구성 요소가 필요합니다.

- **KIRI Engine** (Blender용 Gaussian Splatting Viewer)  
  👉 https://www.kiriengine.app/blender-addon

- **GBlend Server**  
  씬 생성, 정렬 등 일부 기능은 외부 서버가 필요합니다.  
  👉 서버 설정 가이드: [server/README.md](https://github.com/jieun-b/gblend/blob/main/server/README.md)

## Quick Start

1. COLMAP 데이터셋 폴더 선택  
2. Gaussian Splatting 씬 생성  
3. 씬 정렬 (Z-up / scale)  
4. Animated Camera 생성  
5. 객체 텍스트 검색 → GLB 배치  
6. Camera Cull 실행  
7. 렌더 설정 후 출력