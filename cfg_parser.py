class CFG:
    def __init__(self, cfg_text):
        self.rules = parse_cfg(cfg_text)
        self.start_symbol = list(self.rules.keys())[0]

    def derive(self, target_string):
        accepted, steps = derive_string(self.rules, self.start_symbol, target_string)
        return {
            "accepted": accepted,
            "derivation": steps,
            "tree": steps
        }

def parse_cfg(cfg_text):
    rules = {}
    for line in cfg_text.strip().splitlines():
        if '->' in line:
            left, right = line.split('->')
            left = left.strip()
            productions = [prod.strip().split() if prod.strip() != 'ε' else [] for prod in right.strip().split('|')]
            if left not in rules:
                rules[left] = []
            rules[left].extend(productions)
    return rules


def derive_string(cfg, start_symbol, target_string):
    steps = []

    def expand(current, depth=0):
        steps.append(" ".join(current))

        current_str = ''.join(current)
        if current_str == target_string:
            return True

        if depth > 2 * len(target_string):
            steps.pop()
            return False

        for i, symbol in enumerate(current):
            if symbol in cfg:
                for production in cfg[symbol]:
                    new_string = current[:i] + production + current[i+1:]
                    if expand(new_string, depth + 1):
                        return True

        steps.pop()
        return False

    success = expand([start_symbol])
    return success, steps

