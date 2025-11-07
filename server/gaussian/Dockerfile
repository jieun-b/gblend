FROM nvidia/cuda:11.6.2-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /home

RUN apt-get update && apt-get install -y \
    git wget curl build-essential ninja-build cmake \
    libgl1-mesa-dev libglib2.0-0 python3 python3-dev python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN pip install --upgrade pip==22.3.1 setuptools wheel

RUN git clone --recursive https://github.com/graphdeco-inria/gaussian-splatting.git
WORKDIR /home/gaussian-splatting

RUN pip install torch==1.12.1 torchvision==0.13.1 torchaudio==0.12.1 \
    --extra-index-url https://download.pytorch.org/whl/cu116

RUN pip install plyfile tqdm joblib opencv-python ninja cmake

ENV CUDA_HOME=/usr/local/cuda
ENV TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6"
ENV CC=gcc
ENV CXX=g++

RUN pip install --no-cache-dir ./submodules/diff-gaussian-rasterization
RUN pip install --no-cache-dir ./submodules/simple-knn
RUN pip install --no-cache-dir ./submodules/fused-ssim

WORKDIR /home

COPY requirements.txt /home/requirements.txt
RUN pip install --no-cache-dir -r /home/requirements.txt

COPY app.py /home/app.py

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

