class NT:

	def __init__(self, X, label=None, n=None):
		self._X = X
		self._label = label

	@property
	def X(self):
		return self._X

	def copy(self):
		return NT(self.X)

	def __repr__(self):
		return f'{self.X}'

	def __hash__(self):
		return hash(self.X)

	def __eq__(self, other):
		return isinstance(other, NT) and self.X == other.X

S = NT("S")