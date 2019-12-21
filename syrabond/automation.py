import time
import syrabond.facility
from syrabond.common import log


class StateEngine:
    def __init__(self):
        self.resources = {}


class TimeEngine:
    def __init__(self, facility, orm):
        self.scenarios = []
        scens = orm.load_scenarios('time')
        for scen in scens:
            effect = []
            sch = self.Schedule(scen['schedule'])
            for effect_conf in scen['effect']:
                res = effect_conf.resource
                eff = Map(facility.resources[res], effect_conf.state)
                effect.append(eff)
            self.scenarios.append(self.Scenario(scen['hrn'], sch, effect))
        log('TimeEngine started.')

    def add_scen(self):
        pass

    def check_shedule(self):
        result = []
        now = {'weekday': time.localtime(time.time()).tm_wday,
               'time': [time.localtime(time.time()).tm_hour, time.localtime(time.time()).tm_min]}
        for scen in self.scenarios:
            if now['weekday'] in scen.schedule.days:
                if now['time'] == scen.schedule.start_time:
                    result.append(scen)
        if result:
            log(f"TimeEngine: It's time for scenarios: {[x.hrn for x in result]}")
        return result

    class Schedule:
        def __init__(self, schedule):
            self.days = [int(x) for x in schedule[0].weekdays.split(',')]
            self.start_time = [int(x) for x in schedule[0].start.split(',')]

    class Scenario:
        def __init__(self, hrn, schedule, effect):
            self.hrn = hrn
            self.schedule = schedule
            self.effect = effect
            self.ran = None

        def workout(self):
            now = (time.localtime(time.time()).tm_hour, time.localtime(time.time()).tm_min)
            if not self.ran == now:
                self.ran = now
                for mapper in self.effect:
                    mapper.activate()

class Scenario:  # TODO Add comparison rules for conditions (and | or)

    def __init__(self, hrn: str, conditions, effect):
        self.hrn = hrn
        self.conditions = conditions
        self.effect = effect

    def check_conditions(self, resource):
        result = set()
        if self.conditions[resource.uid].check():
            for cond in self.conditions:
                result.add(self.conditions[cond].check())
            if result == {True}:
                return True
            else:
                return False
        else:
            return False

    def workout(self):
        for mapper in self.effect:
            mapper.activate()


class Map:

    def __init__(self, resource, state):
        self.resource = resource
        self.state = state

    def activate(self):
        if isinstance(self.resource, syrabond.facility.Switch):
            self.resource.turn(self.state)
        elif isinstance(self.resource, syrabond.facility.VirtualAppliance):
            self.resource.set_state(self.state)


class Conditions:

    def __init__(self, resource, positive, compare, state):
        self.resource = resource
        self.positive = positive
        self.compare = compare
        self.state = state

    def check(self):  # TODO Divide for types of resources, make <> work
        if self.compare == '=':
            if self.resource.state == self.state:
                if self.positive:
                    return True
                else:
                    return False
            else:
                if self.positive:
                    return False
                else:
                    return True
        elif self.compare == '>':
            if self.resource.state > self.state:
                if self.positive:
                    return True
                else:
                    return False
        elif self.compare == '<':
            if self.resource.state > self.state:
                if self.positive:
                    return True
                else:
                    return False