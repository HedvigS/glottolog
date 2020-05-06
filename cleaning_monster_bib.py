#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 23:13:49 2020

@author: hedvigskirgard
"""
import os
import csv
from pyglottolog import Glottolog
from tqdm import tqdm

API = Glottolog('.')

def get_bibfiles(filepath = "references/bibtex/"):
    """This is a function that reads in a list of bibtex files"""
    fn = os.listdir(filepath)
    return fn

def write_csv_line(entry):
    out_list = []
    out_list.append(entry.year_int)
    out_list.append(entry.pages_int)
#    out_list.append(entry.lgcodes)

    if "title" in entry.fields:
        out_list.append(entry.fields['title'])
    else: out_list.append("NA")
    
    if "hhtype" in entry.fields:
        out_list.append(entry.fields['hhtype'])
    else: out_list.append("NA")


    if "author" in entry.fields:
        out_list.append(entry.fields['author'])
    else: out_list.append("NA")

    if "inlg" in entry.fields:
        out_list.append(entry.fields['inlg'])
    else: out_list.append("NA")

    if "lgcode" in entry.fields:
        out_list.append(entry.fields['lgcode'])
    else: out_list.append("NA")

    return out_list

def main():
#    full_list = []
    fns = get_bibfiles()
    
    with open("monster_df.csv", "w", newline = "") as f:
        wr = csv.writer(f, quoting = csv.QUOTE_ALL)
        wr.writerow(["year_int", "pages_int", "title", "hhtype", "author", "inlg", "lgcode"])
        for i in fns:
            for entry in tqdm(API.bibfiles[i].iterentries()):
                wr.writerow(write_csv_line(entry))
