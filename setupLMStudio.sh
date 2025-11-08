#!/bin/bash
if [ -n "$1" ]
then

pip install -r ./req.txt

# start LmStudio first time
$1
sleep 5m

# Clean up any existing processes
killall lm-studio


# Create permanent directory and extract/relocate AppImage
sudo mkdir -p /opt/lm-studio
$1 --appimage-extract
sudo mv squashfs-root/* /opt/lm-studio/
# Clean up existing configs (optional?)
rm ~/.lm-studio/.internal/http-server-ctl.json
rm ~/.lm-studio/.internal/http-server-config.json

# Update the app location config to point to permanent mount
 echo '{"path":"/opt/lm-studio/lm-studio","argv":["/opt/lm-studio/lm-studio"],"cwd":"'$HOME'"}' > ~/.lmstudio/.internal/app-install-location.json
# Ensure sure executable has proper permissions
sudo chmod +x /opt/lmstudio/lm-studio
# add lms to PATH
sudo echo 'export PATH="$PATH:$HOME/.lmstudio/bin"' >> ./.bashrc
source ./.bashrc

else
echo "LM studio appimage path not set. "
fi
