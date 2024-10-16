class HashTable(object):
    """
    Represents a hashtable data structure.
    """

    def __init__(self, length=4):
        # for storing items. Initially it's empty.
        self._buckets = [None] * length

    def __hash(self, key):
        """
        Returns hash that represents the index in the buckets
        array for the given key
        """
        length = len(self._buckets)
        return hash(key) % length

    def put(self, key, value):
        """ Inserts add a value in this hashtable. """
        index = self.__hash(key)
        if self._buckets[index] is not None:
            # The index has a bucket; chech whether to update
            # or add as new.
            for kvp in self._buckets[index]:
                # The key exists; so replace value.
                if kvp[0] == key:
                    kvp[1] = value
                    break
            else:
                # No matching key was found; add it with its value to the end.
                self._buckets[index].append([key, value])
        else:
            # The hash index is empty. Create a list and insert the key/value.
            self._buckets[index] = []
            self._buckets[index].append([key, value])

    def get(self, key):
        """ Returns the value pointed to by the given key """
        index = self.__hash(key)
        if self._buckets[index] is None:
            return None
        else:
            # Return the associated value if the given key exists
            # in the bucket pointed by the hash index.
            for kvp in self._buckets[index]:
                if kvp[0] == key:
                    return kvp[1]

            # No matching key was found.
            return None

    def __contains__(self, key):
        for (k, _) in self._buckets[self.__hash(key)]:
            if k == key:
                return True

        return False

    def __iter__(self):
        for bucket in self._buckets:
            yield from bucket
