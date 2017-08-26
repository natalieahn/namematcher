# NameMatcher
Person name matching tools

This repository contains Python code for a set of tools to match person names,
including functionality specific to names beyond simple fuzzy string matching.
The functions handle names ordered either "First [Middle] Last" or "Last, First [Middle]".
They account for suffixes (e.g. "Jr", "III"), initials in place of first or middle names,
and abbreviations or acronyms (e.g. "AJ Smith" and "Adam Smith Jr").

The functions also account for missing first or middle names, such as when a person often
goes by their middle name. With the two strings "John Adam Smith" and "Adam Smith", the
functions will look for the closest matching subsequence of first and middle names, such that
"John" is not matched to "Adam" (yielding a similarity score of 0) but instead "Adam" is
matched to "Adam" (with a similarity score of 1), but with a discount for the subsequence
not starting at the beginning of the string, meaning there is a missing first name.

There are a number of such discounts that are included as parameters (e.g. for a first name
matching an initial, rather than using the full string edit distance, which would give these
two strings a very low similarity score, though initials are common in person names). The
provided parameter values have been optimized on a small training set, but users can adjust
these parameters through experimentation on their own datasets.

Users can also choose a raw string distance metric, specifying Levenshtein edit distance with
"levenshtein", Jaro Winkler with "jaro_winkler", or supplying their own callable function.
A function is also included for matching names from one target list to another list of population
names, which sorts the population list alphabetically and uses a binary search to speed up
the process of finding the closest match to each target name.

Full documentation for the included methods and parameters is included in the file doc.txt,
and examples for using the code are inluced in the file examples.py.


### Copyright

Copyright 2017 Natalie Ahn

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


