import math
import random

import pygame
import os
import config

from queue import PriorityQueue


class Wrapper_for_Priority_Queue:
    def __init__(self, obj):
        self.object = obj

    def __lt__(self, other):
        if self.object[0] < other.object[0]:
            return True
        elif self.object[0] > other.object[0]:
            return False
        else:
            if len(self.object[1]) < len(other.object[1]):
                return False
            elif len(self.object[1]) > len(other.object[1]):
                return True
            else:
                return self.object[1][-1] < other.object[1][-1]


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance: list):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance: list):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class DFS(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance: list):
        path = [0]
        current_coin = 0
        coin_number = len(coin_distance)
        while len(path) < coin_number:
            prices = coin_distance[current_coin]
            coins_with_prices = [(prices[j], j) for j in range(coin_number) if prices[j] != 0]
            coins_with_prices.sort()
            if coins_with_prices[0][1] not in path:
                path.append(coins_with_prices[0][1])
            else:
                k = 0
                while coins_with_prices[k][1] in path and k < coin_number - 1:
                    k += 1
                path.append(coins_with_prices[k][1])
            current_coin = path[-1]
        path.append(0)
        return path


class BruteForce(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_all_paths(self, coin_start, coin_end, coin_distance, visited, path_price, path, paths):
        visited[coin_start] = True
        if len(path) != 0:
            price = coin_distance[path[-1]][coin_start]
        else:
            price = 0
        path_price += price
        path.append(coin_start)
        if coin_start == coin_end and len(path) == len(coin_distance):
            temp = path.copy()
            temp.append(0)
            paths.append((path_price + coin_distance[path[-1]][0], temp))
        else:
            for i in range(len(coin_distance)):
                if not visited[i]:
                    self.get_all_paths(i, coin_end, coin_distance, visited, path_price, path, paths)
        path.pop()
        path_price -= price
        visited[coin_start] = False

    def get_agent_path(self, coin_distance: list):
        paths = []
        coin_number = len(coin_distance)
        for i in range(1, coin_number):
            path = []
            path_price = 0
            visited = [False] * coin_number
            self.get_all_paths(0, i, coin_distance, visited, path_price, path, paths)
        path = min(paths)
        return path[1]


class BranchBound(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance: list):
        pq = PriorityQueue()
        tmp = Wrapper_for_Priority_Queue((0, [0]))
        pq.put(tmp)
        coin_number = len(coin_distance)
        while not pq.empty():
            tmp = pq.get()
            partial_price = tmp.object[0]
            partial_path = tmp.object[1]
            if len(partial_path) == coin_number + 1:
                return partial_path
            elif len(partial_path) == coin_number:
                partial_price += coin_distance[partial_path[-1]][0]
                partial_path.append(0)
                tmp = Wrapper_for_Priority_Queue((partial_price, partial_path))
                pq.put(tmp)
            else:
                prices = coin_distance[partial_path[-1]]
                for i in range(1, coin_number):
                    price = prices[i]
                    if price > 0 and i not in partial_path:
                        new_partial_path = partial_path.copy()
                        new_partial_path.append(i)
                        new_partial_price = partial_price + price
                        tmp = Wrapper_for_Priority_Queue((new_partial_price, new_partial_path))
                        pq.put(tmp)


class AStar(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def is_connected(self, u, v, connected, path):
        result = False
        for i in range(len(connected)):
            if connected[u][i] and i not in path:
                if i == v:
                    return True
                else:
                    path.append(i)
                    result = self.is_connected(i, v, connected, path)
                    if result:
                        break
                    path.pop()
        return result

    def get_min_spanning_tree(self, coin_distance, path):
        coin_number = len(coin_distance)
        if len(path) >= 2:
            excluded_coins = path[1:-1]
        else:
            excluded_coins = []
        price = 0
        included_coins = []
        connected = [[False for count in range(coin_number)] for count in range(coin_number)]

        branches = []
        for i in range(coin_number - 1):
            for j in range(i + 1, coin_number):
                branches.append((coin_distance[i][j], i, j))
        branches.sort(key=lambda x: x[0])

        num = 0
        while num < coin_number - len(excluded_coins) - 1:
            (branch_price, coin1, coin2) = branches.pop(0)
            if coin1 not in excluded_coins and coin2 not in excluded_coins:
                if not self.is_connected(coin1, coin2, connected, [coin1]):
                    if coin1 not in included_coins:
                        included_coins.append(coin1)
                    if coin2 not in included_coins:
                        included_coins.append(coin2)
                    price += branch_price
                    connected[coin1][coin2] = True
                    connected[coin2][coin1] = True
                    num += 1
        return price

    def get_agent_path(self, coin_distance: list):
        paths = [(0, 0, [0])]
        coin_number = len(coin_distance)
        while len(paths) > 0:
            (price_with_mst, partial_price, partial_path) = paths.pop(0)
            if len(partial_path) == coin_number + 1:
                return partial_path
            elif len(partial_path) == coin_number:
                partial_price += coin_distance[partial_path[-1]][0]
                partial_path.append(0)
                paths.append((partial_price, partial_price, partial_path))
            else:
                prices = coin_distance[partial_path[-1]]
                for i in range(1, coin_number):
                    price = prices[i]
                    if price > 0 and i not in partial_path:
                        new_partial_path = partial_path.copy()
                        new_partial_path.append(i)
                        new_mst_price = self.get_min_spanning_tree(coin_distance, new_partial_path)
                        new_partial_price = partial_price + price
                        new_price_with_mst = new_partial_price + new_mst_price
                        paths.append((new_price_with_mst, new_partial_price, new_partial_path))
            paths.sort(key=lambda x: (x[0], -len(x[2]), x[2][-1]))
