# pda_simulator.py
import json
from collections import deque

def parse_pda(raw):
    try:
        data = json.loads(raw)
        print("✅ Loaded JSON transitions:", data['transitions'])
    except json.JSONDecodeError:
        return _parse_pda_text(raw)

    flat = {}
    for state, by_input in data['transitions'].items():
        for inp_sym, by_stack in by_input.items():
            # normalize any variant of epsilon to empty string
            key_input = inp_sym.strip()
            if key_input.lower() in ('ε','epsilon','eps','empty',''):
                inp = ''
            else:
                inp = key_input

            for stack_top, actions in by_stack.items():
                st = stack_top.strip()
                key = (state, inp, st)
                flat.setdefault(key, [])
                # actions may be a list‐of‐lists or a single pair
                if isinstance(actions, list) and actions and isinstance(actions[0], list):
                    for nxt, push in actions:
                        flat[key].append((nxt, push))
                else:
                    # single transition
                    nxt, push = actions
                    flat[key].append((nxt, push))

    # Debug: dump the transition table
    print("\n[PDA PARSER] Flattened transitions:")
    for k, v in flat.items():
        print(f"    {k} → {v}")
    print()

    return {
        'states': set(data['states']),
        'input_symbols': set(data['input_symbols']),
        'stack_symbols': set(data['stack_symbols']),
        'transitions': flat,
        'start_state': data['start_state'],
        'accept_states': set(data['accept_states']),
        'start_stack': data['start_stack']
    }

def _parse_pda_text(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    pda = {
        'states': set(),
        'input_symbols': set(),
        'stack_symbols': set(),
        'transitions': {},
        'start_state': '',
        'accept_states': set(),
        'start_stack': ''
    }
    for line in lines:
        if ':' in line and '->' not in line:
            k,v = [x.strip() for x in line.split(':',1)]
            vals = [i.strip() for i in v.split(',') if i.strip()]
            if k=='states': pda['states']=set(vals)
            elif k=='input_symbols': pda['input_symbols']=set(vals)
            elif k=='stack_symbols': pda['stack_symbols']=set(vals)
            elif k=='start_state': pda['start_state']=vals[0]
            elif k=='accept_states': pda['accept_states']=set(vals)
            elif k=='start_stack': pda['start_stack']=vals[0]
        elif '->' in line:
            lhs,rhs = line.split('->')
            st,inp_sym,stk = [x.strip() for x in lhs.split(',')]
            nxt,push = [x.strip() for x in rhs.split(',')]
            inp = '' if inp_sym in ('ε','epsilon','') else inp_sym
            key=(st,inp,stk)
            pda['transitions'].setdefault(key,[]).append((nxt,push))

    print("\n[PDA CUSTOM PARSE] Transitions:")
    for k,v in pda['transitions'].items():
        print(f"    {k} → {v}")
    print()
    return pda

def simulate_pda(pda, input_str):
    """
    Simulate PDA with BFS, but only allow ε-moves when no real move exists.
    Accept by final state once input is consumed.
    """
    from collections import deque

    # Each config is (state, remaining_input, stack, trace)
    queue = deque([ (pda['start_state'], input_str, [pda['start_stack']], []) ])

    while queue:
        state, rem, stack, trace = queue.popleft()
        step = {'state':state, 'input':rem, 'stack':list(stack)}
        print(f"[CONFIG] {step}")

        # Accept if input empty and in accept state
        if rem == '' and state in pda['accept_states']:
            print("[PDA SIM] Accepted at", step)
            return True, trace + [step]

        if not stack:
            continue

        top = stack[-1]
        real_sym = rem[0] if rem else ''

        # Decide possible moves: real_sym only if it exists, else both
        if (state, real_sym, top) in pda['transitions']:
            symbols = [real_sym]
        else:
            symbols = [real_sym, '']

        for sym in symbols:
            key = (state, sym, top)
            print("  lookup", key, "→", pda['transitions'].get(key))
            if key not in pda['transitions']:
                continue

            for (next_state, push_str) in pda['transitions'][key]:
                new_rem = rem[1:] if sym and rem.startswith(sym) else rem
                new_stack = stack[:-1]  # pop

                if push_str != 'ε':
                    # push characters in reverse order
                    new_stack += list(push_str[::-1])

                queue.append((next_state, new_rem, new_stack, trace + [step]))
        print()

    print("[PDA SIM] All paths exhausted; rejecting.")
    return False, []

