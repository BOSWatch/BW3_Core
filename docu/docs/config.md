# <center>Konfiguration</center>

Die Konfiguration von BOSWatch 3 ist im YAML Format abgelegt und wird nachfolgend beschrieben.  
Immer wenn für eine Einstellung ein **Default** Wert angegeben ist, muss diese Einstellung nicht
zwingend in die Konfiguration eingetragen werden.

## Client

---
### `client:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|name|Name zur Identifizierung der Client Instanz||
|inputSource|Art der zu nutzenden Input Quelle (`sdr` oder `lineIn`)||
|useBroadcast|Verbindungsdaten per [Broadcast](information/broadcast.md) beziehen|no|
|reconnectDelay|Verzögerung für erneuten Verbindungsversuch zum Server|3|
|sendTries|Anzahl der Sendeversuche eines Pakets|3|
|sendDelay|Verzögerung für einen erneuten Sendeversuch|3|

---
### `server:`
Der Abschnitt `server:` wird nur genutzt, wenn `useBroadcast: no` gesetzt ist.  
Ansonsten wird versucht die Verbindungsdaten per Broadcast Paket direkt vom Server zu beziehen.

|Feld|Beschreibung|Default|
|----|------------|-------|
|ip|IP Adresse des Servers|127.0.0.1|
|port|Port des Sever|8080|

**Beispiel:**
```yaml
server:
  ip: 10.10.10.2
  port: 9123
```

---
### `inputSource:`
Es gibt die Auswahl zwischen `sdr` oder `lineIn` als Input Quelle

#### `sdr:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|device|rtl_fm Device ID|0|
|frequency|Zu empfangende Frequenz||
|error|Frequenz Abweichung in ppm|0|
|squelch|Einstellung der Rauschsperre|1|
|gain|Verstärkung des Eingangssignals|100|
|rtlPath|Pfad zur rtl_fm Binary|rtl_fm|
|mmPath|Pfad zur multimon-ng Binary|multimon-ng|

**Beispiel:**
```yaml
inputSource:
  sdr:
    device: 0
    frequency: 85M
    error: 0
    squelch: 1
    gain: 100
    rtlPath: /usr/bin/rtl-fm
    mmPath: /opt/multimon/multimon-ng
```

#### `lineIn:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|device|die device Id der Soundkarte|1|
|mmPath|Pfad zur multimon-ng Binary|multimon-ng|

**Device herausfinden**
Durch eingabe des Befehls `aplay -l` werden alle Soundkarten ausgegeben. Das schaut ungefähr so aus:
```console
**** List of PLAYBACK Hardware Devices ****
card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
  Subdevices: 7/7
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
card 0: ALSA [bcm2835 ALSA], device 1: bcm2835 IEC958/HDMI [bcm2835 IEC958/HDMI]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: ALSA [bcm2835 ALSA], device 2: bcm2835 IEC958/HDMI1 [bcm2835 IEC958/HDMI1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: Device [C-Media USB Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

Wir betrachten das letzte Gerät: `card 1: Device [C-Media USB Audio Device], device 0: USB Audio [USB Audio]`

In dem Fall ist das letzte Gerät - `card 1` - unsere USB-Audio Schnittstelle die wir verwenden wollen.
In der Konfiguration wird das Feld `card` nun auf den Wert 1 gesetzt.

Nach dem Typ der Soundkarte steht das device, in diesem Fall `device 0`.
In der Konfiguration wird das Feld `device` nun auf den Wert 0 gesetzt.

**Beispiel:**
```yaml
inputSource:
  ...
  lineIn:
    card: 1
    device: 0
    mmPath: /opt/multimon/multimon-ng
```

---
### `decoder:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|fms|FMS Decoder|no|
|zvei|ZVEI Decoder|no|
|poc512|POCSAG Decoder (Bitrate 512)|no|
|poc1200|POCSAG Decoder (Bitrate 1200)|no|
|poc2400|POCSAG Decoder (Bitrate 2400)|no|

---
## Server
Nachfolgend alle Paramater der Server Konfiguration

### `server:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|port|Port auf dem der Server lauscht|8080
|name|Name zur Identifizierung der Server Instanz||
|useBroadcast|Verbindungsdaten per Broadcast Server bereitstellen|no|

---
### `alarmRouter:`
Enthält eine Liste der Router Namen, welche bei einem Alarm direkt gestartet werden sollen.

**Beispiel:**
```yaml
alarmRouter:
  - Name des Routers
  - ein weiter Router
```

---
### `router:`
Mit den Routern kann der Verarbeitungsweg eines Alarm-Paketes festgelegt werden. Es können beliebig viele Router in Form einer Liste angegeben werden.

|Feld|Beschreibung|Default|
|----|------------|-------|
|name|Name des Routers||
|route|Definiten des Routenverlaufs

#### `route:`

Jeder Router kann eine beliebige Anzahl einzelner Routenpunkte enthalten. Diese werden innerhalb des Routers sequentiel abgearbeitet. Mögliche Typen der Routenpunkte sind dabei ein Modul, ein Plugin oder ein anderer Router. Sie werden ebenfalls in Form einer Liste definiert.

|Feld|Beschreibung|Default|
|----|------------|-------|
|type|Art des Routenpunktes (module, plugin, router)||
|res|Zu ladende Resource (Siehe entsprechende Kapitel)||
|name|Optionaler Name des Routenpunktes|gleich wie Resource|
|config|Konfigurationseinstellungen des Routenpunktes (Siehe entsprechende Kapitel)||

**Beispiel:**
```yaml
router:
  - name: Router 1
    route:
      - type: module
        res: filter.modeFilter
        name: Filter Fms/Zvei
        config:
          allowed:
            - fms
```

---
## Module/Plugins

Die möglichen Einstellungen der einzelnen Module und Plugins sind im jeweiligen Kapitel aufgelistet.
