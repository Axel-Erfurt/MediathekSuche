# MediathekSuche
🇩🇪
- Mediathek durchsuchen, Filme abspielen, Filme herunterladen
- Integrierter Player & Downloader

Getestet in Mint 19.3 und Ubuntu 18.04 / 19.10

Es kann die Mediathek (ARD, ZDF ...) durchsucht werden, ohne vorher die gesamte Liste herunterladen zu müssen.



__Voraussetzungen__

- python3
- [PyQt5 & Gstreamer - siehe Ubuntuusers Wiki 🇩🇪](https://wiki.ubuntuusers.de/Baustelle/Howto/TVPlayer2/#PyQt5)



__Installation Mint / Ubuntu__

im Terminal folgenden Befehl ausführen:

```wget 'https://raw.githubusercontent.com/Axel-Erfurt/MediathekSuche/master/Install.sh' -O ~/Downloads/Install.sh && chmod +x ~/Downloads/Install.sh && ~/Downloads/Install.sh```

Damit wird die aktuelle Version von github heruntergeladen und im Ordner ~/.local/share/ gespeichert.

Ein Starter (MediathekSuche.desktop) wird in ~/.local/share/applications erstellt

Speicherbedarf auf der Festplatte ca 500kB



__Deinstallation__

Dazu im Terminal folgende Befehle ausführen

```cd ~/.local/share/ && rm -rf MediathekSuche```

```cd ~/.local/share/applications && rm MediathekSuche.desktop```



__Programm starten__

Aus dem Startmenu (MediathekSuche)

oder im Terminal mit

```cd ~/.local/share/MediathekSuche && python3 ./MediathekSuche.py```


In der Datei DLOrdner.txt kann der Download Ordner festgelegt werden (Slash am Ende!)

Beispiel:

```/home/Benutzer/Videos/```

SD / HD umschalten mit Button (gilt für Player und Downloader)

__Wildcards__

- # Thema durchsuchen
- + Title durchsuchen
- * Beschreibung durchsuchen
- ohne alles durchsuchen

__Shortcuts__

- Mausrad = Fenstergröße ändern
- F = Fullscreen an / aus
- ↑ = lauter
- ↓ = leiser
- ← = < 1 Minute zurück
- → = > 1 Minute vor
- SHIFT + ← = < 10 Minutes zurück
- SHIFT + → = > 10 Minutes vor
- Q = Fenster schließen
`

![screenshot](https://github.com/Axel-Erfurt/MediathekSuche/blob/master/screenshot.png)
