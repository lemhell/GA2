import json
import tkinter as tk

from models.entities import Field

input_data_file = "input/entities.json"

if __name__ == '__main__':

    data = json.load(open(input_data_file, 'r'))
    field = Field(500, 500, data)

    achievable_enemies = field.solve(accuracy=1)
    for turret_number, goals_list in achievable_enemies.items():
        print("%s: %s" % (str(turret_number), str([str(g) for g in goals_list])))

    window = tk.Tk()
    canvas = tk.Canvas(window, bg="white", height=500, width=500)

    field.draw(canvas)

    canvas.pack()
    window.mainloop()

