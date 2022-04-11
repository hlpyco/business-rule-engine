import unittest
from hlpy_business_rule_engine import RuleEngine


class TestBusinessRuleEngine(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.eng = RuleEngine()
        rules = [
            {
                'name': "is_auction",
                'conditions': ['person == "vip"', 'event == "is_auction"'],
                'actions': '''
                    print("call")
                    set_variable("test", "value")''',
                'priority': 1000
            },
            {
                'name': "send_sms_garanzia",
                'conditions': ['person == "vip"', 'event == "call_assistance"'],
                'actions': '''
                    print("Sending sms for for garanzie")
                    set_variable("var", "value")''',
                'priority': 1000
            },
            {
                'name': "send_sms_accident",
                'conditions': ['person == "vip"', 'event == "call_assistance"'],
                'actions': '''
                    print("Sending sms for for accident")
                    set_variable("run", "incident")''',
                'priority': 100
            },
        ]

        self.eng.add_rules(rules)

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
        self.assertEqual(response['test'], 'value')

    def testAddRule(self):
        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                print("Rule with priority")
                set_variable("new", "this")''',
            'priority': 1
        })
        response = self.eng.process({
            'person': 'vip',
            'event': 'call_assistance',
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
                        exclude_rule("send_sms_accident"),
                        set_variable("only", "this")''',
            'priority': 1
        })

        self.eng.remove_rule("send_sms_accident2")
        self.assertEqual(len(self.eng.ordered_rules), 3)

    def testExclusionByName(self):

        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "call_assistance"'],
            'actions': '''
                          print("Rule with priority")
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

    def testCustomFunction(self):

        self.eng.add_rule({
            'name': "send_sms_accident2",
            'conditions': ['person == "vip"', 'event == "is_auction"'],
            'actions': '''
                        print("Rule with priority")
                        exclude("event", "is_auction")
                        set_variable("custom_value", custom_f())''',
            'priority': 1
        })

        def custom_f():
            print("custom_f")
            return "custom_value"

        self.eng.register_function(custom_f)
        response = self.eng.process({
            'person': 'vip',
            'event': 'is_auction',
        })
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response['custom_value'], 'custom_value')
