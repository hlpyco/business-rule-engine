import unittest
from rule_engine import RuleEngine


class TestBusinessRuleEngineFromFolder(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.eng = RuleEngine()
        self.eng.load_rules_from_folder("rule_set")

    def testMultiExecRules(self):
        response = self.eng.process({
            'business_partner': 'arval',
            'event': 'call_assistance',
            'car_issue': 'INCIDENTE'
        })

        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(response['run'], 'incident')
        self.assertEqual(response['var'], 'value')

    def testRule(self):

        print(self.eng.ordered_rules)
        response = self.eng.process({
            'business_partner': 'arval',
            'event': 'is_auction',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['test'], 'value')

    def testAddRule(self):
        self.eng.add_rule({
            'name': "send_sms_arval_accident2",
            'conditions': ['business_partner = "arval"', 'event = "call_assistance"'],
            'actions': [
                'print("Rule with priority")',
                'set_variable("new", "this")'
            ],
            'priority': 1
        })

        for r in self.eng.ordered_rules:
            print(f"{r['rule'].rulename}")

        response = self.eng.process({
            'business_partner': 'arval',
            'event': 'call_assistance',
            'car_issue': 'INCIDENTE'
        })
        self.assertEqual(len(response.keys()), 3)
        self.assertEqual(response['new'], 'this')
        self.assertEqual(response['run'], 'incident')
        self.assertEqual(response['var'], 'value')
        self.eng.remove_rule("send_sms_arval_accident2")

    def testExclusion(self):
        self.eng.add_rule({
            'name': "send_sms_arval_accident2",
            'conditions': ['business_partner = "arval"', 'event = "call_assistance"'],
            'actions': [
                'print("Rule with priority")',
                'exclude("call_assistance")',
                'set_variable("only", "this")'
            ],
            'priority': 1
        })
        response = self.eng.process({
            'business_partner': 'arval',
            'event': 'call_assistance',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['only'], 'this')
        self.eng.remove_rule("send_sms_arval_accident2")

    def testRemoveRule(self):
        self.eng.add_rule({
            'name': "send_sms_arval_accident2",
            'conditions': ['business_partner = "arval"', 'event = "call_assistance"'],
            'actions': [
                'print("Rule with priority")',
                'exclude("send_sms_arval_accident")',
                'set_variable("only", "this")'
            ],
            'priority': 1
        })

        self.eng.remove_rule("send_sms_arval_accident2")
        self.assertEqual(len(self.eng.ordered_rules), 3)

    def testExclusionByName(self):
        for r in self.eng.ordered_rules:
            print(r['rule'].rulename)

        self.eng.add_rule({
            'name': "send_sms_arval_accident2",
            'conditions': ['business_partner = "arval"', 'event = "call_assistance"'],
            'actions': [
                'print("Rule with priority")',
                'exclude("send_sms_arval_accident")',
                'set_variable("only", "this")'
            ],
            'priority': 1
        })
        response = self.eng.process({
            'business_partner': 'arval',
            'event': 'call_assistance',
        })
        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(response['only'], 'this')
        self.assertEqual(response['var'], 'value')
        self.assertTrue('run' not in response.keys())
        self.eng.remove_rule("send_sms_arval_accident2")
