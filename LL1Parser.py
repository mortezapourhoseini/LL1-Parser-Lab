import os
from collections import OrderedDict

class LL1Parser:
    def __init__(self):
        self.grammar = OrderedDict()
        self.non_terminals = []
        self.terminals = []
        self.first_sets = {}
        self.follow_sets = {}
        self.parse_table = {}
        self.start_symbol = None

    def read_grammar(self, file_path):
        """Read grammar from file"""
        if not os.path.exists(file_path):
            print("Error: File not found!")
            return False
            
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '->' not in line:
                print(f"Format error in line: {line}")
                continue
                
            parts = line.split('->')
            non_terminal = parts[0].strip()
            productions = [p.split() for p in parts[1].split('|')]
            
            if non_terminal not in self.grammar:
                self.grammar[non_terminal] = []
                
            self.grammar[non_terminal].extend(productions)
            
            if non_terminal not in self.non_terminals:
                self.non_terminals.append(non_terminal)
        
        if not self.grammar:
            print("Error: No production rules found!")
            return False
            
        self.start_symbol = list(self.grammar.keys())[0]
        self._find_terminals()
        return True

    def _find_terminals(self):
        """Find all terminals in the grammar"""
        terminals = set()
        for non_terminal, productions in self.grammar.items():
            for production in productions:
                for symbol in production:
                    if symbol != 'ε' and symbol not in self.non_terminals:
                        terminals.add(symbol)
        
        self.terminals = sorted(list(terminals))
        self.terminals.append('$')  # Add end of input marker

    def compute_first_sets(self):
        """Compute FIRST sets for all non-terminals"""
        self.first_sets = {nt: set() for nt in self.non_terminals}
        changed = True
        
        while changed:
            changed = False
            for non_terminal in self.non_terminals:
                for production in self.grammar[non_terminal]:
                    first_set = self._compute_first_for_sequence(production)
                    if not first_set.issubset(self.first_sets[non_terminal]):
                        self.first_sets[non_terminal].update(first_set)
                        changed = True
        
        return self.first_sets

    def _compute_first_for_sequence(self, sequence):
        """Compute FIRST for a sequence of symbols"""
        if not sequence:
            return set()
            
        first_set = set()
        for i, symbol in enumerate(sequence):
            if symbol == 'ε':
                first_set.add('ε')
                break
            elif symbol in self.terminals:
                first_set.add(symbol)
                break
            else:  # Non-terminal
                symbol_first = self.first_sets.get(symbol, set()).copy()
                if 'ε' in symbol_first:
                    symbol_first.remove('ε')
                    first_set.update(symbol_first)
                    if i == len(sequence) - 1:  # Last symbol
                        first_set.add('ε')
                else:
                    first_set.update(symbol_first)
                    break
        
        return first_set

    def compute_follow_sets(self):
        """Compute FOLLOW sets for all non-terminals"""
        self.follow_sets = {nt: set() for nt in self.non_terminals}
        self.follow_sets[self.start_symbol].add('$')
        changed = True
        
        while changed:
            changed = False
            for non_terminal in self.non_terminals:
                for production in self.grammar[non_terminal]:
                    for i, symbol in enumerate(production):
                        if symbol in self.non_terminals:
                            # Compute FIRST for the remainder of the sequence
                            remainder = production[i+1:]
                            first_remainder = self._compute_first_for_sequence(remainder)
                            
                            # Rule 1: Add First(β) to Follow(B) (except ε)
                            new_follows = first_remainder - {'ε'}
                            if not new_follows.issubset(self.follow_sets[symbol]):
                                self.follow_sets[symbol].update(new_follows)
                                changed = True
                            
                            # Rule 2: If ε in First(β) or β is empty
                            if 'ε' in first_remainder or i == len(production) - 1:
                                if not self.follow_sets[non_terminal].issubset(self.follow_sets[symbol]):
                                    self.follow_sets[symbol].update(self.follow_sets[non_terminal])
                                    changed = True
        
        return self.follow_sets

    def build_parse_table(self):
        """Build LL(1) parse table"""
        self.parse_table = {}
        
        # Initialize table
        for non_terminal in self.non_terminals:
            for terminal in self.terminals:
                self.parse_table[(non_terminal, terminal)] = None
        
        # Fill table
        for non_terminal in self.non_terminals:
            for production in self.grammar[non_terminal]:
                first_alpha = self._compute_first_for_sequence(production)
                
                for terminal in first_alpha:
                    if terminal != 'ε':
                        if self.parse_table[(non_terminal, terminal)] is not None:
                            print(f"Warning: Conflict in parse table for ({non_terminal}, {terminal})")
                        self.parse_table[(non_terminal, terminal)] = production
                
                if 'ε' in first_alpha:
                    for terminal in self.follow_sets[non_terminal]:
                        if self.parse_table[(non_terminal, terminal)] is not None:
                            print(f"Warning: Conflict in parse table for ({non_terminal}, {terminal})")
                        self.parse_table[(non_terminal, terminal)] = production
        
        return self.parse_table

    def parse_input(self, input_string):
        """Parse an input string using the parse table"""
        stack = ['$', self.start_symbol]
        input_string = input_string.split()
        input_string.append('$')
        pointer = 0
        steps = []
        accepted = False
        
        while len(stack) > 0:
            top = stack[-1]
            current_input = input_string[pointer]
            
            step = {
                'stack': ' '.join(stack),
                'input': ' '.join(input_string[pointer:]),
                'action': ''
            }
            
            if top == '$' and current_input == '$':
                step['action'] = 'Accept'
                steps.append(step)
                accepted = True
                break
            elif top in self.terminals:
                if top == current_input:
                    stack.pop()
                    pointer += 1
                    step['action'] = f'Match terminal: {top}'
                else:
                    step['action'] = f'Error: Expected {top} but got {current_input}'
                    steps.append(step)
                    break
            else:  # Non-terminal
                production = self.parse_table.get((top, current_input), None)
                if production is not None:
                    stack.pop()
                    if production != ['ε']:
                        # Push production in reverse order
                        for symbol in reversed(production):
                            stack.append(symbol)
                    step['action'] = f'Apply rule: {top} -> {" ".join(production)}'
                else:
                    step['action'] = f'Error: No rule for ({top}, {current_input})'
                    steps.append(step)
                    break
            
            steps.append(step)
        
        return steps, accepted

    def display_first_sets(self):
        """Display FIRST sets"""
        print("\nFIRST Sets:")
        print("=" * 50)
        for non_terminal, first_set in self.first_sets.items():
            print(f"FIRST({non_terminal}) = {{{', '.join(sorted(first_set))}}}")

    def display_follow_sets(self):
        """Display FOLLOW sets"""
        print("\nFOLLOW Sets:")
        print("=" * 50)
        for non_terminal, follow_set in self.follow_sets.items():
            print(f"FOLLOW({non_terminal}) = {{{', '.join(sorted(follow_set))}}}")

    def display_parse_table(self):
        """Display parse table"""
        print("\nLL(1) Parse Table:")
        print("=" * 80)
        
        # Header
        header = ["Non-Terminal"] + self.terminals
        print("{:<15}".format(header[0]), end="")
        for terminal in header[1:]:
            print("{:<20}".format(terminal), end="")
        print()
        
        # Rows
        for non_terminal in self.non_terminals:
            print("{:<15}".format(non_terminal), end="")
            for terminal in self.terminals:
                production = self.parse_table.get((non_terminal, terminal), None)
                if production is not None:
                    production_str = f"{non_terminal} -> {' '.join(production)}"
                    print("{:<20}".format(production_str[:18] + "..." if len(production_str) > 18 else production_str), end="")
                else:
                    print("{:<20}".format(""), end="")
            print()

    def display_parsing_steps(self, steps, accepted):
        """Display parsing steps"""
        print("\nParsing Steps:")
        print("=" * 80)
        print("{:<30} {:<30} {:<30}".format("Stack", "Input", "Action"))
        print("-" * 80)
        
        for step in steps:
            print("{:<30} {:<30} {:<30}".format(
                step['stack'][:28] + "..." if len(step['stack']) > 28 else step['stack'],
                step['input'][:28] + "..." if len(step['input']) > 28 else step['input'],
                step['action'][:28] + "..." if len(step['action']) > 28 else step['action']
            ))
        
        print("\nResult: " + ("Input accepted!" if accepted else "Input rejected!"))

def main():
    """Main function and user interface"""
    parser = LL1Parser()
    
    print("=" * 60)
    print("LL(1) Parser")
    print("=" * 60)
    
    # Get grammar file from user
    file_path = input("Please enter the path to the grammar file: ")
    if not parser.read_grammar(file_path):
        return
    
    # Compute sets and table
    print("\nComputing FIRST sets...")
    parser.compute_first_sets()
    
    print("Computing FOLLOW sets...")
    parser.compute_follow_sets()
    
    print("Building parse table...")
    parser.build_parse_table()
    
    # Display menu
    while True:
        print("\n" + "=" * 40)
        print("Main Menu")
        print("=" * 40)
        print("1. Display FIRST sets")
        print("2. Display FOLLOW sets")
        print("3. Display parse table")
        print("4. Parse an input string")
        print("5. Exit")
        
        choice = input("\nPlease select an option (1-5): ").strip()
        
        if choice == '1':
            parser.display_first_sets()
        elif choice == '2':
            parser.display_follow_sets()
        elif choice == '3':
            parser.display_parse_table()
        elif choice == '4':
            input_string = input("Please enter input string (space separated): ")
            steps, accepted = parser.parse_input(input_string)
            parser.display_parsing_steps(steps, accepted)
        elif choice == '5':
            print("Exiting program...")
            break
        else:
            print("Invalid option! Please enter a number between 1-5.")

if __name__ == "__main__":
    main()
