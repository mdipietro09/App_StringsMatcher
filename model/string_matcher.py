
import pandas as pd
import numpy as np
from sklearn import feature_extraction, metrics
import io
from tqdm import tqdm



class StringMatcher():
    
    def __init__(self, dtf_left, dtf_right):
        self.dtf_left = dtf_left
        self.dtf_right = dtf_right
    
    
    @staticmethod
    def utils_string_matching(a, lst_b, threshold=None, top=None):
        ## vectorizer ("my house" --> ["my", "hi", "house", "sky"] --> [1, 0, 1, 0])
        vectorizer = feature_extraction.text.CountVectorizer()
        X = vectorizer.fit_transform([a]+lst_b).toarray()

        ## cosine similarity (scores a vs lst_b)
        lst_vectors = [vec for vec in X]
        cosine_sim = metrics.pairwise.cosine_similarity(lst_vectors)
        scores = cosine_sim[0][1:]

        ## match
        match_scores = scores if threshold is None else scores[scores >= threshold]
        match_idxs = range(len(match_scores)) if threshold is None else [i for i in np.where(scores >= threshold)[0]] 
        match_strings = [lst_b[i] for i in match_idxs]

        ## dtf
        dtf_match = pd.DataFrame(match_scores, columns=[a], index=match_strings)
        dtf_match = dtf_match[~dtf_match.index.duplicated(keep='first')].sort_values(a, ascending=False).head(top)
        return dtf_match
    
    
    def vlookup(self, threshold=0.7, top=1):
        ## process data
        lst_left = list(set( self.dtf_left.iloc[:,0].tolist() ))
        lst_right = list(set( self.dtf_right.iloc[:,0].tolist() ))
        
        ## match strings
        dtf_matches = pd.DataFrame(columns=['string','match','similarity'])
        for string in tqdm(lst_left):
            dtf_match = self.utils_string_matching(string, lst_right, threshold, top)
            dtf_match = dtf_match.reset_index().rename(columns={'index':'match', string:'similarity'})
            dtf_match["string"] = string
            dtf_matches = dtf_matches.append(dtf_match, ignore_index=True, sort=False)
        return dtf_matches[['string','match','similarity']]
    
    
    @staticmethod
    def write_excel(dtf):
        bytes_file = io.BytesIO()
        excel_writer = pd.ExcelWriter(bytes_file)
        dtf.to_excel(excel_writer, sheet_name='Sheet1', na_rep='', index=False)
        excel_writer.save()
        bytes_file.seek(0)
        return bytes_file
    