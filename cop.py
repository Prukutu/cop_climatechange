""" Compute COP as a function of outdoor temperatures from
    various cases in the literature
"""
import numpy as np

class COP:

    def __init__(self, set_point=296.15, unit='K', g=0.321):
        """ Initialize the COP object with the set point temperature
            and the unit of temperature.
        """

        # Set point temperature is 23 degC as default.
        # May be changed 
        self.set_point = set_point
        self.unit = 'K'
        self.g = g
        
        print('Set point temperature is: ' + str(self.set_point) + self.unit)
        
        return None
    
    def getCOP(self, outdoor_temp, method='carnot'):
        """ Compute the Coefficient of Performance for real systems 
            using a range of methods.
        """

        if method == 'carnot':
            return 0.321*self.set_point/(outdoor_temp - self.set_point)
        
        elif method == 'chow': 
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

            return a - b*(outdoor_temp-273.15)
        
        elif method == 'choi':
            outdoor_temp = outdoor_temp-273.15
            coeff = (638.95 - 4.238*outdoor_temp)/(100 + 3.534*outdoor_temp)

            return coeff
        
        elif method == 'ryu':
            setpoint_c = self.set_point - 273.15
            outdoor_temp = outdoor_temp - 273.15

            return 12 - 0.35*outdoor_temp + .0034*outdoor_temp**2
        
        elif method == 'exergetic':
            coeff = self.g*self.set_point/(outdoor_temp - self.set_point)
            return coeff
        
        else:
            raise Exception(f'Defined method {method} was not found!')

