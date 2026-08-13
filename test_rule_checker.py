import unittest
from rule_checker import RuleChecker

class TestRuleChecker(unittest.TestCase):
    def setUp(self):
        self.checker = RuleChecker()

    def test_duplicate_ip(self):
        case = {'show_output': 'Router# show ip dhcp conflict\nIP address conflict detected'}
        result = self.checker.check_duplicate_ip(case)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule_id'], 'DUPLICATE_IP')

    def test_gateway_mismatch(self):
        case = {'show_output': 'IPv4 Address. . . . . . . . . . . : 192.168.1.50\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 192.168.2.1'}
        result = self.checker.check_gateway_mismatch(case)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule_id'], 'GATEWAY_MISMATCH')

    def test_interface_down(self):
        case = {'show_output': 'GigabitEthernet0/0 is administratively down, line protocol is down'}
        result = self.checker.check_interface_down(case)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule_id'], 'INTERFACE_DOWN')

    def test_vlan_misconfig(self):
        case = {'show_output': 'Native vlan\nGi0/1       on           802.1q         trunking      99\nGi0/2       on           802.1q         trunking      1'}
        result = self.checker.check_vlan_misconfig(case)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule_id'], 'VLAN_MISCONFIG')

    def test_missing_route(self):
        case = {'show_output': 'Gateway of last resort is not set\n\n      10.0.0.0/8 is variably subnetted'}
        result = self.checker.check_missing_route(case)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule_id'], 'MISSING_ROUTE')

    def test_no_findings(self):
        case = {'show_output': 'All good here'}
        result = self.checker.check_all(case)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
