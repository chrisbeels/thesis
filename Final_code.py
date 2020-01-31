

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 13:10:43 2019

@author: christiaanbeels
"""
import requests
import pandas as pd


# =============================================================================
# Method with functions
# =============================================================================

doi_list = ['10.1038/srep16053']
doi_list = ['10.1038/cddiscovery.2016.25', '10.1038/srep16053']
doi_df = pd.DataFrame(doi_list, columns = ['doi'])

papers = pd.read_csv('4-DOIs.csv')
paper_dois = papers.dropna(subset=['doi'])
doi_list = paper_dois['doi']
doi_df = pd.DataFrame(doi_list, columns = ['doi'])


def make_connection (doi):
    url = 'https://api.crossref.org/works/%s' %doi
    return requests.get(url)
    
def check_status (cit_data):
    global count_status_200
    global count_status_404
    #return cit_data.status_code
    if cit_data.status_code == 200:
        count_status_200 += 1
        return cit_data.json()
    else:
        count_status_404 += 1

def extract_ref (data_checked):
    global papers_missing_citations
    if 'reference' in data_checked['message']:
        all_info = data_checked['message']['reference']
        df_info = pd.DataFrame(all_info)
        return df_info
    else:
        papers_missing_citations += 1

def extract_doi(doi, refs):
    global references_with_doi
    global references_with_no_doi
    if 'DOI' in refs:
        references_with_doi += 1
        all_dois = pd.DataFrame(refs['DOI'].dropna())
        all_dois.insert(1, 'citing_paper', doi)
        return all_dois
    else:
        references_with_no_doi += 1


############RESET##############
count_status_200 = 0
count_status_404 = 0
references_with_no_doi = 0
references_with_doi = 0
papers_missing_citations = 0   
edges = pd.DataFrame()
###############################

def execute(doi):
    global edges
    cit_data = make_connection(doi)
    data_checked = check_status(cit_data)
    if data_checked != None:
        refs = pd.DataFrame(extract_ref(data_checked))
        dois = pd.DataFrame(extract_doi(doi, refs))
        edges = pd.concat([edges, dois])
 
result = [execute(doi) for doi in doi_df]
    
       
execute(doi_df)
    
succesful_concats = edges['citing_paper'].nunique()
nodes_coda = pd.DataFrame(edges['citing_paper'].unique())
cited_nodes = pd.DataFrame(edges['DOI'].unique())    

# =============================================================================
# Extract all info from 14195 dois in the graph -cited_nodes-
# =============================================================================
info = pd.DataFrame(columns = ['DOI', 'Title', 'Publisher'])
papers_missing_info = 0


def wanted_info(checked_info, doi):
    global info
    global papers_missing_info
    df_wanted = pd.DataFrame()
    
    if 'title' and 'publisher' in checked_info['message']:
        title = checked_info['message']['title']
        publisher = checked_info['message']['publisher']
        return df_wanted.append({'DOI': doi , 'Title': title, 'Publisher': publisher}, ignore_index=True)

    else:
        papers_missing_info += 1



def ext_info(doi):
    global info
    connect_info = make_connection(doi)
    checked_info = check_status(connect_info)
    if checked_info != None:
        info = pd.concat([info,wanted_info(checked_info, doi)], sort = True)
       

    
[ext_info(doi) for doi in cited_nodes[0]]
info.to_csv (r'/Users/christiaanbeels/OneDrive/Vu/2019-2020 (IMM)/Bachelor Project/Python/info_nodes.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path
info['Title'].nunique()    
unique_nodes = info.drop_duplicates(subset='DOI', keep = 'first')
unique_nodes.to_csv (r'/Users/christiaanbeels/OneDrive/Vu/2019-2020 (IMM)/Bachelor Project/Python/unique_nodes.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path
