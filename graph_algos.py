import heapq

def build_digraph(n, edges):
    # retrun weighted DIrected graph's adj list
    G = {i: [] for i in range(n)}
    for edge in edges:
        G[edge[0]].append((edge[1], edge[2]))
    return G

def lazy_dijkstras(graph, root, end):
    n = len(graph)
    # set up "inf" distances
    dist = [float('inf') for _ in range(n)]
    # set up root distance
    dist[root] = 0
    # set up visited node list
    visited = [False for _ in range(n)]
    prev = [-1 for _ in range(n)]
    # set up priority queue
    pq = [(0, root)]
    # while there are nodes to process
    while len(pq) > 0:
        # get the root, discard current distance
        _, u = heapq.heappop(pq)
        # if the node is visited, skip
        if visited[u]:
            continue
        # set the node to visited
        visited[u] = True
        # check the distance and node and distance
        for v, l in graph[u]:
            # if the current node's distance + distance to the node we're visiting
            # is less than the distance of the node we're visiting on file
            # replace that distance and push the node we're visiting into the priority queue
            if dist[u] + l < dist[v]:
                dist[v] = dist[u] + l
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    path = []
    u = end
    while prev[u] >= 0 or u == root:
        path.append(u)
        u = prev[u]
    path.append(root)
    path = path[::-1]
    return path