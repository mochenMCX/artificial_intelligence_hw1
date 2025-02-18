import csv
edgeFile = 'edges.csv'


def dfs(start, end):
    # Begin your code (Part 2)
    visited = {}
    visited_note = 0
    data = []
    with open('edges.csv', newline='') as file:
        reader = csv.reader(file)
        for a, b, c, d in reader: # start, end, dist, speed-limit
            if a == 'start':
                continue
            data.append([int(a), int(b), float(c), float(d)])
            visited[int(a)] = False
            visited[int(b)]= False
    raise NotImplementedError("To be implemented")
    # End your code (Part 2)


if __name__ == '__main__':
    path, dist, num_visited = dfs(2270143902, 1079387396)
    print(f'The number of path nodes: {len(path)}')
    print(f'Total distance of path: {dist}')
    print(f'The number of visited nodes: {num_visited}')
