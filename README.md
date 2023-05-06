# prefix-parsing

This repository contains implementations for parsing weighted context free grammars (WCFGs). 

The methods can be found under src/parsing/parser.py implement:
- The CKY algorithm (Kasami, 1965; Younger,
1967; Cocke, 1969) for parsing a string under a WCFG;
- The LRI algorithm  (Jelinek and Lafferty, 1991) for finding the weight of a prefix string under a WCFG;
- An improved version of the LRI algorithm (Nowak and Cotterell, 2023) using additional memoization.

To start, run:
```bash
$ git clone git@github.com:franznowak/prefix-parsing.git
$ cd prefix-parsing
$ pip install -e .
```
To unit test, run:
```
pytest .
```

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

Then, call the parser on an example input:
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
