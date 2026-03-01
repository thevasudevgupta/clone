this will be my virtual clone soon. follow [x.com/thevasudevgupta](https://x.com/thevasudevgupta) for updates.

## Setting Up
* create project in GCP
* add billing
* enable compute engine api
* launch instance: e2-micro ~$7 per month

```bash
gcloud auth login
gcloud config set project tvgbot

# Run following command to HostName
gcloud compute instances describe tvgbot --zone us-central1-c --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

# replace ${HostName} with result from previous command
echo 'Host tvgbot
    HostName ${HostName}
    User vasudevgupta
    IdentityFile ~/.ssh/google_compute_engine' >> ~/.ssh/config

ssh tvgbot
```

```bash
sudo apt-get update && sudo apt-get install git make -y

git config --global user.name "Vasudev Gupta"
git config --global user.email "7vasudevgupta@gmail.com"

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
$HOME/miniconda3/bin/conda init
source ~/.bashrc

pip install -e .
```

```bash
python3 run.py --server=discord --max_requests_per_prompt=20
```
