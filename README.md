st3awk
======

`st3awk` allows you to seamlessly process text with awk from within Sublime Text.

What is awk?
> AWK (awk /ɔːk/)[4] is a domain-specific language designed for text processing and typically used as a data extraction and reporting tool.
https://en.wikipedia.org/wiki/AWK

Warning: `st3awk` has only be tested on Windows.

NOTE: awk must either be available in `PATH` or overriden by `awk = "<absolute-path>"` in `Packages/User/awk.sublime-settings`.

Features:
- Supports multi-select.
- Supports quick panel expressions.
- Supports script/program file.
- Supports edit inplace or writing output to new tab/view.

Available commands:
- Awk: Run expression inplace
- Awk: Run expression new tab
- Awk: Run script inplace
- Awk: Run script new tab
- Awk: Open script
