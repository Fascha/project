class Circles:

    def __init__(self, color, size=2):
        self.points = []
        self.color = color
        self.size = size
        self.selected = False

    def add_point(self, x, y):
        self.points.append((x, y))

    def move(self, vector):
        moved_points = []
        for point in self.points:
            moved_points.append((point[0] + vector[0], point[1] + vector[1]))
        self.points = moved_points


class Pixel:

    def __init__(self, x, y, color, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.selected = False


class Line:

    def __init__(self, color, size=5):
        self.points = []
        self.size = size
        self.color = color
        self.selected = False

    def add_point(self, x, y):
        self.points.append((x, y))

    def move(self, vector):
        moved_points = []
        for point in self.points:
            moved_points.append((point[0] + vector[0], point[1] + vector[1]))
        self.points = moved_points


class Path:

    def __init__(self, color, points=[], color_r=255, color_g=255, color_b=255, stroke_width=1, opacity=1):
        self.points = points
        self.stroke_width = stroke_width
        self.color = color
        self.color_r = color_r
        self.color_g = color_g
        self.color_b = color_b
        self.opacity = opacity
        self.css = None

    def add_point(self, x, y):
        self.points.append((x, y))

    def set_color(self, r, g, b):
        if r and g and b:
            pass
        else:
            raise ValueError()

    def update_css(self):
        self.css = """
            stroke-width: %d;
            fill-color: rgb(%d, %d, %d);
            stroke-opacity: %d;
        """ % (self.stroke_width, self.r, self.g, self.b, self.opacity)
