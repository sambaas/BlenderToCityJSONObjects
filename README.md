# Bomen CityJSON genereren adhv. maaiveld hoogte

Dit python script + Blender bestand maakt het mogelijk om CityJSONs te genereren met daarin 'lowpoly' bomen.
De RD locatie en type van de bomen wordt uit CSV bestan(den) gehaald, en de hoogte wordt bepaald aan de hand van 3D tegels gegenereerd met de TileBakeTool (https://github.com/Amsterdam/CityDataToBinaryModel)

Begin met het clonen van deze repo in een map:

git clone https://github.com/sambaas/BlenderToCityJSONObjects.git

## Blender3.2

Blender is nodig om dit script te starten, maar is niet bijgesloten in deze repository.
Download Blender 3.2 als zip en pak deze uit in de map /Blender3.2/

https://www.blender.org/download/releases/3-2/

## CSV met bomen

Plaats een CSV (of meerdere) met de bomen informatie in de map "CSVs"
De CSV moet de volgende velden bevatten (qua volgorde, header name doet er niet toe)

Id;Boomsoort;Boomhoogte;X-Coordinaat;Y-Coordinaat;

Er staat een voorbeeld csv in de CSVs map.

## Binaire grondtegels

Plaats de binaire grondtegels (gegenereerd met de TileBakeTool*) in de map "GroundTiles".
De bestanden moeten qua benaming overeenkomen met bijvoorbeeld: terrain_117000-442000-lod1.bin
Waarin de x en y coordinaten natuurlijk per tegel verschillen.

*https://github.com/Amsterdam/CityDataToBinaryModel

## Start het script

Start het script met het bestand "Start_GeneratingTrees.bat"
