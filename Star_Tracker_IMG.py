import numpy as np
import matplotlib.pyplot as plt
from PyAstronomy import pyasl as asl

class Star_Tracker_IMG:

    CAMBRIDGE_LAT = 42.373615
    CAMBRIDGE_LONG = -71.109734

    def __init__(self, solved_file, jd) -> None:
        self.solved_file = solved_file
        self.julian_date = jd
        pass

    def get_hor_coords(self):
        RA, DEC = self.get_eq_coords()
        alt, az, ha = asl.eq2hor(self.julian_date,)
        return (alt, az)

    def get_eq_coords(self):
        file = open(self.solved_file)
        return (ra,dec)