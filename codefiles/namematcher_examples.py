# NameMatcher
# Example code for using the classes in namematcher.py
# -----------------------------------------------------------------------------

import re
from namematcher import NameMatcher

name_matcher = NameMatcher()

# Match score for two names:
score = name_matcher.match_names('Nat Ahn', 'Natalie Ahn')
print(score)
# -----------------------------------------------------------------------------
# 0.9875
# -----------------------------------------------------------------------------

score = name_matcher.match_names('Natalie Ahn', 'Gabrielle Elul')
print(score)
# -----------------------------------------------------------------------------
# 0.222080208393
# -----------------------------------------------------------------------------


# Use a different string distance metric
name_matcher = NameMatcher(distfun='levenshtein') # default
name_matcher = NameMatcher(distfun='jaro_winkler')
name_matcher = NameMatcher(distfun=my_callable_function)


# Find the best matches for a list of names in another list of names:
sample_names = ['Nat G. Ahn', 'John Doe', 'AJ Smith', 'Rob Smith']
pop_names = ['Ahn, Natalie Grace', 'Ahn, Nancy G.', 'Smith, Adam Jr.', 'Smith, Peter Robert', 'Doe, Paul',
					'Doh, John', 'Anh, Nathan', 'Smith, Albert III']

matches = name_matcher.find_closest_names(sample_names, pop_names)
for i in range(len(matches)):
	orig_name = sample_names[i]
	pop_name, pop_index, score = matches[i]
	print('For name: %s, best match: %s, score %f' % (orig_name, pop_name, score))

# -----------------------------------------------------------------------------
# For name: Nat G. Ahn, best match: Ahn, Nancy G., score 0.969107
# For name: John Doe, best match: Doh, John, score 0.863038
# For name: AJ Smith, best match: Smith, Adam Jr., score 0.854846
# For name: Rob Smith, best match: Smith, Peter Robert, score 0.916250
# -----------------------------------------------------------------------------


# To change parameters, e.g. to reduce or eliminate the discount on a match
# between a first/middle initial and first/middle name. In the example above,
# "Nat G. Ahn" was matched to "Ahn, Nancy G." though it should probably have matched
# "Ahn, Natalie Grace". That's because matching the middle initials "G." and "G."
# got a higher score than matching "G." to "Grace". If we change the parameter
# 'disc_initial' to be closer to 1, the name we want becomes the best match.

name_matcher.params['disc_initial'] = 0.9

matches = name_matcher.find_closest_names(sample_names, pop_names)
for i in range(len(matches)):
	orig_name = sample_names[i]
	pop_name, pop_index, score = matches[i]
	print('For name: %s, best match: %s, score %f' % (orig_name, pop_name, score))

# -----------------------------------------------------------------------------
# For name: Nat G. Ahn, best match: Ahn, Natalie Grace, score 0.981250
# For name: John Doe, best match: Doh, John, score 0.863038
# For name: AJ Smith, best match: Smith, Adam Jr., score 0.854846
# For name: Rob Smith, best match: Smith, Peter Robert, score 0.916250
# -----------------------------------------------------------------------------

# We could also try reducing or eliminating the discount on an abbreviation
# (i.e. a shortened version of a first/middle name that's longer than an initial)
# so that "Nat" and "Natalie" are treated as a perfect or nearly perfect match
# (and the one-letter difference between "Nat" and "Nancy" drops that pair
# to second place).

name_matcher.params['disc_initial'] = 0.8
name_matcher.params['disc_abbrev'] = 0.99

matches = name_matcher.find_closest_names(sample_names, pop_names)
for i in range(len(matches)):
	orig_name = sample_names[i]
	pop_name, pop_index, score = matches[i]
	print('For name: %s, best match: %s, score %f' % (orig_name, pop_name, score))

# -----------------------------------------------------------------------------
# For name: Nat G. Ahn, best match: Ahn, Natalie Grace, score 0.973750
# For name: John Doe, best match: Doh, John, score 0.863038
# For name: AJ Smith, best match: Smith, Adam Jr., score 0.854846
# For name: Rob Smith, best match: Smith, Peter Robert, score 0.916250
# -----------------------------------------------------------------------------

