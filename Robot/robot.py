cells = {
    ' ': 'EMPTY',
    'B': 'BOX',
    'E': 'EXIT',
    'W': 'WALL'
}

class Cell:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'

class Robot:
    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.map = m
        self.keep = False

    def __repr__(self):
        return f'X = {self.x}, Y = {self.y}\n'

    def show(self):
        for i in range(len(self.map)):
            print()
            for j in range(len(self.map[0])):
                if i == self.y and j == self.x:
                    print('R', end='')
                else:
                    if self.map[i][j].type == 'WALL':
                        print('W', end='')
                    elif self.map[i][j].type == 'EMPTY':
                        print(' ', end='')
                    elif self.map[i][j].type == 'BOX':
                        print('B', end='')
                    elif self.map[i][j].type == 'EXIT':
                        print('E', end='')

    def go(self, direction):
        if direction == 'up' and self.map[self.y - 1][self.x].type != 'WALL' and self.map[self.y - 1][self.x].type != 'BOX':
            self.y -= 1
            return True
        elif direction == 'down' and self.map[self.y + 1][self.x].type != 'WALL' and self.map[self.y + 1][self.x].type != 'BOX':
            self.y += 1
            return True
        elif direction == 'left' and self.map[self.y][self.x - 1].type != 'WALL' and self.map[self.y][self.x - 1].type != 'BOX':
            self.x -= 1
            return True
        elif direction == 'right' and self.map[self.y][self.x + 1].type != 'WALL' and self.map[self.y][self.x + 1].type != 'BOX':
            self.x += 1
            return True
        return False

    def exit(self):
        if self.map[self.y][self.x].type == 'EXIT':
            return True
        return False

    def pick(self, direction):
        if direction == 'up' and self.map[self.y - 1][self.x].type == 'BOX' and not self.keep:
            self.map[self.y - 1][self.x].type = 'EMPTY'
            self.keep = True
            return True
        elif direction == 'down' and self.map[self.y + 1][self.x].type == 'BOX' and not self.keep:
            self.map[self.y + 1][self.x].type = 'EMPTY'
            self.keep = True
            return True
        elif direction == 'left' and self.map[self.y][self.x - 1].type == 'BOX' and not self.keep:
            self.map[self.y][self.x - 1].type = 'EMPTY'
            self.keep = True
            return True
        elif direction == 'right' and self.map[self.y][self.x + 1].type == 'BOX' and not self.keep:
            self.map[self.y][self.x + 1].type = 'EMPTY'
            self.keep = True
            return True
        return False

    def drop(self, direction):
        if direction == 'up' and self.map[self.y - 1][self.x].type == 'EMPTY' and self.keep:
            self.map[self.y - 1][self.x].type = 'BOX'
            self.keep = False
            return True
        elif direction == 'down' and self.map[self.y + 1][self.x].type == 'EMPTY' and self.keep:
            self.map[self.y + 1][self.x].type = 'BOX'
            self.keep = False
            return True
        elif direction == 'left' and self.map[self.y][self.x - 1].type == 'EMPTY' and self.keep:
            self.map[self.y][self.x - 1].type = 'BOX'
            self.keep = False
            return True
        elif direction == 'right' and self.map[self.y][self.x + 1].type == 'EMPTY' and self.keep:
            self.map[self.y][self.x + 1].type = 'BOX'
            self.keep = False
            return True
        return False

    def look(self, direction):
        if direction == 'up':
            return self.lookFunc(0, -1)
        elif direction == 'down':
            return self.lookFunc(0, 1)
        elif direction == 'left':
            return self.lookFunc(-1, 0)
        elif direction == 'right':
            return self.lookFunc(1, 0)

    def lookFunc(self, i, j):
        x = self.x + i
        y = self.y + j
        res = list()
        while self.map[y][x].type == 'EMPTY':
            x += i
            y += j
            res.append('EMPTY')
        res.append(self.map[y][x].type)
