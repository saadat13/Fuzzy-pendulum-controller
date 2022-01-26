from __future__ import division
# -*- coding: utf-8 -*-

# python imports
import math
from math import degrees
# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
import re
from collections import defaultdict


class Param:
    sets = []

    def fuzzify_for(self, x):
        mem = {}
        for s in self.sets:
            mem[s] = self.get_membership(s, x)
        return mem

    def get_membership(self, set_name, x):
        try:
            return getattr(self, set_name)(x)
        except AttributeError:
            raise Exception('no set found with this name')


class PV(Param):
    sets = ['cw_fast', 'cw_slow', 'stop', 'ccw_slow', 'ccw_fast']

    def cw_fast(self, x):
        if x == -200:
            return 1
        elif -200 < x <= -100:
            return -0.01*x - 1
        return 0

    def cw_slow(self, x):
        if -200 <= x <= -100:
            return 0.01*x + 2
        elif -100 < x <= 0:
            return -0.01*x
        return 0

    def stop(self, x):
        if -100 <= x <= 0:
            return 0.01*x + 1
        elif 0 < x <= 100:
            return -0.01*x + 1
        return 0

    def ccw_slow(self, x):
        if 0 <= x <= 100:
            return 0.01*x
        elif 100 < x <= 200:
            return -0.01*x + 2
        return 0

    def ccw_fast(self, x):
        if 100 <= x < 200:
            return 0.01*x - 1
        elif x == 200:
            return 1
        return 0


class PA(Param):
    sets = ['up_more_right', 'up_right', 'up', 'up_left', 'up_more_left', 'down_more_left', 'down_left', 'down', 'down_right', 'down_more_right']

    def up_more_right(self, x):
        if 0 <= x <= 30:
            return x/30
        elif 30 < x <= 60:
            return (-x/30) + 2
        return 0

    def up_right(self, x):
        if 30 <= x <= 60:
            return (x/30) - 1
        elif 60 < x <= 90:
            return -(x/30) + 3
        return 0

    def up(self, x):
        if 60 <= x <= 90:
            return (x / 30) - 2
        elif 90 < x <= 120:
            return -(x / 30) + 4
        return 0

    def up_left(self, x):
        if 90 <= x <= 120:
            return (x / 30) - 3
        elif 120 < x <= 150:
            return -(x / 30) + 5
        return 0

    def up_more_left(self, x):
        if 120 <= x <= 150:
            return (x / 30) - 4
        elif 150 < x <= 180:
            return -(x / 30) + 6
        return 0

    def down_more_left(self, x):
        if 180 <= x <= 210:
            return (x / 30) - 6
        elif 210 < x <= 240:
            return -(x / 30) + 8
        return 0

    def down_left(self, x):
        if 210 <= x <= 240:
            return (x / 30) - 7
        elif 240 < x <= 270:
            return -(x / 30) + 9
        return 0

    def down(self, x):
        if 240 <= x <= 270:
            return (x / 30) - 8
        elif 270 < x <= 300:
            return -(x / 30) + 10
        return 0

    def down_right(self, x):
        if 270 <= x <= 300:
            return (x / 30) - 9
        elif 300 < x <= 330:
            return -(x / 30) + 11
        return 0

    def down_more_right(self, x):
        if 300 <= x <= 330:
            return (x / 30) - 10
        elif 330 < x <= 360:
            return -(x / 30) + 12
        return 0


class CP(Param):
    sets = ['left_far', 'left_near', 'stop', 'right_near', 'right_far']

    def left_far(self, x):
        if x == -10:
            return 1
        elif -10 < x <= -5:
            return -0.2*x - 1
        return 0

    def left_near(self, x):
        if -10 <= x <= -2.5:
            return (2/15)*x + 4/3
        elif -2.5 < x <= 0:
            return -(2/5)*x
        return 0

    def stop(self, x):
        if -2.5 <= x <= 0:
            return 0.4*x + 1
        elif 0 < x <= 2.5:
            return -0.4*x + 1
        return 0

    def right_near(self, x):
        if 0 <= x <= 2.5:
            return 0.4*x
        elif 2.5 < x <= 10:
            return -(2/15)*x + 4/3
        return 0

    def right_far(self, x):
        if 5 <= x < 10:
            return 0.2*x - 1
        elif x == 10:
            return 1
        return 0


class CV(Param):
    sets = ['left_fast', 'left_slow', 'stop', 'right_slow', 'right_fast']

    def left_fast(self, x):
        if x == -5:
            return 1
        elif -5 <= x <= 1:
            return -0.4*x - 1
        return 0

    def left_slow(self, x):
        if -5 <= x <= -1:
            return (1/4)*x + (5/4)
        elif -1 < x <= 0:
            return -x
        return 0

    def stop(self, x):
        if -1 <= x <= 0:
            return x + 1
        elif 0 < x <= 1:
            return -x + 1
        return 0

    def right_slow(self, x):
        if 0 <= x <= 1:
            return x
        elif 1 <= x <= 5:
            return -(1/4)*x + (5/4)
        return 0

    def right_fast(self, x):
        if 2.5 <= x < 5:
            return 0.4*x - 1
        elif x == 5:
            return 1
        return 0


force_ranges = {
    'left_fast': (-100, -60),
    'left_slow': (-80, 0),
    'stop': (-60, 60),
    'right_slow': (0, 80),
    'right_fast': (60, 100)
}


class ForceInverse:

    def __init__(self):
        pass

    def left_fast(self, y):
        # y1 = 0.05x + 5 -> x = (y1 - 5) / 0.05
        # y2 = -0.05x - 3 -> x = (y2 + 3) / (-0.05)
        return (y-5)*20, (y+3)*(-20)

    def left_slow(self, y):
        # y1 = 0.05x + 4 -> x = (y1 - 4) / 0.05
        # y2 = -(1/60)x -> x = -60y
        return (y-4)*20, -60*y

    def stop(self, y):
        # y1 = (1/60)x + 1 -> x = (y1 - 1) * 60
        # y2 = -(1/60)x + 1 -> x = (y2 - 1) * (-60)
        return (y-1) * 60, (y - 1) * (-60)

    def right_slow(self, y):
        # y1 = (1/60)x -> x = y * 60
        # y2 = -(0.05)x + 4 -> x = (y2 - 4) / (- 0.05)
        return y * 60, (y - 4) * (-20)

    def right_fast(self, y):
        # y1 = 0.05x - 3 -> x = (y1 + 3) / 0.05
        # y2 = -(0.05)x + 5 -> x = (y2 - 5) / (-0.05)
        return (y + 3) * 20, (y - 5) * (-20)


class System:
    def __init__(self):
        self.rules = self.load_rules()
        self.force_inverter = ForceInverse()

    def inference(self, sets_dict):
        force_set = defaultdict(float)
        for rule in self.rules:
            set_name, value = self.single_rule_inference(rule, sets_dict)
            force_set[set_name] = max(force_set[set_name], value)
            assert 0 <= force_set[set_name] <= 1
        return force_set

    def load_rules(self):
        rules = []
        with open('controllers/complex.fcl', 'r') as f:
            lines = filter(lambda x: len(x) > 0, map(str.strip, f.readlines()))
            rule_lines = filter(lambda x: x.startswith(r'RULE '), lines)
            rules = map(lambda x: x.split(':')[1].strip(), rule_lines)
        return rules

    def single_rule_inference(self, rule, sets_dict):
        rule = rule.replace('IF', '').replace(';', '').strip()
        cond, then = rule.split('THEN')
        for item in sorted(re.findall(r'([a-z_]+ IS [a-z_]+)', cond), key=len, reverse=True):
            parameter, set_ = map(str.strip, item.split('IS'))
            cond = cond.replace(item, str(sets_dict[parameter][set_]))
        # print(cond)
        a_force_set_name = then.split('IS')[1].strip()
        res = eval(cond.lower())
        # print res if res > 0 else ''
        return a_force_set_name, res

    def defuzzify(self, force_sets):
        active_sets = {k: v for k, v in force_sets.items() if v > 0}
        sigma_area = 0
        sigma_area_cross_x_bar = 0  # area*x_bar
        for set_name, memship_value in active_sets.items():
            x1, x2 = getattr(self.force_inverter, set_name)(memship_value)
            # print x1, x2
            x3, x4 = force_ranges[set_name]
            area = (1/2) * (math.fabs(x2-x1) + math.fabs(x4-x3)) * memship_value
            x_bar = (x2 + x1) / 2
            sigma_area_cross_x_bar += area * x_bar
            sigma_area += area
        force_value = sigma_area_cross_x_bar / sigma_area if sigma_area > 0 else 0
        return force_value


class FuzzyController:

    def __init__(self, fcl_path):
        # self.system = Reader().load_from_file(fcl_path)
        self.system = System()

    def _make_input(self, world):
        return dict(
            cp = world.x,
            cv = world.v,
            pa = degrees(world.theta),
            pv = degrees(world.omega)
        )


    def _make_output(self):
        return dict(
            force = 0.
        )

    def decide(self, world):
        output = self._make_output()
        input_ = self._make_input(world)
        # print input_['pa']
        pa, pv, cp, cv = input_['pa'], input_['pv'], input_['cp'], input_['cv']
        pa = pa % 180
        # fuzzify
        fuzzified_input = {'pv': PV().fuzzify_for(pv), 'pa': PA().fuzzify_for(pa),
                           'cp': CP().fuzzify_for(cp), 'cv': CV().fuzzify_for(cv)
                           }
        # inference
        force_sets = self.system.inference(fuzzified_input)
        # defuzzify
        output['force'] = self.system.defuzzify(force_sets)
        # self.system.calculate(self._make_input(world), output)
        force = self.system.defuzzify(force_sets)
        return force
