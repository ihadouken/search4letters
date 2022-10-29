# pep8 complaint


def search4vowels(word: str) -> set:
	"""Displays vowels inside the phrase."""
	vowels = set('aieou')
	return vowels.intersection(set(word.strip()))


def search4letters(phrase: str, letters: str = 'aieou') -> set:
	"""Displays common characters in two phrases."""
	return set(letters.strip()).intersection(set(phrase.strip()))