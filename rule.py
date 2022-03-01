import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


class Rule:

    def __init__(self, rule_name: str, conditions=[], actions="", priority=10000) -> None:
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

