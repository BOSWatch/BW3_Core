# <center>Regex Filter</center> 
---

## Beschreibung
Mit diesem Modul ist es möglich, komplexe Filter basierend auf Regulären Ausdrücken (Regex) anzulegen.  
Für einen Filter können beliebig viele Checks angelegt werden, welche Felder eines BOSWatch Pakets mittels Regex prüfen.

Folgendes gilt:

- Die Filter werden nacheinander abgearbeitet
- Innerhalb des Filters werden die Checks nacheinander abgearbeitet
- Sobald ein einzelner Check fehlschlägt ist der ganze Filter fehlgeschlagen
- Sobald ein Filter mit all seinen Checks besteht, wird mit der Ausführung des Routers fortgefahren
- Sollten alle Filter fehlschlagen wird die Ausführung des Routers beendet

Vereinfacht kann man sagen, dass einzelnen Router ODER-verknüpft und die jeweiligen Checks UND-verknüpft sind.

## Unterstütze Alarmtypen
- Fms
- Pocsag
- Zvei
- Msg

## Resource
`filter.regexFilter`

## Konfiguration
|Feld|Beschreibung|Default|
|----|------------|-------|
|name|Beliebiger Name des Filters||
|checks|Liste der einzelnen Checks innerhalb des Filters||

#### `checks:`
|Feld|Beschreibung|Default|
|----|------------|-------|
|field|Name des Feldes innerhalb des BOSWatch Pakets welches untersucht werden soll||
|regex|Regulärer Ausdruck (Bei Sonderzeichen " " verwenden)||

**Beispiel:**
```yaml
- type: module
  res: filter.regexFilter
  config:
    - name: "Zvei filter"
      checks:
        - field: tone
          regex: "65[0-9]{3}"  # all zvei with starting 65
    - name: "FMS Stat 3"
      checks:
        - field: mode
          regex: "fms"  # check if mode is fms
        - field: status
          regex: "3"  # check if status is 3
```

---
## Modul Abhängigkeiten
- keine

---
## Externe Abhängigkeiten
- keine

---
## Paket Modifikationen
- keine

---
## Zusätzliche Wildcards
- keine