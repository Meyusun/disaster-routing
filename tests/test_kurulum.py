"""Kurulum testi (Adim 1): kutuphaneler, osmnx surumu ve EMSR648 verisi yerinde mi?

Veri klasoru varsayilan olarak proje kokundeki "data"; DR_VERI_KOK ortam degiskeniyle degistirilebilir.
"""
import glob
import importlib
import os
import warnings
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
KUTUPHANELER = ["osmnx", "networkx", "geopandas", "shapely", "pyproj",
                "rasterio", "scipy", "numpy", "matplotlib", "PIL"]
# scripts/run_emsr.py dosyalari "<veri>/*<AOI>*/*<ad>*.shp" kalibiyla ariyor.
EMSR_DOSYALARI = ["areaOfInterestA", "builtUpA"]
EKSIK_MESAJ = "data/emsr648 eksik: README'deki 'Veri hazırlığı' adımını yap."


def _veri_kok():
    return KOK / os.environ.get("DR_VERI_KOK", "data")  # mutlak yol verilirse KOK yok sayilir


def _eksik_dosyalar(emsr, aoi):
    return [ad for ad in EMSR_DOSYALARI
            if not glob.glob("{}/*{}*/*{}*.shp".format(emsr, aoi, ad))]


def test_kutuphaneler_yuklenebiliyor():
    eksik = []
    for ad in KUTUPHANELER:
        try:
            importlib.import_module(ad)
        except ImportError:
            eksik.append(ad)
    assert not eksik, "Şu kütüphaneler yüklenemedi: {}. environment.yml ile ortamı kurun.".format(", ".join(eksik))


def test_osmnx_surumu():
    import osmnx
    ana = int(osmnx.__version__.split(".")[0])
    assert ana >= 2, "osmnx sürümü {} — en az 2.x gerekli.".format(osmnx.__version__)


def test_emsr_verisi_var():
    emsr = _veri_kok() / "emsr648"
    eksik = _eksik_dosyalar(emsr, "AOI17")
    assert not eksik, "{} (bakılan yer: {}, AOI17'de eksik: {})".format(EKSIK_MESAJ, emsr, ", ".join(eksik))
    for aoi in ("AOI04", "AOI16"):
        eksik = _eksik_dosyalar(emsr, aoi)
        if eksik:
            warnings.warn("{} verisi eksik ({}): {}".format(aoi, emsr, ", ".join(eksik)))
