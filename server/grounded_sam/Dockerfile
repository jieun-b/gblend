FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel

# Arguments to build Docker Image using CUDA
ARG USE_CUDA=0
ARG TORCH_ARCH="7.0;7.5;8.0;8.6"

ENV AM_I_DOCKER=True
ENV BUILD_WITH_CUDA="${USE_CUDA}"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_ARCH}"
ENV CUDA_HOME=/usr/local/cuda-12.1
# Ensure CUDA is correctly set up
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/conda/lib/python3.10/site-packages/torch/lib


# Install required packages and specific gcc/g++
RUN apt-get update && apt-get install --no-install-recommends wget ffmpeg=7:* \
    libsm6=2:* libxext6=2:* git=1:* nano vim=2:* ninja-build gcc-10 g++-10 -y \
    && apt-get clean && apt-get autoremove && rm -rf /var/lib/apt/lists/*

ENV CC=gcc-10
ENV CXX=g++-10

WORKDIR /home

COPY requirements.txt /home/requirements.txt
RUN pip install --no-cache-dir -r /home/requirements.txt

COPY app.py /home/app.py

RUN git clone --depth 1 https://github.com/IDEA-Research/Grounded-SAM-2.git
WORKDIR /home/Grounded-SAM-2


# Install essential Python packages
RUN python -m pip install --upgrade pip "setuptools>=62.3.0,<75.9" wheel numpy \
    opencv-python transformers supervision pycocotools addict yapf timm

# Install segment_anything package in editable mode

RUN sed -i "s/-gencode=arch=compute_120,code=sm_120/-gencode=arch=compute_75,code=sm_75/" setup.py

RUN pip install -e .
RUN pip install --no-build-isolation -e grounding_dino

RUN cd grounding_dino && \
    bash ../checkpoints/download_ckpts.sh && \
    bash ../gdino_checkpoints/download_ckpts.sh 
    

WORKDIR /home
ENV PYTHONPATH=/home

EXPOSE 8001
CMD ["uvicorn", "app:app", "--app-dir", "/home", "--host", "0.0.0.0", "--port", "8001"]
