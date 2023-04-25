# Search-algorithms-for-TSP
Different implementations of search algorithm used for travelling salesman problem.

We have derived different Agent classes, where every new Agent implements different search algorithm in its get_agent_path method. Search algorithms that are used are:
1. Depth First Search
2. Brute Force Search
3. Branch and Bound algorithm
4. A* algorithm, in which the heuristic function is the minimum spanning tree of the map with coins. Minimum spanning tree is found using Kruskal's algorithm.
