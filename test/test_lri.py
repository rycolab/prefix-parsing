import numpy as np
from fastlri.base.cfg import CFG
from fastlri.base.nonterminal import NT
from fastlri.base.symbol import Sym
from fastlri.parsing.parser import Parser


def get_simple_cfg():
    Y = NT("Y")
    Z = NT("Z")
    a = Sym("a")

    cfg = CFG()
    cfg.add(1, cfg.S, Y, Z)
    cfg.add(0.5, Y, Z, Y)
    cfg.add(0.5, Y, a)
    cfg.add(1, Z, a)

    return cfg

def get_complex_cfg():
    NP = NT("NP")
    VP = NT("VP")
    Det = NT("Det")
    N = NT("N")
    PP = NT("PP")
    V = NT("V")
    Adj = NT("Adj")
    Adv = NT("Adv")
    AdvP = NT("AdvP")
    fruit = Sym("fruit")
    flies = Sym("flies")
    like = Sym("like")
    a = Sym("a")
    green = Sym("green")
    banana = Sym("banana")

    cfg = CFG()
    cfg.add(1, cfg.S, NP, VP)
    cfg.add(0.25, NP, Det, N)
    cfg.add(0.25, NP, Det, NP)
    cfg.add(0.25, NP, N, N)
    cfg.add(0.25, NP, Adj, N)
    cfg.add(1, VP, V, NP)
    cfg.add(1, AdvP, Adv, NP)
    cfg.add(0.5, N, fruit)
    cfg.add(0.25, N, flies)
    cfg.add(0.25, N, banana)
    cfg.add(0.5, V, flies)
    cfg.add(0.5, V, like)
    cfg.add(1, Det, a)
    cfg.add(1, Adj, green)
    cfg.add(1, Adv, like)
    
    return cfg

class TestLri:
    def test_plc(self):
        parser = Parser(get_simple_cfg())
        P_L = parser.plc()
        correct = np.array([[1. , 1. , 0.5],\
                            [0. , 1. , 0.5],\
                            [0. , 0. , 1. ]])
        assert np.all(P_L == correct)

    def test_cky(self):
        parser = Parser(get_complex_cfg())
        pins = parser.cky("fruit flies", chart=True)
        assert pins[(NT("N"), 0, 0)] == 0.5
        assert pins[(NT("N"), 1, 1)] == 0.25
        assert pins[(NT("NP"), 0, 1)] == 0.03125

    def test_cky_fast(self):
        parser = Parser(get_complex_cfg())
        pins = parser.cky_fast("fruit flies", chart=True)
        assert pins[(NT("N"), 0, 0)] == 0.5
        assert pins[(NT("N"), 1, 1)] == 0.25
        assert pins[(NT("NP"), 0, 1)] == 0.03125

    
    def test_lri(self):
        parser = Parser(get_simple_cfg())
        ppre = parser.lri("a a a", chart=True)
        assert ppre[(parser.cfg.S, 0, 0)] == 1.0
        assert ppre[(parser.cfg.S, 0, 1)] == 1.0
        assert ppre[(parser.cfg.S, 0, 2)] == 0.5

        parser = Parser(get_complex_cfg())
        ppre = parser.lri("fruit flies", chart=True)
        assert ppre[(parser.cfg.S, 0, 0)] == 0.125
        assert ppre[(parser.cfg.S, 1, 1)] == 0.0625
        assert ppre[(parser.cfg.S, 0, 1)] == 0.03125

    def test_lri_fast(self):
        parser = Parser(get_simple_cfg())
        ppre = parser.lri_fast("a a a", chart=True)
        assert ppre[(parser.cfg.S, 0, 0)] == 1.0
        assert ppre[(parser.cfg.S, 0, 1)] == 1.0
        assert ppre[(parser.cfg.S, 0, 2)] == 0.5

        parser = Parser(get_complex_cfg())
        ppre = parser.lri_fast("fruit flies", chart=True)
        assert ppre[(parser.cfg.S, 0, 0)] == 0.125
        assert ppre[(parser.cfg.S, 1, 1)] == 0.0625
        assert ppre[(parser.cfg.S, 0, 1)] == 0.03125
