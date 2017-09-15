"""
Sabastian Mugazambi
NB.py
"""

import csv
import random
import numpy as np
import heapq
import math
import collections
import time
import copy
import scipy.stats



def load(filename):
    """ Loading and parsing files into a list sets """
    with open(filename, 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\n')
        dict_factors = collections.defaultdict(list)
        keyz=[]
        first = 0;

        for row in reader:
            if first < 1:
                for key in row:
                    dict_factors[key]
                    keyz.append(key)
                first += 1
            else:
                for i in range(len(keyz)):
                    dict_factors[keyz[i]].append(row[i])

        #remove empty strings
        for key,value in dict_factors.iteritems():
                dict_factors[key] = filter(None,value)

        #convert to float
        for key,value in dict_factors.iteritems():
                dict_factors[key] = map(float,value)

        return dict_factors

def remove(dict_val, list_keys):
    #removing unwanted factors
    for key in list_keys:
        dict_val.pop(key)
    return dict_val

def get_Bins(values, credit_bins, cut_off):
    #putting the factors into bins
    for i in range(len(values)):
        if (values[i] < cut_off):
            values[i] = credit_bins[0]
        else:
            values[i]= credit_bins[1]
    return values

def bin_prob(fails,passes,stu_val):
    both_probs = []
    #calculate student probabilities given fail
    fail_counts = np.bincount(fails)
    both_probs.append(float(fail_counts[stu_val])/sum(fail_counts))
    #calculating probabilities of pass
    pass_counts = np.bincount(passes)
    both_probs.append(float(pass_counts[stu_val])/sum(pass_counts))

    return both_probs

def cont_prob(fails,passes,stu_val):
    #fails calculating probs
    both_probs = []
    fails_mean = np.mean(fails)
    fails_sd = np.std(fails)
    both_probs.append(scipy.stats.norm.pdf(stu_val, loc=fails_mean, scale=fails_sd))
    #passes calculating probs
    pass_mean = np.mean(passes)
    pass_sd = np.std(passes)
    both_probs.append(scipy.stats.norm.pdf(stu_val, loc=pass_mean, scale=pass_sd))

    return both_probs

def main():
    """ Main function and user interface of this program """
    #Loading the data into a dictionary with column name as key
    docs = load('writingportfolio.csv')
    #remove a couple of fectors which I think are useless
    key_remove = ['Minnesota','Birth Year']
    docs = remove(docs,key_remove)


    #get the true value needed and remove it from dictionary
    st_id = docs.pop('Project ID')
    true_value = map(int, docs.pop('Needs Work'))

    #Detect what is to be binned and what is not to be
    bin_keys = ['International','Abroad Credits','AP Credits','CS Credits','English Credits','Science Credits','Writing Credits']
    num_bin = len(bin_keys)

    #Detect the keys that are supposed to be cummulative
    cont_keys = ['Verbal SAT','Math SAT','Cumulative GPA','# essays in portfolios']
    num_cont = len(cont_keys)

    #puting the binning ones in bin_keys
    credit_bins = [0,1]

    #cut off points for bins are in order as in bin_keys
    #cut_offs = [1,0,33.0,12.0,10.0,15,5]
    cut_offs = [1,0,33.0,12.0,10.0,15,10]

    #creating bins for the keys with bins
    for i in range(len(bin_keys)):
        key = bin_keys[i]
        docs[key] = get_Bins(docs.get(key),credit_bins,cut_offs[i])

    #combining the keys for iteration
    all_keys = bin_keys + cont_keys
    #empty list of predicted values
    pred_values = []

    for i in range(len(st_id)):
        #Lists that will hold probabilities
        list_fail_probs = []
        list_pass_probs = []

        count = 0
        for factor_values in all_keys:

            #Leave 1 cross validation
            #Removing student in question
            vals = copy.copy(docs.get(factor_values))
            tr = copy.copy(true_value)
            stu_val = vals.pop(i)
            tr.pop(i)

            #seperate passed from not passed the passed and not passed
            vals = np.array(vals)
            tr = np.array(tr)
            failed = np.where(tr == 1)
            passed = np.where(tr == -1)

            #make the two lists and their counts
            fails = vals[failed]
            passes = vals[passed]

            #get the two main probabilities
            total_ob = len(tr)
            prob_fail = float(len(fails))/total_ob
            prob_pass = float(len(passes))/total_ob


            if (count < num_bin):
                #calculate probabilities for binned things
                p = bin_prob(fails, passes, stu_val)
                list_fail_probs.append(p[0])
                list_pass_probs.append(p[1])
                count += 1

            else:
                #calculate probabilities for cumulative
                pp = cont_prob(fails, passes, stu_val)
                list_fail_probs.append(pp[0])
                list_pass_probs.append(pp[1])
                count += 1

        fail_side =  np.prod(np.array(list_fail_probs)) * prob_fail
        pass_side =  np.prod(np.array(list_pass_probs)) * prob_pass

        #predicting for each student
        if (fail_side <= pass_side):
            pred_values.append(-1)
        else:
            pred_values.append(1)

    #calculating accuarcy
    correct = 0
    for i in range(len(pred_values)):
        if (pred_values[i] == true_value[i]):
            correct += 1
    accuracy = float(correct)/len(pred_values)

    print "The accuracy is", accuracy


if __name__ == "__main__":
    main()
