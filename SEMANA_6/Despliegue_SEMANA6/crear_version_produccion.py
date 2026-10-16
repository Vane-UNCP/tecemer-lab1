import json, shutil

v1 = json.load(open("version_info_v1.json", encoding="utf-8"))
v2 = json.load(open("version_info_v2.json", encoding="utf-8"))
ganadora = max([v1, v2], key=lambda v: v["metricas"]["f1_clase_1"])

shutil.copy(f"version_info_{ganadora['version']}.json", "version_info_produccion.json")
print("Versión en producción:", ganadora["version"])