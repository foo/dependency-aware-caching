import random
import logging
import time


class RandomBucket:
    def __init__(self, tree):
        self.cache = []
        self.tree = tree
        random.seed(time.time())

    def reset_buckets(self):
        T = []
        maximal_items = self.find_maximal_items(self.cache)
        for x in maximal_items:
            T.append(x.get_subtree())
        return T

    def find_maximal_items(self, cache):
        maximal_items = []
        for node in cache:
            if node.parent_node not in cache:
                maximal_items.append(node)
        return maximal_items

    def serve_requests(self, request_list, k, l, bypass_cost):
        cost = 0
        T = self.reset_buckets()
        self.cache = []
        for v in request_list:
            logging.info(f"Serving request {v.idx}")
            if v in self.cache:
                logging.debug("    Item Already cached")
                T, cost = self.fetch_item(v, T, k, cost)
                # served v
            else:
                logging.debug("    Item Not Cached")
                w = self.find_minimum_not_cached_node(v)
                logging.debug(f"    Minimum Not Cached Item: {w.idx}")
                S = self.intersection_with_buckets(w, T)
                n = (k/harmonic_number(min(k, l)))**0.5
                if len(S) > n:
                    logging.debug("        Size of S is more than n")
                    T = self.remove_items_from_buckets(int(n), S, T)
                    T = self.remove_frozen_buckets(T)
                    # bypass v
                    logging.info(f"Bypassing request {v.idx}")
                    cost += bypass_cost
                else:
                    T = self.remove_items_of_v_from_buckets(w, T)
                    T = self.remove_frozen_buckets(T)
                    if len(T) == 0:
                        logging.debug("    Resetting Buckets")
                        T = self.reset_buckets()
                        T = self.remove_items_of_v_from_buckets(w, T)
                        T = self.remove_frozen_buckets(T)
                        logging.debug("    Current Buckets:")
                        for bucket in T:
                            logging.debug(f"    - \
                                {list(map(lambda x: x.idx, bucket))}")
                    logging.info(f"Fetching {w.idx} for request {v.idx}")
                    T, cost = self.fetch_item(w, T, k, cost)
                    # if w=v, serve, otherwise:
                    if w != v:
                        # bypass
                        cost += bypass_cost
        return cost

    def remove_items_from_buckets(self, n, S, T):
        S = list(sorted(S, key=lambda x: x.topo_order))
        removable_items = S[0:n]
        for node in removable_items:
            for bucket in T:
                if node in bucket:
                    bucket.remove(node)
        logging.debug("        The following items have been removed from \
            buckets:")
        for node in removable_items:
            logging.debug(f"        - {node.idx}")
        return T

    def fetch_item(self, w, T, k, cost):
        if w not in self.cache:
            if len(self.cache) == k:
                logging.debug("    FetchItem: Cache is full")
                logging.debug("    FetchItem: Current Buckets:")
                for bucket in T:
                    logging.debug(f"    FetchItem: - \
                        {list(map(lambda x: x.idx, bucket))}")
                B = self.choose_bucket(T)
                logging.debug(f"    FetchItem: Chosen bucket: \
                    {list(map(lambda x: x.idx, B))}")
                y = max(B, key=lambda x: x.topo_order)
                logging.debug(f"    FetchItem: Evicting item {y.idx}")
                for bucket in T:
                    if y in bucket:
                        bucket.remove(y)
                T = self.remove_frozen_buckets(T)
                self.cache.remove(y)
            self.cache.append(w)
            logging.debug(f"    FetchItem: Adding Item {w.idx} to cache")
            cost = cost + 1
        return (T, cost)

    def remove_items_of_v_from_buckets(self, v, T):
        v_subtree = v.get_subtree()
        for node in v_subtree:
            for bucket in T:
                if node in bucket:
                    bucket.remove(node)
        return T

    def remove_frozen_buckets(self, T):
        T_new = []
        for bucket in T:
            if len(bucket) != 0:
                T_new.append(bucket)
        return T_new

    def choose_bucket(self, T):
        n = len(T)
        i = random.randint(0, n-1)
        return T[i]

    def find_minimum_not_cached_node(self, v):
        v_subtree = v.get_subtree()
        not_cached = list(filter(lambda x: x not in self.cache, v_subtree))
        w = min(not_cached, key=lambda x: x.topo_order)
        return w

    def intersection_with_buckets(self, w, T):
        w_subtree = w.get_subtree()
        flatten_T = [j for bucket in T for j in bucket]
        S = list(filter(lambda x: x in flatten_T, w_subtree))
        return S


class TreeCaching:
    def __init__(self, tree):
        self.cache = []
        self.tree = tree
        self.not_cached = [node for node in self.tree.nodes]
        self.node_id_dict = self.get_node_id_dict(tree)

    def get_node_id_dict(self, tree):
        id_dict = dict()
        for node in tree.nodes:
            id_dict[node.idx] = node
        return id_dict

    def reset_counter(self):
        # x[i] = [cnt(Pi), |Pi|]
        counter = {k: v for k, v in zip(list(map(lambda x: x.idx,
                                                 self.tree.nodes)),
                                        [[0, 0] for i in
                                         range(len(self.tree.nodes))])}
        keys = list(map(lambda x: x.idx, self.tree.nodes))
        for k in keys:
            counter[k][1] = self.node_id_dict[k].get_size()
        return counter

    def serve_requests(self, request_list, k, bypass_cost):
        cost = 0
        counter = self.reset_counter()
        self.cache = []
        for v in request_list:
            logging.debug(f"Request: {v.idx}")
            if v not in self.cache:
                cost += bypass_cost

                # update request counter
                node = v
                queue = [v, ]
                while node.idx != 0:
                    counter[node.idx][0] += 1
                    if node.idx != 1:
                        queue.insert(0, node.parent_node)
                    node = node.parent_node
                logging.debug("Updated Counter:")
                logging.debug(counter)
                # check if there is any satisfied node
                satisfied = False
                for node in queue:
                    if counter[node.idx][0] >= counter[node.idx][1]:
                        satisfied = True
                        logging.debug(f"Node {node.idx} satisfies the \
                            condition")
                        break

                if satisfied:
                    # fetch the the tree cap rooted at node
                    to_fetch = [i for i in node.get_subtree() if i not in
                                self.cache]
                    to_fetch = sorted(to_fetch, key=lambda x: x.topo_order)
                    if len(to_fetch) + len(self.cache) > k:
                        # cache size exceeded
                        logging.debug("Cache size exceeded!")
                        self.cache = []
                        counter = self.reset_counter()
                    else:
                        for node_fetch in to_fetch:
                            self.cache.append(node_fetch)
                            cost += 1
                            next_node = node_fetch
                            counts = counter[node_fetch.idx][0]
                            while next_node.idx != 0:
                                counter[next_node.idx][0] -= counts
                                counter[next_node.idx][1] -= 1
                                next_node = next_node.parent_node
                        logging.debug("Next Counter:")
                        logging.debug(counter)
        return cost


def harmonic_number(n):
    H = 0
    for i in range(1, n+1):
        H += 1/i
    return H
