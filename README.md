# Business Rule Engine
The hlpy business rule engine.

## Installation
```
pip install hlpy-business-rule-engine
```

## Usage
```python
from rule_engine import RuleEngine

engine = RuleEngine()
# To load a folder of .rules files use the method 'load_rules_from_folder'
engine.add_rules([
    {
        'name': "is_event_0",
        'conditions': ['field == "value"', 'event == "event_0"'],
        'actions': '''
                    print("is_auction")
                    set_variable("test", "value")''',
        'priority': 1000
    },
    {
        'name': "is_event_1",
        'conditions': ['field == "value"', 'event == "event_1"'],
        'actions': '''
                    print("Performing action...")
                    set_variable("var", "var_value")''',
        'priority': 1000
    },
    {
        'name': "is_event_1_2",
        'conditions': ['field == "value"', 'event == "event_1"'],
        'actions': '''
                    print("Performing actions for event 1")
                    set_variable("run", "result_run")''',
        'priority': 100
    },
])

response = engine.process({
    'field': 'value',
    'event': 'event_1',
})
assert response['run'] == 'result_run'
assert response['var'] == 'var_value'
```
