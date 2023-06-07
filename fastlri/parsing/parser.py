from fastlri.base.symbol import Sym
import numpy as np
from collections import defaultdict as dd
from fastlri.base.production import Production
from fastlri.base.nonterminal import S

class Parser:
    def __init__(self, cfg):
        self.cfg = cfg
    
    def cky(self, input, chart=False):
            """Calculates the chart of substring probabilities using CKY."""
            # convert input string to list
            if type(input) == str:
                input = [Sym(token) for token in input.split()]
            N = len(input)
            
            # initialization
            β = dd(lambda: 0.0)

            # terminal productions
            for (head, body), w in self.cfg.terminal:
                for k in range(N):
                    if body[0] == input[k]:
                        β[head, k, k] += w

            # binary productions
            for l in range(2, N+1):
                for i in range(N-l+1):
                    k = i + l - 1
                    for j in range(i, k):
                        for p, w in self.cfg.binary:
                            X, Y, Z = p.head, p.body[0], p.body[1]
                            β[X, i, k] += β[Y, i, j] * β[Z, j+1, k] * w
            return β if chart else β[S, 0, N-1]
    
    def cky_fast(self, input, chart=False):
        """A faster version of CKY  for dense grammars."""

        # convert input string to list
        if type(input) == str:
            input = [Sym(token) for token in input.split()]
        N = len(input)

        # initialization
        β = dd(lambda: 0.0)

        # create an index from NT triplets to binary production weights
        W = dd(lambda: 0.0)
        for p, w in self.cfg.binary:
            X, Y, Z = p.head, p.body[0], p.body[1]
            W[X, Y, Z] = w

        # terminal productions
        for (head, body), w in self.cfg.terminal:
            for k in range(N):
                if body[0] == input[k]:
                    β[head, k, k] += w

        # binary productions
        for l in range(2, N+1):
            for i in range(N-l+1):
                k = i + l - 1
                for Y in self.cfg.V:
                    for Z in self.cfg.V:
                        γ = 0.0
                        for j in range(i, k):
                            γ += β[Y, i, j] * β[Z, j+1, k]
                        for X in self.cfg.V:
                            β[X, i, k] += γ * W[X, Y, Z]
        return β if chart else β[S, 0, N-1]

    def plc(self):
        """Computes the left-corner expectations. Requires CNF."""
        assert self.cfg.in_cnf

        # get canonical index over non-terminals
        V = self.cfg.ordered_V
        V_idx = {X:i for i,X in enumerate(V)}

        # calculate the matrix P of one-step derivations
        P = np.zeros((len(V),len(V)))
        for p, w in self.cfg.binary:
            X, Y = V_idx[p.head], V_idx[p.body[0]]
            P[X, Y] += w
        
        # compute the closure over derivations
        P_L = np.linalg.inv(np.eye(len(V), len(V)) - P)
        return P_L
    
    def lri(self, input, chart=False):
        """Original LRI algorithm by Jelinek and Lafferty (1991)."""
        # convert input string to list
        if type(input) == str:
            input = [Sym(token) for token in input.split()]
        
        # initialization
        N = len(input)
        V = self.cfg.ordered_V
        V_idx = {X:i for i,X in enumerate(V)}
        ppre = dd(lambda: 0.0)

        # precompute β using CKY
        β = self.cky(input, chart=True)

        # precompute E
        E = dd(lambda: 0.0)
        P_L = self.plc()
        for X in self.cfg.V:
            for Y in self.cfg.V:
                E[X, Y] = P_L[V_idx[X], V_idx[Y]]

        # precompute E2
        E2 = dd(lambda: 0.0)
        for X in self.cfg.V:
            for (head, body), w in self.cfg.binary:
                Y2, Y, Z = head, body[0], body[1]
                E2[X, Y, Z] += E[X, Y2] * self.cfg._P[Production(Y2, (Y, Z))]

        # compute base case
        for X in self.cfg.V:
            for i in range(N):
                for (head, body), w in self.cfg.terminal:
                    Y, v = head, body[0]
                    if v == input[i]:
                        ppre[X, i, i] += E[X, Y] * w

        # compute prefix probability
        for l in range(2, N+1):
            for i in range(N-l+1):
                k = i + l - 1
                for j in range(i, k):
                    for X in self.cfg.V:
                        for Y in self.cfg.V:
                            for Z in self.cfg.V:
                                ppre[X, i, k] += E2[X, Y, Z] * β[Y, i, j] \
                                    * ppre[Z, j+1, k]
        
        return ppre if chart else ppre[S, 0, N-1]
    
    def lri_fast(self, input, chart=False):
        """Faster prefix parsing algorithm by Nowak and Cotterell (2023)."""
        # convert input string to list
        if type(input) == str:
            input = [Sym(token) for token in input.split()]
        
        # initialization
        N = len(input)
        V = self.cfg.ordered_V
        V_idx = {X:i for i,X in enumerate(V)}
        ppre = dd(lambda: 0.0)

        # precompute β using CKY
        β = self.cky_fast(input, chart=True)

        # precompute E
        E = dd(lambda: 0.0)
        P_L = self.plc()
        for X in self.cfg.V:
            for Y in self.cfg.V:
                E[X, Y] = P_L[V_idx[X], V_idx[Y]]

        # precompute γ and δ
        γ = dd(lambda: 0.0)
        δ = dd(lambda: 0.0)
        for i in range(N):
            for j in range(N):
                for p, w in self.cfg.binary:
                    X, Y, Z = p.head, p.body[0], p.body[1]
                    γ[i, j, X, Z] += w * β[Y, i, j]
                for X in self.cfg.V:
                    for Y in self.cfg.V:
                        for Z in self.cfg.V:
                            δ[i, j, X, Z] += E[X, Y] * γ[i, j, Y, Z]

        # compute base case
        for X in self.cfg.V:
            for i in range(N):
                for p, w in self.cfg.terminal:
                    Y, v = p.head, p.body[0]
                    if v == input[i]:
                        ppre[X, i, i] += E[X, Y] * w

        # compute prefix probability
        for l in range(2, N+1):
            for i in range(N-l+1):
                k = i + l - 1
                for j in range(i, k):
                    for X in self.cfg.V:
                        for Z in self.cfg.V:
                            ppre[X, i, k] += δ[i, j, X, Z] * ppre[Z, j+1, k]
        
        return ppre if chart else ppre[S, 0, N-1]
