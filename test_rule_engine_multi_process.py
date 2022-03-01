import multiprocessing
from multiprocessing import Manager
import time
from rule_engine import RuleEngine
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
engine = RuleEngine()
engine.load_rules_from_folder("rule_set")

def useless_function(params, result:dict, sec=1):
    time.sleep(sec)
    result.update(engine.process(params))


if __name__ == '__main__':
    start = time.perf_counter()
    manager = Manager()

    res1 = manager.dict()
    res2 = manager.dict()
    process1 = multiprocessing.Process(target=useless_function, args=[{
        'business_partner': 'arval',
        'event': 'is_auction',
    }, res1, 1])
    process2 = multiprocessing.Process(target=useless_function, args=[{
        'business_partner': 'arval',
        'event': 'call_assistance',
        'car_issue': "INCIDENTE"
    }, res2])
    process1.start()
    process2.start()
    end = time.perf_counter()
    process1.join()
    process2.join()
    print(res1)
    print(res2)
    print(f'Finished in {round(end-start, 2)} second(s)')
