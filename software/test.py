from cfg_parser import parse_cfg, derive_string
from pda_simulator import parse_pda
from visualizer import draw_cfg_tree, draw_pda_states

cfg_text = """
S -> a S b | ε
"""
cfg = parse_cfg(cfg_text)
accepted, steps = derive_string(cfg, 'S', 'aaabbb')

print("ACCEPTED:", accepted)
print("STEPS:", steps)

if accepted:
    draw_cfg_tree(steps)
else:
    print("CFG did not accept the string.")

