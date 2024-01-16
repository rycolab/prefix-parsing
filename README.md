# prefix-parsing

Code accompanying the ACL 2023 publication "[A Fast Algorithm for Computing Prefix Probabilities](https://arxiv.org/abs/2306.02303)".

This repository contains implementations for parsing weighted context free grammars (WCFGs) in chomsky normal form (CNF). 

A context-free grammar is in CNF if the all the rules are in one of the following forms:
```
S -> ε
X -> Y Z
X -> a
``` 
Where S is the distinguished start non-terminal, X, Y, and Z are non-terminals, and a is a terminal.

The methods can be found under `src/parsing/parser.py` implement:
- The CKY algorithm ([Kasami, 1965](https://www.ideals.illinois.edu/items/100444); [Younger,
1967](https://doi.org/https://doi.org/10.1016/S0019-9958(67)80007-X); [Cocke and Schwartz, 1969](https://www.softwarepreservation.org/projects/FORTRAN/CockeSchwartz_ProgLangCompilers.pdf)) for parsing a string under a WCFG in CNF;
- The LRI algorithm  ([Jelinek and Lafferty, 1991](https://aclanthology.org/J91-3004)) for finding the weight of a prefix string under a WCFG in CNF;
- An improved version of the LRI algorithm ([Nowak and Cotterell, 2023](https://arxiv.org/abs/2306.02303)) using additional memoization.

---
To start, run:
```bash
$ git clone git@github.com:rycolab/prefix-parsing.git
$ cd prefix-parsing
$ pip install -e .
```
To unit test, run:
```
pytest .
```
---

## Example usage
First, define a weighted context free grammar as follows:
```python
from fastlri.parsing.parser import Parser
from fastlri.base.cfg import CFG
from fastlri.base.nonterminal import NT
from fastlri.base.symbol import Sym

# define the nonterminals of the grammar
NP = NT("NP")
VP = NT("VP")
Det = NT("Det")
N = NT("N")
PP = NT("PP")
V = NT("V")
Adj = NT("Adj")
Adv = NT("Adv")
AdvP = NT("AdvP")

# define the terminals of the grammar
fruit = Sym("fruit")
flies = Sym("flies")
like = Sym("like")
a = Sym("a")
green = Sym("green")
banana = Sym("banana")

# define the rules of the grammar
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

print(cfg)
```
```
N → fruit	0.5
N → flies	0.25
N → banana	0.25
S → NP VP	1.0
V → like	0.5
V → flies	0.5
NP → N N	0.25
NP → Det N	0.25
NP → Adj N	0.25
NP → Det NP	0.25
VP → V NP	1.0
Adj → green	1.0
Adv → like	1.0
Det → a		1.0
AdvP → Adv NP	1.0
```

Then, create a parser for this CFG:
```python
parser = Parser(cfg)
```

Now you can parse input strings using CKY:
```python
parser.cky("fruit flies like a green banana")
```
```
0.000244140625
```

Similarly for lri and fast lri:
```python
parser.lri("fruit flies like a green banana")
```
```
0.000244140625
```

```python
parser.lri_fast("fruit flies like a green banana")
```
```
0.000244140625
```

For a prefix that has no rooted parse tree under the CFG, cky will return 0, while lri returns a positive probability:

```python
parser.cky("fruit flies like")
```
```
0.0
```

```python
parser.lri_fast("fruit flies like")
```
```
0.015625
```

It is also possible to get the full dynamic programming chart by setting a flag:

```python
parser.lri_fast("fruit flies", chart=True)
```
```
defaultdict(<function fastlri.parsing.parser.Parser.lri_fast.<locals>.<lambda>()>,
            {(N, 0, 1): 0.5,
             (N, 1, 2): 0.25,
             (Adv, 0, 1): 0.0,
             (Adv, 1, 2): 0.0,
             (Det, 0, 1): 0.0,
             (Det, 1, 2): 0.0,
             (VP, 0, 1): 0.0,
             (VP, 1, 2): 0.5,
             (NP, 0, 1): 0.125,
             (NP, 1, 2): 0.0625,
             (S, 0, 1): 0.125,
             (S, 1, 2): 0.0625,
             (AdvP, 0, 1): 0.0,
             (AdvP, 1, 2): 0.0,
             (Adj, 0, 1): 0.0,
             (Adj, 1, 2): 0.0,
             (V, 0, 1): 0.0,
             (V, 1, 2): 0.5,
             (N, 0, 2): 0.0,
             (Adv, 0, 2): 0.0,
             (Det, 0, 2): 0.0,
             (VP, 0, 2): 0.0,
             (NP, 0, 2): 0.03125,
             (S, 0, 2): 0.03125,
             (AdvP, 0, 2): 0.0,
             (Adj, 0, 2): 0.0,
             (V, 0, 2): 0.0})
```

---
## Cite 

If you use this code or the underlying algorithm in your own work, please cite our publication as follows:

Franz Nowak and Ryan Cotterell. 2023. A Fast Algorithm for Computing Prefix Probabilities. In _Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL)_, Toronto, Canada.

```
@inproceedings{nowak-cotterell-2023, 
    author={Franz Nowak and Ryan Cotterell},
    title={A Fast Algorithm for Computing Prefix Probabilities},
    booktitle={Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL)},
    url={https://arxiv.org/abs/2306.02303},
    address={Toronto, Canada},
    year={2023}
}
```



## Contact

For any questions or problems, please file an [issue](https://github.com/rycolab/prefix-parsing/issues) or email [fnowak@ethz.ch](mailto:fnowak@ethz.ch).
