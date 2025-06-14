import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import pygame
from envs.constants import config
import time
from q_learning.constants import DEBUG_UPDATE

UP = "↑"
DOWN = "↓"
LEFT = "←"
RIGHT = "→"
PUT_OUT_FIRE = "🔥"


class Visualizer:
    _pause = False

    def __init__(self, grid_shape, num_actions):
        self._debug_update = DEBUG_UPDATE

        self.grid_shape = grid_shape
        self.num_actions = num_actions

        plt.ion()
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 10))
        self.fig.tight_layout()

        self.q = QValuePlot(self.axes[1][1])
        self.td_error = Axis("TD Error", "Error", "red", self.axes[0][0])
        self.epsilon = Axis("Epsilon", "Epsilon", "blue", self.axes[0][1])

        self.ax3 = self.axes[1][0]
        self.ax3.clear()
        self.ax3.set_title("Max Q-values")
        q_values = np.zeros(self.grid_shape)
        self.heatmap = self.ax3.imshow(q_values, cmap="viridis")
        self.fig.colorbar(self.heatmap, ax=self.ax3)
        self.counter = 0

    def update(self, q_table, epsilon, td_error, target, is_fire_on):
        self.counter += 1
        if self.counter == self._debug_update:
            self.counter = 0
        else:
            return

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self._pause = not self._pause
                elif event.key == pygame.K_LEFT:
                    self._debug_update -= 1
                elif event.key == pygame.K_RIGHT:
                    self._debug_update += 1

        if self._pause:
            pygame.display.flip()
            time.sleep(1)
            return self.update(q_table, epsilon, td_error, target, is_fire_on)

        self.q.update(q_table, target, is_fire_on)
        self.td_error.update(td_error)
        self.epsilon.update(epsilon)

        # q_values = np.zeros(self.grid_shape)
        # for x in range(config.grid_size):
        #     for y in range(config.grid_size):
        #         # q_values[x, y] = np.max(q_table[idx])
        #         idx = get_values(q_table, ((x, y), target, is_fire_on))
        # self.heatmap.set_data(q_values)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class Axis:
    def __init__(self, title, y_label, color, axis):
        self.data = []

        self.axis = axis
        self.axis.clear()
        self.axis.set_title(title)
        self.axis.set_xlabel("Step")
        self.axis.set_ylabel(y_label)
        self.axis.grid(True)
        (self.line,) = self.axis.plot(self.data, label="Step", color=color)

    def update(self, data):
        self.data.append(data)
        self.line.set_ydata(self.data)
        self.line.set_xdata(range(len(self.data)))

        self.axis.relim()
        self.axis.autoscale_view()


class QValuePlot:

    def __init__(self, axis):
        self.texts = {}
        self.ax = axis
        self.ax.set_xlim(0, config.grid_size)
        self.ax.set_ylim(0, config.grid_size)
        self.ax.set_xticks(np.arange(0, config.grid_size + 1))
        self.ax.set_yticks(np.arange(0, config.grid_size + 1))
        self.ax.grid(True)
        self.ax.invert_yaxis()
        self.ax.set_title("Q-Table Action Values")

        self.vmin = -10
        self.vmax = 10
        self.cmap = plt.get_cmap("viridis")
        self.norm = mcolors.Normalize(vmin=-10, vmax=10)

        # Initialize all text annotations (one per direction per cell)
        for x in range(config.grid_size):
            for y in range(config.grid_size):
                cx, cy = y + 0.5, x + 0.5
                self.texts[(x, y)] = {
                    UP: self.ax.text(
                        cx, cy - 0.3, "", ha="center", va="center", fontsize=8
                    ),
                    RIGHT: self.ax.text(
                        cx + 0.3, cy, "", ha="center", va="center", fontsize=8
                    ),
                    DOWN: self.ax.text(
                        cx, cy + 0.3, "", ha="center", va="center", fontsize=8
                    ),
                    LEFT: self.ax.text(
                        cx - 0.3, cy, "", ha="center", va="center", fontsize=8
                    ),
                    PUT_OUT_FIRE: self.ax.text(
                        cx, cy, "", ha="center", va="center", fontsize=8
                    ),
                    "best": self.ax.text(
                        cx - 0.3, cy - 0.3, "", ha="center", va="center", fontsize=8
                    ),
                }

    def update(self, q_table, target, is_fire_on):
        for x in range(config.grid_size):
            for y in range(config.grid_size):
                values = get_values(q_table, (((x, y), target, is_fire_on)))

                max = {"val": 0, "action": ""}
                for direction, value in zip(
                    [RIGHT, UP, LEFT, DOWN, PUT_OUT_FIRE], values
                ):
                    if value > max["val"]:
                        max["val"] = value
                        max["action"] = direction
                    color = self.cmap(self.norm(value))
                    text_obj = self.texts[(x, y)][direction]
                    text_obj.set_text(f"{value:.1f}")
                    text_obj.set_color(color)

                color = self.cmap(self.norm(max["val"]))
                text_obj = self.texts[(x, y)]["best"]
                text_obj.set_text(f"{max['action']}")
                text_obj.set_color(color)


def get_values(q_table, observation):
    return q_table[observation[1][0]][observation[1][1]][1 if observation[2] else 0][
        observation[0][0]
    ][observation[0][1]]
