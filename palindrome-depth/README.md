# Palindrome Depth

Take a number, add it to its reverse, and repeat until the result is a palindrome. For example, 87 takes four steps:

```
87 + 78 = 165
165 + 561 = 726
726 + 627 = 1353
1353 + 3531 = 4884
```

The number of steps is the number's *depth*. This script groups every integer from 1 to a limit by depth. Some numbers, like 196, are not known to ever reach a palindrome (these are called [Lychrel numbers](https://en.wikipedia.org/wiki/Lychrel_number)), so the search stops after 1000 steps.

## Usage

```bash
python palindrome_depth.py
```

```
Classify numbers from 1 up to: 200
Depth 0: [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, ...]
Depth 1: [10, 12, 13, 14, 15, 16, 17, 18, 20, ...]
...
Depth 24: [89, 98]
No palindrome within 1000 steps: [196]
```
