import logging
import re
from typing import List

INDENTATION_PATTERN = re.compile(r"([\t ]+).+")


class Rule:

    def __repr__(self) -> str:
        return f"rule_name: {self.rule_name}, priority: {self.priority}"

    DEFAULT_PRIORITY = 10000

    def __init__(self, rule_name: str, conditions: List[str] = [], actions="", priority=DEFAULT_PRIORITY) -> None:
        self.rule_name: str = rule_name
        self.conditions: List[str] = conditions
        self.actions: str = RuleParser.normalize_indentation(actions)
        self.priority: int = priority

    def check_conditions(self, params: dict, custom_functions={}) -> bool:
        result = True
        for condition in self.conditions:
            r = eval(condition, {}, {**params, **custom_functions})
            if not isinstance(r, bool):
                logging.error(f"Condition {condition} is not boolean")
                raise Exception(f"Condition {condition} is not boolean")
            result = result and r
        return result

    def run_actions(self, params, custom_functions={}):
        code = compile(self.actions, '<string>', 'exec')
        eval(code, {}, {**params, **custom_functions})

    def execute(self, params: dict, custom_functions={}):
        rvalue = self.check_conditions(params, custom_functions=custom_functions)
        if rvalue:
            self.run_actions(params, custom_functions=custom_functions)


class RuleParser:

    def parsestr(self, text: str) -> Rule:
        is_condition: bool = False
        is_action: bool = False
        is_then: bool = False
        ignore_line: bool = False
        conditions = []
        actions = []
        rule_name = ""
        priority = Rule.DEFAULT_PRIORITY

        for line in text.split('\n'):
            ignore_line = False
            if line.lower().startswith('rule'):
                is_condition = False
                is_action = False
                rule_name = line.split(' ', 1)[1].strip("\"")
            if line.lower().startswith('priority'):
                is_condition = False
                is_action = False
                priority = int(line.split(' ', 1)[1].strip("\""))
            if line.lower().strip().startswith('when'):
                ignore_line = True
                is_condition = True
                is_action = False
            if line.lower().strip().startswith('then'):
                if is_then:
                    # TODO change this exception
                    raise Exception('using multiple "then" in one rule is not allowed')
                is_then = True
                ignore_line = True
                is_condition = False
                is_action = True
            if line.lower().strip().startswith('end'):
                ignore_line = True
                is_condition = False
                is_action = False
                is_then = False
            if rule_name and is_condition and not ignore_line:
                conditions.append(line.strip())
            if rule_name and is_action and not ignore_line:
                actions.append(line)
        string_actions = RuleParser.normalize_indentation("\n".join(actions))
        logging.debug(f"Adding rule [{rule_name}] with conditions [{conditions}],"
                      f" actions [\n{string_actions}], priority [{priority}]")
        return Rule(rule_name, conditions, string_actions, priority=priority)

    @staticmethod
    def normalize_indentation(instructions: str):
        lines = instructions.split("\n")
        dedented = []
        first = True
        for line in lines:
            if first:
                if len(line.strip()) == 0:
                    continue
                m = INDENTATION_PATTERN.findall(line)
                first = False
                if re.match("[A-Za-z]", line[0]):
                    return instructions
            dedented.append(line.replace(m[0], "", 1))
        return "\n".join(dedented)
