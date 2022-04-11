import logging
import os
import re

from .rule import Rule, RuleParser


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
        for key, exclusion in exclusions:
            conds = ";".join(rule.conditions)
            result = re.search(f'{key}\s*==\s*["|\']{exclusion}["|\']', conds)
            logging.debug(f'checking [{conds}] wrt [{f"{key}=={exclusion}"}]. Result [{result}]')
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

        builtin_names = self.builtins()
        exclusions = builtin_names['exclusions']
        excluded_rules = builtin_names['excluded_rules']

        for rule in self.ordered_rules:
            try:
                logging.debug(f"exclusions: [{exclusions}]")
                if not self.is_excluded(rule, exclusions) and rule.rule_name not in excluded_rules:
                    result = rule.execute(params, custom_functions={**self.CUSTOM_FUNCTIONS, **builtin_names})
                    logging.debug(f"result {result}")
                else:
                    logging.info(f"rule [{rule.rule_name}] is excluded")
            except Exception as e:
                logging.error(e)

        return builtin_names['variables']

    @staticmethod
    def builtins():
        variables = {}
        exclusions = {}
        excluded_rules = []

        def set_variable(key, value):
            variables[key] = value
            return variables

        def get_variable(key):
            return variables[key] if key in variables.keys() else None

        def get_context():
            return variables

        def exclude(key, value):
            exclusions.update({key: value})

        def exclude_rule(rule_name):
            excluded_rules.append(rule_name)

        return {
            'set_variable': set_variable,
            'get_variable': get_variable,
            'get_context': get_context,
            'exclude': exclude,
            'exclude_rule': exclude_rule,
            'variables': variables,
            'exclusions': exclusions,
            'excluded_rules': excluded_rules
        }

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
        r = self.parser.parsestr(rule)
        self.add_rule_to_knowledge(r)

    @classmethod
    def register_function(cls, function, function_name: str = None) -> None:
        custom_function_name = function_name or function.__name__
        cls.CUSTOM_FUNCTIONS[custom_function_name] = function

    @classmethod
    def unregister_function(cls, function, function_name: str = None) -> None:
        custom_function_name = function_name or function.__name__
        del (cls.CUSTOM_FUNCTIONS[custom_function_name])
