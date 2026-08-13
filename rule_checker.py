import re
import ipaddress

class RuleChecker:
    def __init__(self):
        self.rules = [
            self.check_duplicate_ip,
            self.check_gateway_mismatch,
            self.check_interface_down,
            self.check_vlan_misconfig,
            self.check_missing_route,
            self.check_incorrect_subnet_mask
        ]

    def check_all(self, case):
        findings = []
        for rule in self.rules:
            result = rule(case)
            if result:
                findings.extend(result if isinstance(result, list) else [result])
        return findings

    def check_duplicate_ip(self, case):
        findings = []
        output = case.get('show_output', '')
        # Check for explicitly reported conflicts
        if 'IP address conflict' in output or 'dhcp conflict' in output.lower():
            findings.append({
                "rule_id": "DUPLICATE_IP",
                "severity": "Medium",
                "evidence_reference": "DHCP conflict detected in show output",
                "explanation": "An IP address conflict was detected on the network."
            })
        return findings

    def check_gateway_mismatch(self, case):
        findings = []
        output = case.get('show_output', '')
        # Basic heuristic parsing for ipconfig
        ip_match = re.search(r'IPv4 Address[ .]*: ([\d\.]+)', output)
        mask_match = re.search(r'Subnet Mask[ .]*: ([\d\.]+)', output)
        gw_match = re.search(r'Default Gateway[ .]*: ([\d\.]+)', output)
        
        if ip_match and mask_match and gw_match:
            try:
                ip = ip_match.group(1)
                mask = mask_match.group(1)
                gw = gw_match.group(1)
                
                # Exclude loopback/empty
                if gw and gw != '127.0.0.1' and gw != '0.0.0.0':
                    network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                    gateway_ip = ipaddress.IPv4Address(gw)
                    
                    if gateway_ip not in network:
                        findings.append({
                            "rule_id": "GATEWAY_MISMATCH",
                            "severity": "High",
                            "evidence_reference": f"IP {ip}, Mask {mask}, GW {gw}",
                            "explanation": f"The default gateway {gw} is not in the same subnet as the host IP {ip}/{mask}."
                        })
            except Exception:
                pass
        return findings

    def check_interface_down(self, case):
        findings = []
        output = case.get('show_output', '')
        
        if 'administratively down' in output:
            findings.append({
                "rule_id": "INTERFACE_DOWN",
                "severity": "High",
                "evidence_reference": "Interface administratively down",
                "explanation": "One or more interfaces are administratively down and need to be enabled with 'no shutdown'."
            })
        elif 'line protocol down' in output or 'line protocol is down' in output:
             findings.append({
                "rule_id": "INTERFACE_DOWN",
                "severity": "High",
                "evidence_reference": "Line protocol down",
                "explanation": "The line protocol is down on an interface, indicating a layer 1 or layer 2 issue."
            })
        return findings

    def check_vlan_misconfig(self, case):
        findings = []
        output = case.get('show_output', '')
        
        if 'Native vlan mismatch' in output or 'Native vlan' in output:
            # We would normally parse neighbor CDP or just flag if we see different native vlans
            # Let's do a simple check on multiple trunks output
            native_vlans = re.findall(r'trunking\s+(\d+)', output)
            if len(set(native_vlans)) > 1:
                findings.append({
                    "rule_id": "VLAN_MISCONFIG",
                    "severity": "High",
                    "evidence_reference": f"Native VLANs: {', '.join(native_vlans)}",
                    "explanation": "A native VLAN mismatch was detected across trunk links."
                })
        return findings

    def check_missing_route(self, case):
        findings = []
        output = case.get('show_output', '')
        
        if 'Gateway of last resort is not set' in output and '0.0.0.0/0' not in output:
            findings.append({
                "rule_id": "MISSING_ROUTE",
                "severity": "High",
                "evidence_reference": "Gateway of last resort is not set",
                "explanation": "The router does not have a default route configured."
            })
        return findings

    def check_incorrect_subnet_mask(self, case):
        # A full check requires knowing the intended subnet. 
        # This is a stub for potential future deterministic checks if intended mask is provided.
        findings = []
        return findings

if __name__ == '__main__':
    # Simple self-test
    checker = RuleChecker()
    test_case = {
        'show_output': 'IPv4 Address. . . . . . . . . . . : 192.168.1.50\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 192.168.2.1'
    }
    print(checker.check_all(test_case))
