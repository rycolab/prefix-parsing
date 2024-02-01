from collections import defaultdict as dd
from fastlri.base.nonterminal import NT, S
from fastlri.base.symbol import Sym
from fastlri.base.production import Production
from fastlri.base.exceptions import InvalidProduction

class CFG:

    def __init__(self, _S = S):
        # alphabet of terminal symbols Σ
        self.Sigma = set([])

        # non-terminal symbols V
        self.V = set([_S])

        # production rules of the form V × (Σ ∪ V)* × R
        self._P = dd(lambda: 0.0)

        # unique start non-terminal symbol S
        self.S = _S

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
            if head == self.S and body == ():
                # S → ε
                continue
            elif head in self.V and len(body) == 2 and all([elem in self.V \
                    and elem != self.S for elem in body]):
                # A → B C
                continue
            elif head in self.V and len(body) == 1 and body[0] in self.Sigma:
                # A → a
                continue
            else:
                return False
        return True
    
    @property
    def is_pcfg(self) -> bool:
        """Returns whether the grammar is locally normalized."""
        for head in self.V:
            total = 0
            for p, w in self.P:
                if p.head == head:
                    total += w
            if total != 1:
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
            elif isinstance(elem, Sym):
                self.Sigma.add(elem)
            elif elem != ():
                raise InvalidProduction

        self._P[Production(head, body)] += w
    
    @staticmethod
    def from_string(string, comment="#", start='S'):
        import re
        if isinstance(start, str): start = NT(start)
        cfg = CFG(_S = start)
        string = string.replace('->', '→')   # synonym for the arrow
        for line in string.split('\n'):
            line = line.strip()
            if not line or line.startswith(comment): continue
            try:
                [(w, lhs, rhs)] = re.findall('(.*):\s*(\S+)\s*→\s*(.*)$', line)
                lhs = lhs.strip()
                rhs = rhs.strip().split()

                rhs_ = []
                for x in rhs:
                    if x[0].isupper() or x[0].startswith('@'):
                        rhs_.append(NT(x))
                    else:
                        rhs_.append(Sym(x))
                cfg.add(float(w), NT(lhs), *rhs_)

            except ValueError as e:
                raise ValueError(f'bad input line:\n{line}')
        return cfg

    def __str__(self):
        return "\n".join(f"{w}: \t {p}" for (p, w) in sorted(self.P, \
            key=lambda x: (len(str(x[0].head)), str(x[0].head), \
            len(str(x[0])))))
