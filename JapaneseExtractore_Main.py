#!/usr/bin/env python
#-*- coding: utf-8 -*-
import nltk
import string
import operator
from konlpy.tag import Komoran
from re import compile as _Re
from konlpy.tag import Kkma
# from jNlp.jTokenize import jTokenize

def isPunct(word):
	punctuationList = ["[","^"," 「","」","!","?","。","．","）","]","*","[","!","?","。"]
	return len(word) == 1 and word in punctuationList

def isNumeric(word):
	try:
		float(word) if '.' in word else int(word)
		return True
	except ValueError:
		return False

class RakeKeywordExtractor:

	def __init__(self):
		# self.stopwords = set(stopwords.words('japanese'))
		self.stopwords = set(nltk.corpus.stopwords.words('japanese'))
		# index = 0
		# for stopword in self.stopwords[0].itervalues():
		# 	print (index+1,"----",self.stopword)
		# for words in self.stopwords:
		# 	if words == "なったら":
		# 		print "Found match"
		self.top_fraction = 1 # consider top third candidate keywords by score


	def _generate_candidate_keywords(self, sentences):
		phrase_list = []
		for sentence in sentences:
			words = map(lambda x: "|" if x in self.stopwords else x,
			self.testTokens(sentence))
			phrase = []
			for word in words:
				print ("word in genereate phrase:")
				print (word)
				if word == "|" or isPunct(word):
					if len(phrase) > 0:
						phrase_list.append(phrase)
						phrase = []
				else:
					phrase.append(word)
		tempPhrasesList = []
		for phrases in phrase_list:
			tempPhrases = []
			print ("phrases----",phrases)
			for phrase in phrases:
				phrase = phrase.encode("utf-8")
				print ("phrase--",phrase)
				tempPhrases.append(phrase)
			tempPhrasesList.append(tempPhrases)
		return phrase_list

	def _calculate_word_scores(self, phrase_list):
		word_freq = nltk.FreqDist()
		word_degree = nltk.FreqDist()
		for phrase in phrase_list:
			degree = len(filter(lambda x: not isNumeric(x), phrase)) - 1
			print ("length of current phrase--",degree)
			for word in phrase:
				# word = word.encode("utf-8")
				print ("word in _calculate_word_scores---",word)
				word_freq[word] += 1
				word_degree[word] +=degree
				# word_freq.inc(word)
				# word_degree.inc(word, degree) # other words
		for word in word_freq.keys():
			word_degree[word] = word_degree[word] + word_freq[word] # itself
		# word score = deg(w) / freq(w)
		word_scores = {}
		for word in word_freq.keys():
			word_scores[word] = word_degree[word] / word_freq[word]
		return word_scores

	def _calculate_phrase_scores(self, phrase_list, word_scores):
		phrase_scores = {}
		for phrase in phrase_list:
			tempPhrase = []
			phrase_score = 0
			for word in phrase:
				print ("word in phrase_score----",word)
				phrase_score += word_scores[word]
				tempPhrase.append(word)
			print ("phrase in phrase score::::", tempPhrase)
			phrase_scores[" ".join(phrase)] = phrase_score
		return phrase_scores
    
	def sentenceTokenizer(self,text):
		jp_sent_tokenizer = nltk.RegexpTokenizer(u'[^ 「」!?。．）]*[!?。]')
		sentences = jp_sent_tokenizer.tokenize (text)
		return sentences

	def extractNoun(self,sentences):
		kkma = Kkma()
		nnp_nnbList = []
		for sentence in sentences:
			posTaggedSentence = kkma.pos(sentence)
			print ("pos tagged sentence is here----")
			print (posTaggedSentence)
			for postaggedList in posTaggedSentence:
				pos = postaggedList[1]
				word = postaggedList[0]
				print (word,"----noun k lie--",pos)
				if "NNP" in pos or \
				"NNB" in pos:

					
					word = word.encode("utf-8")
					print ("Noun----",word)
					nnp_nnbList.append(word)
		return nnp_nnbList

	def extract(self, text, incl_scores=False):
		print ("in extract--",text)
		sentences = self.sentenceTokenizer(text)
		# jp_sent_tokenizer = nltk.RegexpTokenizer(u'[^ 「」!?。．）]*[!?。]')
		# sentences = jp_sent_tokenizer.tokenize (text)
		# sentences = jTokenize(text)
		# print ("sentence tokenize--")
		# print sentences
		# print len(sentences)
		for w in sentences:
			print ("a sentece---")
			print (w)
			words = self.testTokens(w)
			for word in words:
				print ("word is---")
				print (word)
			
		phrase_list = self._generate_candidate_keywords(sentences)
		# phraseListinJapanese = self.testTokens(phrase_list)
		# tempPhrase = ""
		# for p in phrase_list:
		# 	print "inside phrase list"
		# 	# element = self.testTokens(p)
		# 	tempPhrase = tempPhrase+p
		# 	# print ("element--",element)
		# phrases = self.testTokens(tempPhrase)	
		# for test in phrases:
		# 	print "test"
		# 	print test
		print ("phrase list--",phrase_list)
		word_scores = self._calculate_word_scores(phrase_list)
		print ("word score--",word_scores)
		phrase_scores = self._calculate_phrase_scores(
		  phrase_list, word_scores)
		print ("phrase score--",phrase_scores)
		sorted_phrase_scores = sorted(phrase_scores.iteritems(),
		  key=operator.itemgetter(1), reverse=True)
		print ("sorted phrase score--",sorted_phrase_scores)
		n_phrases = len(sorted_phrase_scores)
		print ("n phrase--",n_phrases)
		if incl_scores:
			return sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]
		else:
			return map(lambda x: x[0],
		    sorted_phrase_scores[0:int(n_phrases/self.top_fraction)])

	def testTokens(self,sentence):
		_unicode_chr_splitter = _Re( '(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)' ).split
		return [ chr for chr in _unicode_chr_splitter( sentence ) if chr ]

def finalJapaneseKeyword(text):
	i = isPunct("?")
	# print i
	rake = RakeKeywordExtractor()
	# keywords = rake.extract(unicodedata.normalize('NFKD', "地震保険を扱う２９社の支払額を合算した。支払件数は約７万６５００件で、加入者からの申請件数全体の４割ほどの支払いが完了した。最終的な支払額は２千億～３千億円にのぼる見通し。県別では熊本が約６万６５００件（１１６３億円）と最多で、大分が約４６００件（３８億円）、福岡が約４３００件（２７億円）と続いた。").encode('ascii','ignore'), incl_scores=True)
	keywords = rake.extract(text \
	  , incl_scores=True)
	print ("keywordssssss-----------")
	print (keywords)
	print ("tuple to list")
	keywordsList = list(keywords)
	sentences = rake.sentenceTokenizer(text)
	nounlist = rake.extractNoun(sentences)

	count = 0;
	finalKeywords = []
	for keywordWithRank in keywordsList:
		keyword = keywordWithRank[0]
		rank = keywordWithRank[1]
		
		# keyword,rank = keyword.split(',')
		keyword = keyword.encode("utf-8")
		print ("keyword--",keyword,"-------",rank)
		print ("total no of sentences--",len(sentences))
		if keyword in nounlist:
			finalKeywords.append(keyword)
			count +=1
		else:
			if len(sentences)<3 and count<2:
				finalKeywords.append(keyword)
				count +=1
			elif 3<len(sentences) and count<5:
				finalKeywords.append(keyword)
				count +=1
	print ("final more relevent keywords---------")
	for finalKeyword in finalKeywords:
		print (finalKeyword)
	return finalKeywords
		
if __name__ == "__main__":
	text = u"同紙はまた、「過去の米大統領は広島訪問を、原爆投下への謝罪と見なされる恐れがあることから避けてきた」とした上で、「オバマ氏は謝罪ではなく、日米同盟と現代の核兵器の危険性への警告に焦点を当てた」と解説した"
	keyword = finalJapaneseKeyword(text)
	for w in keyword:
		print ("final----",w)

