# Install CSCORE
echo "Installing CSCORE"
echo 'deb http://download.opensuse.org/repositories/home:/auscompgeek:/robotpy/Raspbian_11/ /' | sudo tee /etc/apt/sources.list.d/home:auscompgeek:robotpy.list
curl -fsSL https://download.opensuse.org/repositories/home:auscompgeek:robotpy/Raspbian_11/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_auscompgeek_robotpy.gpg > /dev/null
sudo apt update
sudo apt install python3-cscore