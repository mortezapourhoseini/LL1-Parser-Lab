# LL1 Parser Lab

A Python implementation of an LL(1) parser with grammar analysis capabilities.

## Features

- Computes FIRST and FOLLOW sets for context-free grammars
- Builds LL(1) parse tables
- Parses input strings with detailed step-by-step execution
- Terminal-based user interface

## File Naming Convention

- Grammar files: `G#_Description.txt` (e.g., `G2_Arithmetic.txt`)
- Test files: `T#_Description.txt` (e.g., `T2_Arithmetic.txt`)

## Available Grammars

1. `G2_Arithmetic.txt` - Simple arithmetic expressions
2. `G3_if-else.txt` - If-else conditional statements
3. `G4_declarations.txt` - Variable and function declarations

   - You can also create your own grammar file with the appropriate format

## Usage

1. Run the parser:
   ```bash
   python ll1_parser.py
   ```

2. Enter the path to a grammar file when prompted (e.g., `G2_Arithmetic.txt`)

3. Use the menu options to:
   - View FIRST and FOLLOW sets
   - View the parse table
   - Parse input strings from corresponding test files

## Example

To test the arithmetic grammar:
1. Use grammar file: `G2_Arithmetic.txt`
2. Use test input from: `T2_Arithmetic.txt`

This implementation helps understand the core concepts of compiler design and LL(1) parsing.
