""" Compute COP as a function of outdoor temperatures from
    various cases in the literature
"""
import numpy as np

class COP:

    def __init__(self, set_point=296.15, unit='K'):

        # Set point temperature is 74 degF as default.
        # May be changed 
        self.set_point = set_point
        self.unit = 'K'
        
        print('Set point temperature is: ' + str(self.set_point) + self.unit)
        
        return None


    def carnot(self, outdoor_temp):
        return self.set_point/(outdoor_temp - self.set_point)


    def chow_2000(self, outdoor_temp):
        print(self.set_point - 273.15) 
        if self.set_point - 273.15 == 23:
            a = 4.825
            b = .0687
        elif self.set_point - 273.15 == 25:
            a = 5.153
            b = .0738
        elif self.set_point - 273.15 == 27:
            a = 5.241
            b = .0742
        else:
            print('Invalid setpoint for Chow et al (2000)')

            a = np.nan
            b = np.nan

        return a + b*outdoor_temp

    
    def choi(self, outdoor_temp):
        coeff = (638.95 - 4.238*outdoor_temp)/(100 + 3.534*outdoor_temp)

        return coeff

    def ryu(self, outdoor_temp):
        setpoint_c = self.set_point - 273.15

        return 12 - 0.35*outdoor_temp + .0034*outdoor_temp**2
