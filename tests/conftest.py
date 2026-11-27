"""Testlerin ortak yol agi.

Varsayilan: internetsiz, 6x6 kavsakli sahte bir izgara sehir (kavsaklar arasi 100 m, UTM 37N).
DR_CANLI=1 ortam degiskeni verilirse V3'teki gercek OSM bolgesi (Kahramanmaras, internet gerekir) kullanilir.
Ayni testler iki durumda da calisir.
"""
import os
import networkx as nx
import pytest
from pyproj import Transformer
from shapely.geometry import LineString

CRS = "EPSG:32637"
X0, Y0, ADIM, N = 300000.0, 4160000.0, 100.0, 6
_geri = Transformer.from_crs(CRS, "EPSG:4326", always_xy=True).transform


def _latlon(x, y):
    lon, lat = _geri(x, y)
    return lat, lon


def sahte_sehir():
    G = nx.MultiDiGraph(crs=CRS)
    for i in range(N):
        for j in range(N):
            G.add_node(i * N + j, x=X0 + j * ADIM, y=Y0 + i * ADIM)
    for i in range(N):
        for j in range(N):
            a = i * N + j
            for b in ([a + 1] if j < N - 1 else []) + ([a + N] if i < N - 1 else []):
                for u, v in ((a, b), (b, a)):
                    geom = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])])
                    G.add_edge(u, v, key=0, length=ADIM, geometry=geom, osmid=len(G.edges))
    A = _latlon(X0 + 10, Y0 + 10)                                   # sol alt kose yakini
    B = _latlon(X0 + (N - 1) * ADIM - 10, Y0 + (N - 1) * ADIM - 10)  # sag ust kose yakini
    return G, A, B


@pytest.fixture
def sehir():
    if os.environ.get("DR_CANLI") == "1":
        from dr.routing import load_graph
        G = load_graph(36.925, 37.575, 36.940, 37.585)
        return G, (37.577, 36.927), (37.583, 36.938)
    return sahte_sehir()
