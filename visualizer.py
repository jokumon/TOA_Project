from graphviz import Digraph
import uuid


# ---------------- CFG Derivation Tree ----------------

def draw_cfg_tree(steps, output_file='cfg_tree'):
    """
    Draws a derivation tree from leftmost derivation steps.
    Each step is a full sentential form (like ["S", "A B", "a B", "a b"])
    """
    dot = Digraph(format='png')
    dot.attr('node', shape='circle')

    # Recursive function to build tree
    def build_tree(parent_id, sentential_form, depth):
        if depth >= len(steps):
            return

        current_symbols = steps[depth].split()

        for i, symbol in enumerate(current_symbols):
            node_id = str(uuid.uuid4())
            dot.node(node_id, symbol)
            dot.edge(parent_id, node_id)

            if depth + 1 < len(steps):
                next_symbols = steps[depth + 1].split()

                # Check if expansion occurred here
                if len(next_symbols) > len(current_symbols):
                    # We assume only the first non-terminal expands (leftmost derivation)
                    if symbol != next_symbols[i]:  # crude but works
                        build_tree(node_id, steps[depth + 1], depth + 1)
                        break  # only one expansion per step

    # Begin tree
    root_symbol = steps[0].split()[0]  # start symbol
    root_id = str(uuid.uuid4())
    dot.node(root_id, root_symbol)
    build_tree(root_id, steps[0], 0)

    if output_file.endswith('.png'):
        output_file = output_file[:-4]
        
    dot.render(filename=output_file, format='png', cleanup=True)
    return output_file + ".png"


# ---------------- PDA State Diagram ----------------

def draw_pda_states(pda, output_file='pda_diagram'):
    """
    Draws PDA state transitions from the parsed PDA.
    """
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')  # Left to right

    for state in pda['states']:
        shape = 'doublecircle' if state in pda['accept_states'] else 'circle'
        dot.node(state, shape=shape)

    dot.node('', shape='none')  # Invisible start arrow
    dot.edge('', pda['start_state'])

    for (cur_state, inp, stack_top), transitions in pda['transitions'].items():
        for next_state, push in transitions:
            label = f"({inp if inp else 'ε'}, {stack_top} → {push})"
            dot.edge(cur_state, next_state, label=label)

    dot.render(filename=output_file, cleanup=True)
    return output_file + ".png"

