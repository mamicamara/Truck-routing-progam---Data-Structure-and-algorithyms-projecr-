from hashtable import HashTable

class Graph:
    """
    A graph structures that uses a hashtable structure to store
    the graph's information (vertices, edges and weight of the edges).
    """
    def __init__(self):
        self.__info = HashTable()

    def add_vertex(self, vertex) -> None:
        """
        Inserts a vertex to this graph
        """
        self.__info.put(vertex, HashTable())

    def add_edge(self, v1, v2, distance: float) -> None:
        """
        Inserts a weighted bidirectional edge between vertex v1 and vertex v2; the
        Weight is the distance between the vertices.
        """
        self.__info.get(v1).put(v2, distance)
        self.__info.get(v2).put(v1, distance)

    def get_distance(self, v1, v2) -> float:
        """
        Returns the distance between vertex v1 and vertex v2.
        """
        return self.__info.get(v1).get(v2)
