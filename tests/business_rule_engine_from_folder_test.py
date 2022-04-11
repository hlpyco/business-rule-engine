import unittest
from hlpy_business_rule_engine import RuleEngine


class TestBusinessRuleEngineFromFolder(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.eng = RuleEngine()
        self.eng.load_rules_from_folder("tests/rule_set")

    def testMultiExecRules(self):
        response = self.eng.process({
            'person': 'vip',
            'event': 'call_assistance',
            'car_issue': 'INCIDENT'
        })

        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(response['run'], 'incident')
        self.assertEqual(response['var'], 'value')

    def testRule(self):
        response = self.eng.process({
            'person': 'vip',
            'event': 'is_auction',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['priority'], 'True')

    def testAddRule(self):
        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                print("Rule with priority"),
                set_variable("new", "this")''',
            'priority': 1
        })

        response = self.eng.process({
            'person': 'vip',
            'event': 'call_assistance',
            'car_issue': 'INCIDENT'
        })
        self.assertEqual(len(response.keys()), 3)
        self.assertEqual(response['new'], 'this')
        self.assertEqual(response['run'], 'incident')
        self.assertEqual(response['var'], 'value')
        self.eng.remove_rule("send_sms_accident2")

    def testExclusion(self):
        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                print("Rule with priority"),
                exclude("event", "call_assistance")
                set_variable("only", "this")''',
            'priority': 1
        })
        response = self.eng.process({
            'person': 'vip',
            'event': 'call_assistance',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['only'], 'this')
        self.eng.remove_rule("send_sms_accident2")

    def testRemoveRule(self):
        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                print("Rule with priority"),
                exclude_rule("send_sms_accident")
                set_variable("only", "this")''',
            'priority': 1
        })

        self.eng.remove_rule("send_sms_accident2")
        self.assertEqual(len(self.eng.ordered_rules), 4)

    def testExclusionByName(self):

        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                print("Rule with priority"),
                exclude_rule("send_sms_accident")
                set_variable("only", "this")''',
            'priority': 1
        })
        response = self.eng.process({
            'person': 'vip',
            'event': 'call_assistance',
        })
        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(response['only'], 'this')
        self.assertEqual(response['var'], 'value')
        self.assertTrue('run' not in response.keys())
        self.eng.remove_rule("send_sms_accident2")

    def testRuleWithPriority(self):
        response = self.eng.process({
            'person': 'vip',
            'event': 'is_auction',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['priority'], 'True')
