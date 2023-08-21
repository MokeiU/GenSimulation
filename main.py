import math
import sys

import pygame
from random import randint
from button_module import Button

pygame.init()

MAX_IQ = 3

ENERGY_PER_CYCLE = 5
ENERGY_TO_CHILD = 50
ENERGY_TO_MOVE = 10
ENERGY_TO_ATTACK = 20
ENERGY_TO_BOOST_AGE = 5
ENERGY_TO_ROTATE = 0
ENERGY_FROM_PHOTOSYNTHESIS = 40

MAX_AGE = 1000
MAX_AGE_BOOST = 10
agents_count = 100

click = []
WINX, WINY = 1920, 1080
window = pygame.display.set_mode((WINX, WINY), pygame.FULLSCREEN)
pygame.display.set_caption("Gen")
GX, GY = 80, 50
MAP = [[False for j in range(GY)] for i in range(GX)]
INC_SIZE = 16
GRAY_COLOR = (50, 50, 50)
ADD = 80
FPS = 999
cycle = 0

show_mode = "STANDARD"
'''
STANDARD
PREDATOR
AGE
'''

buttons = []
font64 = pygame.font.Font(None, 64)
font32 = pygame.font.Font(None, 32)
mutate_chance = 3  # 20 % = 1/5
clock = pygame.time.Clock()
agents = []
directed_genes = 3
GEN_CHILD = "GEN_CHILD"
GEN_MOVE = "GEN_MOVE"
GEN_ATTACK = "GEN_ATTACK"
GEN_SYNTEZ = "GEN_SYNTEZ"
GEN_ROTATE = "GEN_ROTATE"
GEN_AGE_BOOST = "GEN_AGE_BOOST"


GENS = [
    GEN_CHILD,
    GEN_MOVE,
    GEN_ATTACK,
    GEN_SYNTEZ,
    GEN_ROTATE,
    GEN_AGE_BOOST
]
genes = [
    GEN_CHILD,
    GEN_MOVE,
    GEN_ATTACK,
    GEN_SYNTEZ,
    GEN_ROTATE,
    GEN_AGE_BOOST
]
# genes = [
#     0,
#     10,
#     20,
#     30,
#     40,
#     50,
# ]
'''
0 - потомство
10 - передвижение
20 - атака
30 - фотосинтез
40 - поворот
50 - долгожительство
'''


def click_map():
    dist = 0
    mx, my = pygame.mouse.get_pos()
    px, py = -1, -1
    for i in range(GX + 1):
        for j in range(GY + 1):
            x, y, h, w = click[i][j]
            if x < mx < x + h and y < my < y + w:
                px, py = i, j
            else:
                new_dist = abs(x + h - mx) + abs(y + w - my)
                if new_dist < dist:
                    dist = new_dist
                    px, py = i, j
    return px, py


class Agent:
    ENERGY_CHANGE = {
        GEN_CHILD: ENERGY_TO_CHILD,
        GEN_MOVE: ENERGY_TO_MOVE,
        GEN_ATTACK: ENERGY_TO_ATTACK,
        GEN_SYNTEZ: -ENERGY_FROM_PHOTOSYNTHESIS,
        GEN_ROTATE: ENERGY_TO_ROTATE,
        GEN_AGE_BOOST: ENERGY_TO_BOOST_AGE,
    }

    @staticmethod
    def dir_to_v(direct: int) -> (int, int):
        vx, vy = 0, 0
        if direct in [1, 2, 3]:
            vx = 1
        elif direct in [5, 6, 7]:
            vx = -1
        if direct in [0, 1, 7]:
            vy = 1
        elif direct in [3, 4, 5]:
            vy = -1
        return vx, vy

    def __init__(self, x: int, y: int, r: int, g: int, b: int, iq: int, genes: list, id: int, energy=100):
        """
        :param x: x coordinate (from 0 to GX)
        :param y: y coordinate (from 0 to GY)
        :param r: red color (from 0 to 255)
        :param g: green color (from 0 to 255)
        :param b: blue color (from 0 to 255)
        :param iq: genes count
        :param genes: list with genes
        :param id: unique Agent id
        :param energy: energy to actions
        """
        self.cords = x, y
        self.color = min(max(r, 0), 255), min(max(g, 0), 255), min(max(b, 0), 255)
        self.iq = iq
        self.genes = genes
        self.energy = energy
        self.id = id
        self.age = 0

    @staticmethod
    def random_gen(iq: int) -> list:
        new_genes = []
        for _ in range(iq):
            new_gen_number = randint(1, len(genes))
            new_gen_id = genes[new_gen_number - 1]
            new_gen_arg = None
            if new_gen_number <= directed_genes:
                new_gen_arg = randint(0, 7)
            elif new_gen_number == 5:
                new_gen_arg = randint(1, 100)
            new_genes.append([new_gen_id, new_gen_arg])
        return new_genes

    def get_mutate_genes(self, chance: int) -> (int, list, list):
        new_genes = []
        new_iq = self.iq
        mutate_count = 0
        r, g, b = self.color
        for gen in self.genes:
            x1 = randint(1, 100)
            if x1 <= chance:
                mutate_count += 1
                x2 = randint(1, 2 + len(genes))
                if x2 == 1:  # deleting gen
                    new_iq -= 1
                    continue
                if x2 == 2 and new_iq < MAX_IQ:
                    new_iq += 1
                    dop_gen = Agent.random_gen(1)[0]
                    new_genes.append(dop_gen)
                new_genes.append(Agent.random_gen(1)[0])
            else:
                new_genes.append(gen)
        for i in range(mutate_count):
            x3 = randint(1, 3)
            x4 = -20 if randint(1, 2) == 1 else 20
            if x3 == 1:
                r += x4
            elif x3 == 2:
                g += x4
            else:
                b += x4
        new_color = r, g, b
        # print(f"color mutate: {new_color}")
        return new_iq, new_genes, new_color

    def step(self):
        self.age += 1
        self.energy -= ENERGY_PER_CYCLE
        max_age_buster = 0
        for gen in self.genes:
            gen_id = gen[0]
            gen_arg = gen[1]
            result = True
            if gen_id == GEN_CHILD:
                if self.energy >= ENERGY_TO_CHILD:
                    result = self.child(Agent.dir_to_v(gen_arg))
                    if result:
                        self.energy = self.energy // 2
            elif gen_id == GEN_MOVE:
                if self.energy >= ENERGY_TO_ROTATE:
                    result = self.move(Agent.dir_to_v(gen_arg))
            elif gen_id == GEN_ATTACK:
                self.energy += self.attack(Agent.dir_to_v(gen_arg))
            elif gen_id == GEN_ROTATE:
                self.rotate_right(gen_arg)
            elif gen_id == GEN_AGE_BOOST:
                max_age_buster += MAX_AGE_BOOST

            if result:
                self.energy -= self.ENERGY_CHANGE[gen_id]

        if self.energy <= 0 or self.age >= MAX_AGE + max_age_buster:
            x, y = self.cords
            MAP[x][y] = False
            agents.remove(self)

    def move(self, v) -> bool:
        x, y = self.cords
        nx, ny = (x + v[0]) % GX, (y + v[1]) % GY
        if not MAP[nx][ny]:
            self.cords = nx, ny
            MAP[nx][ny] = self.id
            MAP[x][y] = False
            return True
        return False

    def attack(self, v) -> int:
        x, y = self.cords
        nx, ny = (x + v[0]) % GX, (y + v[1]) % GY
        if MAP[nx][ny]:
            agent_id = MAP[nx][ny]
            for agent in agents:
                if agent.id == agent_id:
                    v_energy = agent.energy
                    # print(f"attack {agent.id} for {v_energy} energy")
                    agents.remove(agent)
                    MAP[nx][ny] = False
                    return v_energy
        return 0

    def child(self, v: tuple) -> bool:
        x, y = self.cords
        nx, ny = (x + v[0]) % GX, (y + v[1]) % GY
        if not bool(MAP[nx][ny]):
            iq, genes, color = self.get_mutate_genes(mutate_chance)
            r, g, b = color
            new_agent = Agent(nx, ny, r, g, b, iq, genes, agents[-1].id + 1, energy=self.energy // 2)
            agents.append(new_agent)
            MAP[nx][ny] = new_agent.id
            return True
        return False

    def rotate_right(self, chance: int):
        new_genes = []
        for gen in self.genes:
            if gen[0] in [GEN_SYNTEZ, GEN_ROTATE, GEN_AGE_BOOST]:
                continue
            if randint(1, 100) <= chance:
                new_genes.append([gen[0], (gen[1] + 1) % 8])
            else:
                new_genes.append(gen)
        self.genes = new_genes


selected_agent_id = None
selected_agent = None


def check_events():
    global selected_agent_id
    for agent in agents:
        if selected_agent_id is not None:
            if agent.id == selected_agent_id:
                global selected_agent
                selected_agent = agent

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            key = event.key
            global SPEED
            if key == pygame.K_1:
                SPEED = 1
            elif key == pygame.K_2:
                SPEED = 5
            elif key == pygame.K_3:
                SPEED = 20
            elif key == pygame.K_4:
                SPEED = 999
            elif key == pygame.K_q:
                exit()

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        px, py = click_map()
        if px != -1 and mx < click[-1][-1][1] and my < click[-1][-1][0]:
            # global selected_agent_id
            selected_agent_id = MAP[px][py]
            # print(f"selected {selected_agent_id} ---> {px}:{py}")
    for button in buttons:
        button.check()


def agents_step():
    for agent in agents:
        agent.step()


def draw_objects():
    def draw_arrow(direction: int, sp: tuple, ep: tuple, ap: tuple, width: int, color: tuple, surface: pygame.Surface):
        sx, sy = sp
        ex, ey = ep
        px, py = ap
        tmp = 8
        if direction == 0:
            pygame.draw.line(surface, color, sp, ep, width - 1)
            pygame.draw.line(surface, color, sp, (sx + px, sy + py), width)
            pygame.draw.line(surface, color, sp, (sx - px, sy + py), width)
        # elif direction == 1: # Todo
        #     pygame.draw.line(surface, color, (sx + SPEED, sy), (ex - SPEED, ey), width)
        #     pygame.draw.line(surface, color, (sx + SPEED, sy), (sx + SPEED, sy + py * 2), width - 1)
        #     pygame.draw.line(surface, color, (sx + SPEED, sy), (sx - px, sy), width - 1)
        # elif direction == 2:
        #     pygame.draw.line(surface, color, (sx - SPEED + 1, sy + SPEED + 1), (sx + SPEED, sy + SPEED + 1), width - 1)
        #     pygame.draw.line(surface, color, (sx + SPEED + 1, sy + SPEED + 1), (sx, sy + SPEED * 2), width - 1)
        #     pygame.draw.line(surface, color, (sx + SPEED + 1, sy + SPEED + 1), (sx, sy + 2), width - 1)
        # elif direction == 4:
        #     pygame.draw.line(surface, color, sp, ep, width - 1)
        #     pygame.draw.line(surface, color, ep, (sx + px, sy + py), width)
        #     pygame.draw.line(surface, color, ep, (sx - px, sy + py), width)

    global selected_agent

    window.fill((0, 0, 0))

    for i, line in enumerate(MAP):
        for j, tile in enumerate(line):
            x, y = i + ADD + (i - 1) * INC_SIZE, j + ADD + (j - 1) * INC_SIZE
            pygame.draw.rect(window, GRAY_COLOR, (x, y, 12, 12))

    if show_mode == "STANDARD":
        for agent in agents:
            i, j = agent.cords
            r, g, b = agent.color
            x, y = (i + ADD + (i - 1) * INC_SIZE, j + ADD + (j - 1) * INC_SIZE)
            pygame.draw.rect(window, (r, g, b), (x, y, 12, 12))
            if agent.id == selected_agent_id:
                pygame.draw.rect(window, (0, 255, 0), (x, y, 12, 12), 2)

    elif show_mode == "PREDATOR":
        for agent in agents:
            i, j = agent.cords
            x, y = (i + ADD + (i - 1) * INC_SIZE, j + ADD + (j - 1) * INC_SIZE)
            r, g, b = 0, 255, 0
            for gen in agent.genes:
                if gen[0] == GEN_ATTACK:
                    r += 102
                    g -= 102
            r, g = min(max(r, 0), 255), min(max(g, 0), 255)
            if agent.id == selected_agent_id:
                pygame.draw.rect(window, (0, 0, 255), (x, y, 12, 12), 2)
            else:
                pygame.draw.rect(window, (r, g, 0), (x, y, 12, 12))

    elif show_mode == "AGE":
        for agent in agents:
            i, j = agent.cords
            x, y = (i + ADD + (i - 1) * INC_SIZE, j + ADD + (j - 1) * INC_SIZE)
            max_age_agent = MAX_AGE
            for gen in agent.genes:
                if gen[0] == GEN_AGE_BOOST:
                    max_age_agent += MAX_AGE_BOOST
            tmp = 1 / (max_age_agent - agent.age if max_age_agent - agent.age != 0 else 1) * 25
            tmp = min(max(tmp, 0), 255)
            r, b = tmp, tmp

            if agent.id == selected_agent_id:
                pygame.draw.rect(window, (255, 0, 0), (x, y, 12, 12), 2)
            else:
                pygame.draw.rect(window, (r, 0, b), (x, y, 12, 12))


    x, y, h, w, size = WINX - 220, WINY - 480, 200, 320, 6
    pygame.draw.line(window, GRAY_COLOR, (x, y), (x, y + w), size)
    pygame.draw.line(window, GRAY_COLOR, (x + h, y), (x + h, y + w), size)
    pygame.draw.line(window, GRAY_COLOR, (x, y), (x + h, y), size)
    pygame.draw.line(window, GRAY_COLOR, (x, y + w), (x + h, y + w), size)
    if not selected_agent_id:
        selected_agent = None
    if selected_agent is not None:
        for id, gen in enumerate(selected_agent.genes):
            row, line = id % 10, math.floor(id / 10)

            bx, by = 15, 15
            gen_id = gen[0]
            gen_arg = gen[1]
            pos = x + bx + row * 20, y + by + line * 20
            if gen_id == GEN_CHILD:  # child
                pygame.draw.circle(window, (255, 255, 255), pos, 10)
                arrow_start_point = x + bx + id * 20 - 1, y + 5
                arrow_end_point = x + bx + id * 20 - 1, y + 24
                draw_arrow(gen_arg, arrow_start_point, arrow_end_point, (5, 8), 5, (255, 0, 0), window)
            if gen_id == GEN_MOVE:  # move
                pygame.draw.circle(window, (0, 0, 255), pos, 10)
            if gen_id == GEN_ATTACK:  # attack
                pygame.draw.circle(window, (255, 0, 0), pos, 10)
            if gen_id == GEN_SYNTEZ:  # eat
                pygame.draw.circle(window, (0, 255, 0), pos, 10)
            if gen_id == GEN_ROTATE:  # rotate
                pygame.draw.circle(window, (100, 100, 255), pos, 10)
            if gen_id == GEN_AGE_BOOST:  # age boost
                pygame.draw.circle(window, (100, 0, 255), pos, 10)

    for button in buttons:
        button.draw()


def draw_text():
    def draw_current_cycle():
        text = "CYCLE: " + str(cycle)
        window.blit(font64.render(text, True, (255, 255, 255)), (WINX - len(str(cycle)) * 25 - 180, 20))

    def draw_speed():
        global SPEED
        speed = SPEED
        speed_cords = WINX - 225 if speed < 99 else WINX - 300, 80
        text = "SPEED: " + str(speed)
        window.blit(font64.render(text, True, (255, 255, 255)), speed_cords)

    def draw_fps():
        fps = clock.get_fps()
        fps_cords = WINX - 175 if fps < 99 else WINX - 225, 140
        text = "FPS: " + str(round(fps))
        window.blit(font64.render(text, True, (255, 255, 255)), fps_cords)

    def draw_mouse_pos():
        pos = pygame.mouse.get_pos()
        text = str(pos)
        if len(text) < 8:
            pos_cords = WINX - 125, WINY - 80
        elif len(text) < 11:
            pos_cords = WINX - 200, WINY - 80
        else:
            pos_cords = WINX - 250, WINY - 80
        window.blit(font64.render(text, True, (255, 255, 255)), pos_cords)

    def draw_current_agents_count():
        len_agents = len(agents)
        x = 1820
        if len_agents < 9:
            x = 1880
        elif len_agents < 99:
            x = 1860
        elif len_agents < 999:
            x = 1840
        x -= 220
        agents_cords = x, 200
        text = "AGENTS: " + str(len_agents)
        window.blit(font64.render(text, True, (255, 255, 255)), agents_cords)

    def draw_mouse_line_column():
        px, py = click_map()
        window.blit(font64.render(f"{px}/{py}", True, (255, 255, 255)), (WINX - 120, WINY - 540))

    def draw_agent_info():
        if selected_agent is not None:
            x, y, bx, by = WINX - 220, WINY - 480, 9, 6
            for id, gen in enumerate(selected_agent.genes):
                if gen[1] is not None:
                    if gen[0] == 0:
                        continue
                        # window.blit(font32.render(f"{gen[1]}", True, (50, 50, 50)), (x + bx + id * 20, y + by))
                    elif gen[0] != 20:
                        window.blit(font32.render(f"{gen[1]}", True, (200, 200, 200)), (x + bx + id * 20, y + by))
                    else:
                        window.blit(font32.render(f"{gen[1]}", True, (0, 0, 0)), (x + bx + id * 20, y + by))

            x, y = selected_agent.cords
            window.blit(font64.render(f"X:{x}", True, (255, 255, 255)), (1715, 670))
            window.blit(font64.render(f"Y:{y}", True, (255, 255, 255)), (1715, 720))
            window.blit(font64.render(f"EN:{selected_agent.energy}", True, (255, 255, 255)), (1715, 770))
            window.blit(font64.render(f"AGE:{selected_agent.age}", True, (255, 255, 255)), (1715, 820))

            if MAP[x][y] != selected_agent.id:
                window.blit(font64.render(f"DEAD", True, (200, 0, 0)), (1715, 870))

    draw_current_cycle()
    draw_speed()
    draw_fps()
    draw_mouse_pos()
    draw_current_agents_count()
    draw_mouse_line_column()
    draw_agent_info()


def start():
    def calculate_window_grid(p: int, g: int) -> (int, int, int, int):
        x, y = (p - 1) * 17 + 80, (g - 1) * 17 + 80
        h, w = 12, 12
        return x, y, x + h, y + w

    def get_free_place_cords() -> (int, int):
        x, y = randint(0, GX - 1), randint(0, GY - 1)
        while bool(MAP[x][y]):
            x, y = randint(0, GX - 1), randint(0, GY - 1)
        return x, y

    global agents_count
    if len(agents) == 0:
        x, y = get_free_place_cords()
        iq = 3
        new_agent = Agent(x, y, 255, 255, 255, iq, Agent.random_gen(iq), 1)
        agents.append(new_agent)
        agents_count -= 1

        MAP[x][y] = agents[-1].id

    for i in range(agents_count):
        x, y = get_free_place_cords()
        iq = MAX_IQ
        new_agent = Agent(x, y, 255, 255, 255, iq, Agent.random_gen(iq), agents[-1].id + 1)
        agents.append(new_agent)

        MAP[x][y] = agents[-1].id

    for i in range(0, GX + 1):
        click.append([])
        for j in range(0, GY + 1):
            click[i].append(calculate_window_grid(i, j))

    def button_set_predator_show_mode():
        global show_mode
        show_mode = "PREDATOR"

    def button_set_standard_show_mode():
        global show_mode
        show_mode = "STANDARD"

    def button_set_age_show_mode():
        global show_mode
        show_mode = "AGE"

    global buttons
    buttons = [
        Button(button_set_predator_show_mode, button_set_standard_show_mode, window, (WINX - 120, WINY - 140, 40, 40),
               (255, 150, 150)),
        Button(button_set_age_show_mode, button_set_standard_show_mode, window, (WINX - 180, WINY - 140, 40, 40),
               (150, 150, 255)),
    ]
    global selected_agent_id
    selected_agent_id = agents[0].id


def clear():
    pygame.display.flip()

    global cycle
    cycle += 1


start()
SPEED = 20
while True:
    if cycle % SPEED == 0:
        agents_step()
        clock.tick(FPS)
    draw_objects()
    check_events()
    draw_objects()
    draw_text()
    clear()
