
import pandas as pd
import re
from sklearn import feature_extraction, metrics
import io



class strings_matcher():
    
    def __init__(self, dtf_lookup, dtf_match):
        self.dtf_lookup = dtf_lookup
        self.dtf_match = dtf_match
    
    
    @staticmethod
    def strings_similarity(a, b):
        a = re.sub(r'[^\w\s]', '', str(a).lower().strip())
        b = re.sub(r'[^\w\s]', '', str(b).lower().strip())
        lst_txt = [a, b]
        vectorizer = feature_extraction.text.CountVectorizer(lst_txt)
        matrix = vectorizer.fit_transform(lst_txt).toarray()
        lst_vectors = [vec for vec in matrix]
        cosine_matrix = metrics.pairwise.cosine_similarity(lst_vectors)
        cosine_sim_diag = cosine_matrix[0,1]
        return cosine_sim_diag
    
    
    def match_strings(self, stringa, lst_strings, threshold=0.7, top=1):
        ## compute similarity
        dtf_matches = pd.DataFrame([{"lookup":stringa, "match":str_match,
                                     "similarity": self.strings_similarity(stringa, str_match)}
                                     for str_match in lst_strings])
        ## put in a dtf
        dtf_matches = dtf_matches[ dtf_matches["similarity"]>=threshold ]
        dtf_matches = dtf_matches[["lookup", "match", "similarity"]].sort_values("similarity", ascending=False)
        if top is not None:
            dtf_matches = dtf_matches.iloc[0:top,:]
        if len(dtf_matches) == 0:
            dtf_matches = pd.DataFrame([[stringa,"None",0]], columns=['lookup','match',"similarity"])
        return dtf_matches
    
    
    def vlookup(self, threshold=0.7, top=1):
        ## process data
        lst_lookup = list(set( self.dtf_lookup.iloc[:,0].tolist() ))
        lst_match = list(set( self.dtf_match.iloc[:,0].tolist() ))
        
        ## match strings
        dtf_matches = pd.DataFrame(columns=['lookup', 'match', "similarity"])
        for string in lst_lookup:
            dtf_match = self.match_strings(string, lst_match, threshold=threshold, top=top)
            dtf_matches = dtf_matches.append(dtf_match)
        dtf_matches = dtf_matches.reset_index()
        dtf_matches = dtf_matches.drop("index", axis=1)
        return dtf_matches
    
    
    @staticmethod
    def write_excel(dtf):
        bytes_file = io.BytesIO()
        excel_writer = pd.ExcelWriter(bytes_file)
        dtf.to_excel(excel_writer, sheet_name='Sheet1', na_rep='', index=False)
        excel_writer.save()
        bytes_file.seek(0)
        return bytes_file
    