#!/bin/sh
cd ~/.local/share/
echo "MediathekSuche herunterladen ..."
wget https://github.com/Axel-Erfurt/MediathekSuche/archive/master.zip
echo "MediathekSuche entpacken"
unzip -o master.zip
echo "zip Datei wird entfernt"
rm master.zip
mv ~/.local/share/MediathekSuche-master ~/.local/share/MediathekSuche
cp ~/.local/share/MediathekSuche/MediathekSuche.desktop ~/.local/share/applications
echo "MediathekSuche wird gestartet ..."
python3 ~/.local/share/MediathekSuche/MediathekSuche.py
