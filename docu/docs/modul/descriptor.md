# <center>Descriptor</center> 
---

## Beschreibung
Mit diesem Modul können einem Alarmpaket beliebige Beschreibungen in Abhänigkeit der enthaltenen Informationen hinzugefügt werden.

## Unterstütze Alarmtypen
- Fms
- Pocsag
- Zvei
- Msg

## Resource
`descriptor`

## Konfiguration
Informationen zum Aufbau eines [BOSWatch Pakets](../develop/packet.md)

|Feld|Beschreibung|Default|
|----|------------|-------|
|scanField|Feld des BW Pakets welches geprüft werden soll||
|descrField|Name des Feldes im BW Paket in welchem die Beschreibung gespeichert werden soll||
|wildcard|Optional: Es kann für das angelegte `descrField` automatisch ein Wildcard registriert werden|None|
|descriptions|Liste der Beschreibungen||

#### `descriptions:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|for|Inhalt im `scanField` auf welchem geprüft werden soll||
|add|Beschreibungstext welcher im `descrField` hinterlegt werden soll||

**Beispiel:**
```yaml
- type: module
  res: descriptor
  config:
    - scanField: tone
      descrField: description
      wildcard: "{DESCR}"
      descriptions:
        - for: 12345
          add: FF DescriptorTest
        - for: 45678
          add: FF TestDescription
    - scanField: status
      descrField: fmsStatDescr
      wildcard: "{STATUSTEXT}"
      descriptions:
        - for: 1
          add: Frei (Funk)
        - for: 2
          add: Frei (Wache)
        - ...
```

---
## Modul Abhängigkeiten
- keine

---
## Externe Abhängigkeiten
- keine

---
## Paket Modifikationen
- Wenn im Paket das Feld `scanField` vorhanden ist, wird das Feld `descrField` dem Paket hinzugefügt
- Wenn keine Beschreibung vorhanden ist, wird im Feld `descrField` der Inhalt des Feldes `scanField` hinterlegt

---
## Zusätzliche Wildcards
- Von der Konfiguration abhängig
