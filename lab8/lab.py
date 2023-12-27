"""
6.101 Lab 9:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    Prefix Tree Class
    """

    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if not key:
            self.value = value
        elif len(key) == 1:
            char = key[0]
            if char not in self.children:
                self.children[char] = PrefixTree()
            self.children[char].value = value
        else:
            char = key[0]
            if char not in self.children:
                self.children[char] = PrefixTree()
            self.children[char].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if not key:
            return self.value
        else:
            return self.children[key[0]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        # when do we want to delete the tree? we delete it from it's ancestor
        # dictionary
        if not self.__contains__(key):
            raise KeyError
        if not key:
            self.value = None
        elif len(key) == 1:
            self.children[key[0]].value = None
        else:
            self.children[key[0]].__delitem__(key[1:])

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """

        if not isinstance(key, str):
            raise TypeError

        if not key:
            return self.value is not None
        elif key[0] in self.children:
            return key[1:] in self.children[key[0]]
        else:
            return False

    def __iter__(self, key=""):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        # ok what are we trying to do here?
        # yield all the key value pairs for all (key, values) in the prefix
        # tree

        # base case: if a key has a value, return that value
        if self.value is not None:
            yield (key, self.value)
        if self.children is not None:
            for char, tree in self.children.items():
                yield from tree.__iter__(key + char)


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    tree = PrefixTree()
    words = tokenize_sentences(text)
    for sentence in words:
        for word in sentence.split():
            if word in tree:
                tree[word] += 1
            else:
                tree[word] = 1
    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix. Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    # Use BFS to find the subtree corresponding to the end of the prefix
    node = tree
    for char in prefix:
        if char not in node.children:
            return []  # Prefix not found in the tree

        node = node.children[char]

    # Traverse the subtree for completions
    completions = []
    agenda = [(node, prefix)]

    while agenda:
        current_node, current_prefix = agenda.pop(0)

        if current_node.value is not None:
            completions.append((current_prefix, current_node.value))

        for char, child_node in current_node.children.items():
            agenda.append((child_node, current_prefix + char))

    # Sort in descending order
    completions.sort(key=lambda x: x[1], reverse=True)

    # Return the top max_count elements if max_count
    if max_count is not None:
        completions = completions[:max_count]

    return [word for word, _ in completions]


def autocorrect_helper(tree, prefix):
    poss = set()
    # A single-character insertion (add any one character in the range "a" to "z" at
    # any place in the word)
    for i in range(len(prefix)):
        for char in "abcdefghijklmnopqrstuvwxyz":
            edit = prefix[:i] + char + prefix[i:]
            if edit in tree:
                poss.add((edit, tree[edit]))
    # A single-character deletion (remove any one character from the word)
    for i in range(len(prefix)):
        valid_check = prefix[:i] + prefix[i + 1 :]
        if valid_check in tree:
            poss.add((valid_check, tree[valid_check]))
    # A single-character replacement (replace any one character in the word with a
    # character in the range "a" to "z")
    for i in range(len(prefix)):
        for char in "abcdefghijklmnopqrstuvwxyz":
            checker = prefix[:i] + char + prefix[i + 1 :]
            if checker in tree:
                poss.add((checker, tree[checker]))
    # A two-character transpose (switch the positions of any two adjacent characters in the word)
    for i in range(len(prefix) - 1):
        edit = prefix[:i] + prefix[i + 1] + prefix[i] + prefix[i + 2 :]
        if edit in tree:
            poss.add((edit, tree[edit]))
    return poss


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """

    if max_count is not None:
        if max_count == 0:
            return []
        most_freq_in_tree = autocomplete(tree, prefix, max_count)
        if len(most_freq_in_tree) >= max_count:
            return most_freq_in_tree
        else:
            additional_edits = list(autocorrect_helper(tree, prefix))

            additional_edits.sort(key=lambda x: x[1], reverse=True)
            return most_freq_in_tree + [
                i for i, _ in additional_edits[: max_count - len(most_freq_in_tree)]
            ]
    else:
        most_freq_in_tree = autocomplete(tree, prefix)
        additional_edits = list(autocorrect_helper(tree, prefix))
        return list(set(most_freq_in_tree + [i for i, _ in additional_edits]))


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
          * matches any sequence of zero or more characters,
          ? matches any single character,
          otherwise char in pattern char must equal char in word.
    """

    def pattern_match(word, p):
        # failure base case
        if p == "*":
            return True
        if len(word) != 0 and len(p) == 0 or len(word) == 0 and len(p) != 0:
            return False

        if len(word) == len(p) and len(word) == 0:
            return True
        else:
            pattern_char = p[0]
            if pattern_char == "?":
                return pattern_match(word[1:], p[1:])
            elif pattern_char in "abcdefghijklmnopqrstuvwxyz":
                if word[0] == pattern_char:
                    return pattern_match(word[1:], p[1:])
                else:
                    return False
            elif pattern_char == "*":
                if len(p) == 1:
                    return True
                for i in range(len(word)):
                    if pattern_match(word[i:], p[1:]):
                        return True
                # If no match is found in the loop, try matching the rest of the pattern
                #backtracking
                return pattern_match(word[1:], p[1:])

    matched = []
    for word, val in tree:
        if pattern_match(word, pattern):
            matched.append((word, val))
    return matched



# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("dracula.txt", encoding="utf-8") as f:
        dracula = f.read()

    drac_tree = word_frequencies(dracula)
    x = list(drac_tree.__iter__())
    sums = sum([val for name,val in x])
    print(sums)
    
    

    
    # why are we getting hat instead of car?
