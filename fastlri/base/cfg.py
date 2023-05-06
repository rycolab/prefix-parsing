from collections import defaultdict as dd
from fastlri.base.nonterminal import NT, S
from fastlri.base.symbol import Sym, ε
from fastlri.base.production import Production
from fastlri.base.exceptions import InvalidProduction

class CFG:

    def __init__(self):
        # alphabet of terminal symbols Σ
        self.Sigma = set([])

        # non-terminal symbols V
        self.V = set([S])

        # production rules of the form V × (Σ ∪ V)* × R
        self._P = dd(lambda: 0.0)

        # unique start non-terminal symbol S
        self.S = S

    @property
    def P(self):
        for p, w in self._P.items():
            yield p, w
    
    @property
    def terminal(self):
        """Returns terminal productions of the CFG."""
        for p, w in self.P:
            (head, body) = p
            if len(body) == 1 and isinstance(body[0], Sym):
                yield p, w
    
    @property
    def binary(self):
        """Returns binary productions of the CFG."""
        for p, w in self.P:
            (head, body) = p
            if len(body) == 2 and isinstance(body[0], NT) \
                and isinstance(body[1], NT):
                yield p, w

    @property
    def ordered_V(self):
        """Returns a list of nonterminals ordered by alphabetical index."""
        V = list(self.V)
        V.sort(key=lambda a: str(a.X))
        return V
    
    @property
    def in_cnf(self):
        """Checks if grammar is in CNF."""
        for p, w in self.P:
            (head, body) = p
            if head == self.S and len(body) == 1 and body[0] == ε:
                # S → ε
                continue
            elif head in self.V and len(body) == 2 and all([elem in self.V \
                    and elem != self.S for elem in body]):
                # A → B C
                continue
            elif head in self.V and len(body) == 1 and body[0] in self.Sigma \
                  and body[0] != ε:
                # A → a
                continue
            else:
                return False
        return True
    
    def add(self, w, head, *body):
        """Add a rule to the CFG."""
        if not isinstance(head, NT):
            raise InvalidProduction

        self.V.add(head)

        for elem in body:
            if isinstance(elem, NT):
                self.V.add(elem)
            elif isinstance(elem, Sym) and elem != ε:
                self.Sigma.add(elem)
            elif elem != ε:
                raise InvalidProduction

        self._P[Production(head, body)] += w
    
    def __str__(self):
        return "\n".join(f"{p}\t{w}" for (p, w) in sorted(self.P, \
            key=lambda x: (len(str(x[0].head)), str(x[0].head), \
            len(str(x[0])))))
