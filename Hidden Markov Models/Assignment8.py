"""
Part of Speech Tagger using HMM 
Jake Traut
12/1/16
"""
from __future__ import division
from collections import defaultdict
import sys

#GLOBALS
TRANS_PROB = defaultdict(dict)
EMISS_PROB = defaultdict(dict)
START_PROB = {}
TAG_FREQ = {}
LINES = []
TAGS = []
WORDS = []


def calc_trans(allTags):
	tag1tag2Freq = defaultdict(dict)
	
	for tag1 in allTags:
		for tag2 in allTags:
			TRANS_PROB[tag1][tag2] = 0
			tag1tag2Freq[tag1][tag2] = 0
			
	lastTag = None 
	for tag in TAGS:
		if(tag == 'EEEE'):
			tag1tag2Freq[lastTag][tag] += 1
			lastTag = None
			continue
		if(lastTag != None):
			tag1tag2Freq[lastTag][tag] += 1 #times tag follows lastTag 	
			
		lastTag = tag
			
	for tag1 in allTags:
		if (tag1 == 'SSSS'):
			continue
		for tag2 in allTags:
			if (tag2 == 'EEEE'):
				continue
			TRANS_PROB[tag2][tag1] = tag1tag2Freq[tag2][tag1] / TAG_FREQ[tag2]	
	
	return TRANS_PROB
	
def calc_emiss(allWords, allTags):	
	wordTagFreq = defaultdict(dict)
	
	for word in allWords:
		for tag in allTags:
			EMISS_PROB[tag][word] = 0
			wordTagFreq[word][tag] = 0
	
	EMISS_PROB['SSSS']['SSSS'] = 1.0
	EMISS_PROB['EEEE']['EEEE'] = 1.0
	
	for line in LINES: 
		if(line != 'SSSS' and line != 'EEEE'):
			lineWord = line.rpartition('\t')[0]
			lineTag = line.rpartition('\t')[2]
			
			wordTagFreq[lineWord][lineTag] += 1

	for word in allWords:
		if(word == 'SSSS' or word == 'EEEE'):
			continue
		for tag in allTags:
			if(tag == 'SSSS' or tag == 'EEEE'):
				continue
			EMISS_PROB[tag][word] = wordTagFreq[word][tag] / TAG_FREQ[tag]
				
	return EMISS_PROB
	
	
def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    for st in states:
		V[0][st] = {"prob": start_p[st] * emit_p[st][obs[0]], "prev": None}
    # Run Viterbi when t > 0

    for t in range(1, len(obs)):
        V.append({})
        for st in states:
            max_tr_prob = max(V[t-1][prev_st]["prob"]*trans_p[prev_st][st] for prev_st in states)
            for prev_st in states:
				if V[t-1][prev_st]["prob"] * trans_p[prev_st][st] == max_tr_prob:
					max_prob = max_tr_prob * emit_p[st][obs[t]]
					V[t][st] = {"prob": max_prob, "prev": prev_st}
					break
		
    opt = []
    # The highest probability
    max_prob = max(value["prob"] for value in V[-1].values())
    previous = None
    # Get most probable state and its backtrack
    for st, data in V[-1].items():
        #print st, data
        if data["prob"] == max_prob:
            opt.append(st)
            previous = st
            break
    # Follow the backtrack till the first observation
    for t in range(len(V) - 2, -1, -1):
        opt.insert(0, V[t + 1][previous]["prev"])
        previous = V[t + 1][previous]["prev"]

    print 'Translated to tags:	' + ' '.join(opt) #+ ' with highest probability of %s' % max_prob

def main():
	
	with open("penntree.tag", "r") as sentences:
		LINES.append("SSSS")
		TAGS.append("SSSS")
		WORDS.append("SSSS")
		TAG_FREQ['SSSS'] = 1
		TAG_FREQ['EEEE'] = 1
		for line in sentences:
				
			if(line == "\n"):
				LINES.append("EEEE")
				LINES.append("SSSS")
				TAGS.append("EEEE")
				TAGS.append("SSSS")
				WORDS.append("EEEE")
				WORDS.append("SSSS")
				TAG_FREQ['SSSS'] += 1
				TAG_FREQ['EEEE'] += 1
			else:
				LINES.append(line.rstrip())
				
				tag = line.rpartition('\t')[2]
				tag = tag.rstrip()
				if tag in TAG_FREQ:
					TAG_FREQ[tag] += 1
				else:
					TAG_FREQ[tag] = 1
				TAGS.append(tag)		
				
				word = line.rpartition('\t')[0]
				word = word.rstrip()

				WORDS.append(word)		
	
		LINES.append("EEEE")
		TAGS.append("EEEE")
		WORDS.append("EEEE")

	allTags = list(set(TAGS))
	allWords = list(set(WORDS))
	
	#populate starting probabilities 
	for tag in allTags:
		if(tag == 'SSSS'):
			START_PROB[tag] = 1.0
		else:
			START_PROB[tag] = 0.0
					
	calc_trans(allTags)
	calc_emiss(allWords, allTags)	
	
	states = allTags
	
	sentence = "SSSS Can a can can a can?"
	
	observations = sentence.split()
	endSentence = observations[-1]
	lastWord = endSentence[:-1]
	punctuation = endSentence[-1]
	observations[-1] = lastWord
	observations.append(punctuation)
	observations.append('EEEE')
	
	print "Sentence:		" + sentence + " EEEE"
	
	print TRANS_PROB['MD']['MD']
	
	print EMISS_PROB['MD']['can']
	
	viterbi(observations, states, START_PROB, TRANS_PROB, EMISS_PROB)

if __name__ == "__main__":
	main()
