from hashlib import sha256


def _hash(v):
    return sha256(v.encode()).hexdigest()


class Node():
    def get_hash(self):
        return self.hash

    def set_hash(self, hash):
        self.hash = hash


class Leaf(Node):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.hash = _hash(key)


class Branch(Node):
    def __init__(self):
        self.childs = {}
        self.hash = 0

    def recalculate(self):
        k = ''
        for k in self.childs.keys():
            k += self.childs[k].get_hash()

        self.set_hash(_hash(k))


class Tree:

    def __init__(self, level=32, recalculate=True):
        self.root = Branch()
        self.level = level
        self.leaf_mark = 'x'
        self.recalculate = recalculate

    def dump(self, silent=False):
        def dump_branch(branch):
            assert(isinstance(branch, Branch))

            for k in branch.childs.keys():
                if k == self.leaf_mark:
                    leaf = branch.childs[k]
                    assert(isinstance(leaf, Leaf))
                    if not silent:
                        print(f'key:{leaf.key} value:{leaf.value}')
                else:
                    dump_branch(branch.childs[k])

        dump_branch(self.root)

    def _key(self, key: str):
        key = hex(key)[2:].rjust(self.level, '0')
        assert(len(key) >= self.level)

        return key

    def _get_path(self, key: str):
        reversed_key = key[::-1]
        path = []
        for i in range(self.level):
            path.append(reversed_key[i])

        return path

    def _recalculate_path(self, path):
        nodes = []
        current_branch = self.root

        for x in path:
            nodes.append(
                current_branch.childs.get(x)
            )
            current_branch = current_branch.childs[x]
        assert(len(nodes) == self.level)

        for i in range(self.level, 0, -1):
            nodes[i-1].recalculate()

    def _create_leaf(self, key, value):
        path = self._get_path(key)
        current_branch = self.root

        for x in path:
            if current_branch.childs.get(x):
                current_branch = current_branch.childs[x]
            else:
                child = Branch()
                current_branch.childs[x] = child
                current_branch = child

        existing = current_branch.childs.get(self.leaf_mark)
        if existing:
            assert(isinstance(existing, Leaf))
            raise ValueError(
                f'Key {key} collision with {existing.key}'
            )
        else:
            leaf = Leaf(key, value)
            current_branch.childs[self.leaf_mark] = leaf
            if self.recalculate:
                self._recalculate_path(path)

        return leaf

    def _get_leaf(self, key):
        path = self._get_path(key)
        current_branch = self.root
        for x in path:
            if current_branch.childs.get(x):
                current_branch = current_branch.childs[x]
            else:
                return False

        return current_branch.childs.get(self.leaf_mark, False)

    def store(self, key, value):
        key = self._key(key)
        return self._create_leaf(key, value)

    def get(self, key):
        key = self._key(key)

        leaf = self._get_leaf(key)
        if leaf:
            return leaf.value
        else:
            return 0
