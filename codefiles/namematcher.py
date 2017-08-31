# Name Matching Tools
# Tools for matching person names
# -----------------------------------------------------------------------------
# Class included: NameMatcher
# Public methods: match_names(name1, name2)
#                 parse_name(name)
#                 find_closest_names(target_names, other_names)
# -----------------------------------------------------------------------------
# Author: Natalie Ahn
# Last revised: August 2017

import re
import csv
import numpy as np
from math import log
from statistics import mean
from bisect import bisect_left
from nltk.metrics import edit_distance
from jellyfish import jaro_winkler

class NameMatcher:
	suffixes = {'junior', 'jr', 'senior', 'sr', 'ii', 'iii', 'iv'}
	weight_order = ['first_names', 'last_name', 'suffix']

	def __init__(self, distfun='levenshtein'):
		if distfun == 'levenshtein':
			self.distfun = self._levenshtein_log
		elif distfun == 'jaro_winkler':
			self.distfun = lambda str1,str2: 1 - jaro_winkler(str1, str2)
		else: self.distfun = distfun
		# The following parameters have been optimized on a limited initial dataset.
		# Users may wish to adjust and experiment with them on their own dataset.
		# Detailed parameter explanations will be provided in the README file.
		self.params = {'weights':[0.25, 0.66, 0.09],
					  'disc_abbrev':0.95, 'disc_abbrev_notstart':0.6,
					  'disc_missing_fname':0.7, 'disc_missing_mname':0.95,
					  'disc_missing_nickname':0.8, 'disc_initial':0.6,
					  'disc_initial_mismatch':0.4, 'disc_acronym':0.5}

	def _levenshtein_pct(self, str1, str2):
		return edit_distance(str1, str2) / max(len(str1),len(str2))

	def _levenshtein_log(self, str1, str2):
		edits = edit_distance(str1, str2)
		log_edits = 1 - log(max(len(str1),len(str2)) - edits + 1,
							max(len(str1),len(str2)) + 1)
		return log_edits

	def match_names(self, name1, name2, speed='fast', min_last_sim=0.8):
		name_dict1 = self.parse_name(name1.lower())
		name_dict2 = self.parse_name(name2.lower())
		sims = {}
		sims['suffix'] = self._suffix_sim(name_dict1['suffix'], name_dict2['suffix'])
		sims['last_name'] = 1 - self.distfun(name_dict1['last_name'], name_dict2['last_name'])
		if speed == 'fast' and sims['last_name'] < min_last_sim:
			sims['first_names'] = 1 - self.distfun(' '.join(name_dict1['last_name']),
												   ' '.join(name_dict2['last_name']))
			return self._weighted_sum(sims)
		jr1 = self._suffix_acron_letter(name_dict1['suffix'])
		jr2 = self._suffix_acron_letter(name_dict2['suffix'])
		version_sims = []
		for fnames1 in [name_dict1[key] for key in ['first_names', 'nicknames']]:
			for fnames2 in [name_dict2[key] for key in ['first_names', 'nicknames']]:
				version_sims.append(self._max_subseq_sim(fnames1, fnames2, jr1, jr2))
		sims['first_names'] = max(version_sims)
		if (name_dict1['nicknames'] and not name_dict2['nicknames']) \
		or (name_dict2['nicknames'] and not name_dict1['nicknames']):
			sims['first_names'] *= self.params['disc_missing_nickname']
		return self._weighted_sum(sims)

	def parse_name(self, name):
		name_dict = {'first_names':[], 'last_name':'', 'nicknames':[]}
		last_tok = re.split('[\s,]', name)[-1]
		if last_tok.lower().replace('.', '') in self.suffixes:
			name_dict['suffix'] = last_tok
			name = name[:-len(last_tok)].strip()
		else: name_dict['suffix'] = ''
		if re.search(',', name):
			parts = re.split(',', name)
			if len(parts) > 1:
				name_dict['last_name'] = parts[0]
				name = ' '.join(parts[1:]).strip()
		parts = [x for x in re.split('[ .]', name) if x]
		if parts and not name_dict['last_name']:
			name_dict['last_name'] = parts[-1]
			parts = parts[:-1]
		for part in parts:
			nickname_match = re.match(r'[\"\'\(\[](.+)[\"\'\)\]]', part)
			if nickname_match:
				name_dict['nicknames'].append(nickname_match.group(1))
			else: name_dict['first_names'].append(part)
		return name_dict

	def _suffix_sim(self, suffix1, suffix2):
		s1, s2 = suffix1.strip('.').lower(), suffix2.strip('.').lower()
		if s1 == s2: return 1
		if any(s == 'junior' for s in [s1, s2]) \
		and any(s == 'jr' for s in [s1, s2]): return 1
		if any(s == 'senior' for s in [s1, s2]) \
		and any(s == 'sr' for s in [s1, s2]): return 1
		if not s1 or not s2: return 0.5
		return 0

	def _suffix_acron_letter(self, suffix):
		if suffix and (suffix.lower()[0] == 'j' or suffix.lower() == 'ii'):
			return 'j'
		return ''

	def _max_subseq_sim(self, fnames1, fnames2, jr1='', jr2=''):
		name_order = sorted([(fnames1, jr1), (fnames2, jr2)], key=lambda x:len(x[0]))
		(shorter, jrshort), (longer, jrlong) = name_order
		if not shorter: return 0
		sequence_sims = []
		last_initial_match = False
		for s in range(len(longer) - len(shorter) + 1):
			token_sims = []
			for t in range(len(shorter)):
				if len(shorter[t])==1 and len(longer[s+t])==1 \
				and shorter[t][0]==longer[s+t][0]:
					token_sims.append(1)
					last_initial_match = True
				elif len(shorter[t])==1 or len(longer[s+t])==1:
					if shorter[t][0]==longer[s+t][0]:
						token_sims.append(self.params['disc_initial'])
						last_initial_match = True
					else:
						if last_initial_match:
							if (len(shorter[t])==1 and shorter[t][0] == jrlong) \
							or (len(longer[s+t])==1 and longer[s+t][0] == jrshort):
								token_sims.append(self.params['disc_acronym'])
						else: token_sims.append(self.params['disc_initial_mismatch'])
						last_initial_match = False
				else:
					substr_sim = self._max_substr_sim(shorter[t], longer[s+t])
					if len(shorter[t])==2 and shorter[t][0] == longer[s+t][0] \
					and ((s+t+1 < len(longer) and shorter[t][1] == longer[s+t+1][0]) \
					or shorter[t][1] == jrlong):
						if self.params['disc_acronym'] > substr_sim:
							substr_sim = self.params['disc_acronym']
					elif len(longer[s+t])==2 and longer[s+t][0] == shorter[t][0] \
					and ((t+1 < len(shorter) and longer[s+t][1] == shorter[t+1][0]) \
					or longer[s+t][1] == jrshort):
						if self.params['disc_acronym'] > substr_sim:
							substr_sim = self.params['disc_acronym']
					token_sims.append(substr_sim)
					last_initial_match = False
			if token_sims: sequence_sims.append(mean(token_sims))
		sim = max(sequence_sims)
		if sequence_sims[0] != sim: sim *= self.params['disc_missing_fname']
		elif len(shorter) != len(longer):
			if len(longer) == len(shorter) + 1 and jrshort and longer[-1] == 'j' \
			and self.params['disc_acronym'] > self.params['disc_missing_mname']:
				sim *= self.params['disc_acronym']
			else: sim *= self.params['disc_missing_mname']
		return sim

	def _max_substr_sim(self, str1, str2):
		if len(str1)==0 or len(str2)==0: return 0
		(shorter, longer) = sorted([str1, str2], key=lambda x:len(x))
		subsims = []
		for i in range(len(longer) - len(shorter) + 1):
			subsims.append(1 - self.distfun(shorter, longer[i:i+len(shorter)]))
		sim = max(subsims)
		if len(longer)!=len(shorter):
			sim *= self.params['disc_abbrev']
		if subsims.index(max(subsims)) > 0:
			sim *= self.params['disc_abbrev_notstart']
		return sim

	def _weighted_sum(self, sims_dict):
		sims_list = [sims_dict[key] for key in self.weight_order]
		sims_weighted = np.multiply(sims_list, self.params['weights'])
		return sum(sims_weighted)

	def find_closest_names(self, target_names, other_names):
		targets_dicts = [self.parse_name(name) for name in target_names]
		others_dicts = [self.parse_name(name) for name in other_names]
		others_enum = [(self._name_string_std(name_dict), name_dict, i) \
						for i,name_dict in enumerate(others_dicts)]
		others_sorted = sorted(others_enum)
		matches = []
		for target_dict in targets_dicts:
			target_std = self._name_string_std(target_dict)
			i = bisect_left(others_sorted, (target_std,))
			best_sim, best_i = 0, i
			if i == len(others_sorted): best_i = i - 1
			j = i - 1
			cont_left = i > 0
			cont_right = j < len(others_sorted) - 1
			while cont_left or cont_right:
				if cont_left and i > 0:
					i -= 1
					sims = {'suffix':self._suffix_sim(target_dict['suffix'], others_sorted[i][1]['suffix']),
							'last_name':1 - self.distfun(target_dict['last_name'], others_sorted[i][1]['last_name']),
							'first_names':1}
					if self._weighted_sum(sims) < best_sim:
					 	cont_left = False
					else:
					 	sim = self.match_names(target_std, others_sorted[j][0], speed='slow')
					 	if sim > best_sim:
					 		best_sim, best_i = sim, i
				else: cont_left = False
				if cont_right and j < len(others_sorted) - 1:
					j += 1
					sims = {'suffix':self._suffix_sim(target_dict['suffix'], others_sorted[j][1]['suffix']),
							'last_name':1 - self.distfun(target_dict['last_name'], others_sorted[j][1]['last_name']),
							'first_names':1}		
					if self._weighted_sum(sims) < best_sim:
					 	cont_right = False
					else:
					 	sim = self.match_names(target_std, others_sorted[j][0], speed='slow')
					 	if sim > best_sim:
					 		best_sim, best_i = sim, j
				else: cont_right = False
			best_i_orig = others_sorted[best_i][2]
			matches.append((other_names[best_i_orig], best_i_orig, best_sim))
		return matches

	def _name_string_std(self, name_dict):
		return (name_dict['last_name'] + ', ' \
				+ ' '.join(name_dict['first_names']) + ' ' \
				+ name_dict['suffix']).strip()


