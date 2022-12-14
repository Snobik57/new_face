# install nvidia-driver
```bash
ubuntu-drivers devices
sudo apt install nvidia-driver-<recommended version>
sudo reboot
```

# install cuda an driver nvidia:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda

reboot
```

# install cudnn:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/${OS}/x86_64/cuda-${OS}.pin

sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt-get update
```

**Where:**

**${OS} is `debian11`, `ubuntu1804`, `ubuntu2004`, `ubuntu2204`.**

```bash
sudo apt-get install libcudnn8=${cudnn_version}-1+${cuda_version}
sudo apt-get install libcudnn8-dev=${cudnn_version}-1+${cuda_version}
```

**Where:**

**${cudnn_version} is `8.6.0.*`**

**${cuda_version} is `cuda10.2` or `cuda11.8`**
    

# install dlib:

```bash
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build
cd build
cmake ..
cmake --build .
```
        
## install virtualenv

- add virtualenv in your project
- activate
- install requirements
- remove dlib: `pip uninstall dlib`

```bash
cd 
cd dlib
python setup.py install
```