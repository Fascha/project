import numpy as np


class Mapping:

    def __init__(self, dest_w, dest_h):
        self.SRC_W = 1024
        self.SRC_H = 768
        self.DEST_W = dest_w
        self.DEST_H = dest_h

        self.source_to_dest = None
        self.dx1, self.dy1 = 0, 0
        self.dx2, self.dy2 = self.DEST_W, 0
        self.dx3, self.dy3 = self.DEST_W, self.DEST_H
        self.dx4, self.dy4 = 0, self.DEST_H

    def calculate_source_to_dest(self, ir_markers):
        if len(ir_markers) == 4:
            # links oben in ir cam: x=0 y=786
            # rechts oben in ir cam: x=1023 y=786
            # links unten in ir cam: x=0 y=0
            # rechts unten in ir cam: x=1023 y=0

            ir_markers_sorted = sorted(ir_markers)

            if ir_markers_sorted[0][1] < ir_markers_sorted[1][1]:
                x1, y1 = ir_markers_sorted[1]
                x4, y4 = ir_markers_sorted[0]
            else:
                x1, y1 = ir_markers_sorted[0]
                x4, y4 = ir_markers_sorted[1]

            if ir_markers_sorted[2][1] < ir_markers_sorted[3][1]:
                x2, y2 = ir_markers_sorted[3]
                x3, y3 = ir_markers_sorted[2]
            else:
                x2, y2 = ir_markers_sorted[2]
                x3, y3 = ir_markers_sorted[3]

            # Step 1
            source_points_123 = np.matrix([[x1, x2, x3],
                                           [y1, y2, y3],
                                           [1, 1, 1]])

            source_point_4 = [[x4],
                              [y4],
                              [1]]

            scale_to_source = np.linalg.solve(source_points_123, source_point_4)

            ls, ms, ts = [float(x) for x in scale_to_source]

            # Step 2
            unit_to_source = np.matrix([[ls*x1, ms*x2, ts*x3],
                                        [ls*y1, ms*y2, ts*y3],
                                        [ls*1, ms*1, ts*1]])

            # Step 3
            dest_points_123 = np.matrix([[self.dx1, self.dx2, self.dx3],
                                         [self.dy1, self.dy2, self.dy3],
                                         [1, 1, 1]])

            dest_point_4 = np.matrix([[self.dx4],
                                      [self.dy4],
                                      [1]])

            scale_to_dest = np.linalg.solve(dest_points_123, dest_point_4)

            ld, md, td = [float(x) for x in scale_to_dest]

            unit_to_dest = np.matrix([[ld*self.dx1, md*self.dx2, td*self.dx3],
                                      [ld*self.dy1, md*self.dy2, td*self.dy3],
                                      [ld*1, md*1, td*1]])

            # Step 4
            source_to_unit = np.linalg.inv(unit_to_source)

            # Step 5
            self.source_to_dest = unit_to_dest @ source_to_unit
        else:
            print("NOT EXACTLY 4 IR MARKER COORDINATES GIVEN")
            return

    def get_pointing_point(self):
        # Mapping of center
        x, y, z = [float(w) for w in self.source_to_dest @ np.matrix([[self.SRC_W/2],
                                                                      [self.SRC_H/2],
                                                                      [1]])]

        # step 7: dehomogenization
        x = x/z
        y = y/z

        return x, y
