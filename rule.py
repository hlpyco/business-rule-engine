import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


class Rule:

    def __repr__(self) -> str:
        return f"rule_name: {self.rule_name}, priority: {self.priority}"

    DEFAULT_PRIORITY = 10000

    def __init__(self, rule_name: str, conditions=[], actions="", priority=DEFAULT_PRIORITY) -> None:
        self.rule_name: str = rule_name
        self.conditions: list[str] = conditions
        self.actions: str = actions
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
            line = line.strip()  # The split on rule name doesn't work for multi-line w/o
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
                    #TODO change this exception
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
                actions.append(line.strip())
        logging.debug(f"Adding rule [{rule_name}] with conditions [{conditions}],"
                      f" actions [{actions}], priority [{priority}]")

        return Rule(rule_name, conditions, "\n".join(actions), priority=priority)
