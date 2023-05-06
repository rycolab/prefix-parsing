import numpy as np
from fastlri.base.cfg import CFG
from fastlri.base.nonterminal import NT
from fastlri.base.symbol import Sym
from fastlri.parsing.parser import Parser

Y = NT("Y")
Z = NT("Z")
a = Sym("a")

cfg = CFG()
cfg.add(1, cfg.S, Y, Z)
cfg.add(0.5, Y, Z, Y)
cfg.add(0.5, Y, a)
cfg.add(1, Z, a)
parser = Parser(cfg)

class TestLri:
    def test_plc(self):
        P_L = parser.plc()
        correct = np.array([[1. , 1. , 0.5],\
                            [0. , 1. , 0.5],\
                            [0. , 0. , 1. ]])
        assert np.all(P_L == correct)

    def test_lri(self):
        ppre = parser.lri([a,a,a], chart=True)
        assert ppre[(parser.cfg.S, 0, 1)] == 1.0
        assert ppre[(parser.cfg.S, 0, 2)] == 1.0
        assert ppre[(parser.cfg.S, 0, 3)] == 0.5
        

    def test_lri_fast(self):
        ppre = parser.lri_fast([a,a,a], chart=True)
        assert ppre[(parser.cfg.S, 0, 1)] == 1.0
        assert ppre[(parser.cfg.S, 0, 2)] == 1.0
        assert ppre[(parser.cfg.S, 0, 3)] == 0.5
