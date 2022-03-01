from business_rule_engine import RuleParser
import os
import logging
import traceback
from collections import OrderedDict
from rule import Rule
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


class RuleEngine:

    CUSTOM_FUNCTIONS = {}

    def __init__(self):
        self.parser = RuleParser()
        self.register_function(print)
        self.ordered_rules = []

    @staticmethod
    def __read_text_file__(file_path):
        with open(file_path, 'r') as f:
            return f.read()

    @staticmethod
    def is_excluded(rule, exclusions):
        for exclusion in exclusions:
            conds = ";".join(rule.conditions)
            result = re.search(f'event\s*==\s*["|\']{exclusion}["|\']', conds)
            logging.debug(f'checking [{conds}] wrt [{f"event=={exclusion}"}]. Result [{result}]')
            if result:
                return True
        return False

    @staticmethod
    def get_priority(ordered_rules):
        return ordered_rules.priority

    def load_rules_from_folder(self, rule_folder):
        for file in os.listdir(path=rule_folder):
            if os.path.isdir(f"{rule_folder}/{file}"):
                self.load_rules_from_folder(f"{rule_folder}/{file}")
            else:
                rule = self.__read_text_file__(f"{rule_folder}/{file}")
                self.add_rule_from_string(rule)

    def process(self, params):
        variables = {}
        exclusions = []

        def set_variable(key, value):
            variables[key] = value
            return variables

        def get_variable(key):
            return variables[key] if key in variables.keys() else None

        def get_context():
            return variables

        def exclude(event):
            exclusions.append(event)

        builtin_functions = {
            'set_variable': set_variable,
            'get_variable': get_variable,
            'get_context': get_context,
            'exclude': exclude,

        }

        for rule in self.ordered_rules:
            try:
                logging.debug(f"exclusions: [{exclusions}]")
                if not self.is_excluded(rule, exclusions) and rule.rule_name not in exclusions:
                    result = rule.execute(params, custom_functions={**self.CUSTOM_FUNCTIONS, **builtin_functions})
                    logging.debug(f"result {result}")
                else:
                    logging.info(f"rule [{rule.rule_name}] is excluded")
            except Exception as e:
                traceback.print_exc()
                logging.error(e)

        return variables

    def add_rules(self, rules):
        for r in rules:
            self.add_rule(r)

    def add_rule(self, rule):
        r = Rule(rule['name'], conditions=rule['conditions'], actions=rule['actions'], priority=rule['priority'])
        self.add_rule_to_knowledge(r)

    def remove_rule(self, rule_name):
        for r in self.ordered_rules:
            if r.rule_name == rule_name:
                self.ordered_rules.remove(r)
                break

    def get_rule(self, rule):
        for r in self.ordered_rules:
            if r.rule_name == rule.rule_name:
                return r
        return None

    def add_rule_to_knowledge(self, rule: Rule):
        old_rule = self.get_rule(rule)
        if old_rule:
            self.ordered_rules.remove(old_rule)
        self.ordered_rules.append(rule)
        self.ordered_rules.sort(key=self.get_priority)
        return True

    def add_rule_from_string(self, rule):
        self.parser.parsestr(rule)
        for key in self.parser.rules:
            value = self.parser.rules[key]
            self.add_rule_to_knowledge(value)
        self.parser.rules = OrderedDict()

    @classmethod
    def register_function(cls, function, function_name: str = None) -> None:
        custom_function_name = function_name or function.__name__
        cls.CUSTOM_FUNCTIONS[custom_function_name] = function

    @classmethod
    def unregister_function(cls, function, function_name: str = None) -> None:
        custom_function_name = function_name or function.__name__
        del(cls.CUSTOM_FUNCTIONS[custom_function_name])