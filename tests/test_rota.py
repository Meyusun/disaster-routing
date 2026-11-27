"""Rota cekirdegi testleri (V3'teki T1, T2, T3, T4, T5, T8a, T8b, T9 ile ayni kontroller)."""
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
from dr.routing import (shortest_route, edge_cost, close_edges_near,
                        delay_edges_near, clearing_route)


def kapali_kullaniyor(G, path):
    return any(edge_cost(u, v, G[u][v]) is None for u, v in zip(path[:-1], path[1:]))


def yolu_kapat(G, u, v):
    for a, b in ((u, v), (v, u)):
        if G.has_edge(a, b):
            for d in G[a][b].values():
                d["closed"] = True


def test_T1_hasarsiz_rota_ve_dijkstra_ayni(sehir):
    G, A, B = sehir
    path, L = shortest_route(G, A, B)
    assert path is not None
    assert abs(L - nx.dijkstra_path_length(G, path[0], path[-1], weight=edge_cost)) < 1e-6


def test_T2_tek_yol_kapaninca_sapma(sehir):
    G, A, B = sehir
    path, L = shortest_route(G, A, B)
    mid = len(path) // 2
    yolu_kapat(G, path[mid], path[mid + 1])
    assert kapali_kullaniyor(G, path)
    path2, L2 = shortest_route(G, A, B)
    assert path2 is not None and not kapali_kullaniyor(G, path2)
    assert L2 >= L - 1e-6


def test_T3_hepsi_kapali_rota_yok(sehir):
    G, A, B = sehir
    for _, _, d in G.edges(data=True):
        d["closed"] = True
    assert shortest_route(G, A, B) == (None, None)


def test_T4_yol_ortasindaki_bina_yolu_kapatir(sehir):
    G, A, B = sehir
    path, _ = shortest_route(G, A, B)
    u, v = path[len(path) // 2], path[len(path) // 2 + 1]
    edges = ox.graph_to_gdfs(G, nodes=False)
    bina = edges.loc[(u, v, 0), "geometry"].interpolate(0.5, normalized=True).buffer(5)
    n = close_edges_near(G, [bina], R=25)
    assert n >= 1 and kapali_kullaniyor(G, path)
    path2, _ = shortest_route(G, A, B)
    assert path2 is not None and not kapali_kullaniyor(G, path2)


def test_T5_uzaktaki_bina_hicbir_yolu_kapatmaz(sehir):
    G, _, _ = sehir
    assert close_edges_near(G, [Point(0, 0).buffer(5)], R=25) == 0


def test_T8a_gecikme_daha_pahali_rota_sectirmez(sehir):
    G, A, B = sehir
    path, _ = shortest_route(G, A, B)
    u, v = path[len(path) // 2], path[len(path) // 2 + 1]
    edges = ox.graph_to_gdfs(G, nodes=False)
    leke = edges.loc[(u, v, 0), "geometry"].interpolate(0.5, normalized=True).buffer(5)
    m = delay_edges_near(G, [leke], R=25, penalty=100)
    eski = sum(edge_cost(a, b, G[a][b]) for a, b in zip(path[:-1], path[1:]))
    path2, L2 = shortest_route(G, A, B)
    assert m >= 1 and path2 is not None and L2 <= eski + 1e-6


def test_T8b_gecikme_rotayi_yok_etmez(sehir):
    G, A, B = sehir
    for _, _, d in G.edges(data=True):
        d["delay"] = d.get("delay", 0.0) + 1000.0
    assert shortest_route(G, A, B)[0] is not None


def test_T9_temizleme_rotasi(sehir):
    G, A, B = sehir
    for _, _, d in G.edges(data=True):
        d["closed"] = True
    path, temizle = clearing_route(G, A, B)
    assert path is not None and len(temizle) == len(path) - 1
    assert all(edge_cost(u, v, G[u][v]) is None for u, v in temizle)


def test_T10_cizgi_seklindeki_engel_de_yolu_kapatir(sehir):
    # Fay hatti gibi cizgi seklindeki tehlikeler icin: close_edges_near poligon yerine cizgi de alabiliyor mu?
    from shapely.geometry import LineString
    G, A, B = sehir
    path, _ = shortest_route(G, A, B)
    u, v = path[len(path) // 2], path[len(path) // 2 + 1]
    edges = ox.graph_to_gdfs(G, nodes=False)
    p = edges.loc[(u, v, 0), "geometry"].interpolate(0.5, normalized=True)
    fay = LineString([(p.x - 3, p.y - 3), (p.x + 3, p.y + 3)])  # yolu kesen kisa bir cizgi
    assert close_edges_near(G, [fay], R=5) >= 1 and kapali_kullaniyor(G, path)
