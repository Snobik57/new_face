# Install Nvidia driver

```bash
sudo modprobe -r nouveau
sudo apt install nvidia-driver-390 nvidia-headless-390 nvidia-utils-390
sudo modprobe -i nvidia
```

# Install CUDA toolkit

```bash
pushd /tmp/

curl -LO https://developer.nvidia.com/compute/cuda/9.1/Prod/local_installers/cuda_9.1.85_387.26_linux
curl -LO https://developer.nvidia.com/compute/cuda/9.1/Prod/patches/1/cuda_9.1.85.1_linux
curl -LO https://developer.nvidia.com/compute/cuda/9.1/Prod/patches/2/cuda_9.1.85.2_linux
curl -LO https://developer.nvidia.com/compute/cuda/9.1/Prod/patches/3/cuda_9.1.85.3_linux
```

## do not install driver or samples

```bash
sudo sh cuda_9.1.85_387.26_linux --silent --override --toolkit
```


## install the patches


```bash
sudo sh cuda_9.1.85.1_linux --silent --accept-eula
sudo sh cuda_9.1.85.2_linux --silent --accept-eula
sudo sh cuda_9.1.85.3_linux --silent --accept-eula
```


## set system wide paths

```bash
echo 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/local/cuda/bin"' | sudo tee /etc/environment
echo /usr/local/cuda-9.1/lib64 | sudo tee /etc/ld.so.conf.d/cuda-9.1.conf
sudo ldconfig

rm /tmp/cuda_9.1.85*_linux
popd
```


# Check that it's working
## reboot system for changes to take effect

```bash
sudo reboot

lsmod | grep nouv && echo FAIL || echo OKAY
lsmod | grep nvid && echo OKAY || echo FAIL

grep -E 'NVIDIA.*390.[0-9]+' /proc/driver/nvidia/version &>/dev/null && echo OKAY || echo FAIL
nvcc -V | grep -E "V9.1.[0-9]+" &>/dev/null && echo OKAY || echo FAIL
```

## this should return stats for all installed cards

```bash
nvidia-smi
```
	
# Install cudnn for cuda 9.1

## Download file with 

"Download cuDNN v7.1.3 (April 17, 2018), for CUDA 9.1"
https://developer.nvidia.com/rdp/cudnn-archive

## Under the Download directory

```bash
tar xvzf cudnn-9.1-linux-x64-v7.1.tgz
sudo cp cuda/include/cudnn.h /usr/local/cuda-9.1/include/
sudo cp cuda/lib64/libcudnn* /usr/local/cuda-9.1/lib64/
sudo chmod a+r /usr/local/cuda-9.1/include/cudnn.h /usr/local/cuda-9.1/lib64/libcudnn*
```