#!/usr/bin/env python3
# If AttributeError: module 'common' has no attribute ...
# then restart kernel of notebook
# OR INCLUDE THESE IN NOTEBOOK:
#%load_ext autoreload
#%autoreload 2


def BuildItemSetList(adata_path):
    '''For GAs reddit subreddit sentences csv file format
    '''
    itemSetList = []
    with open(adata_path, 'r') as f:
        itemSetList = [line.split(',')[1].strip().split(' ') for line in f]
    return itemSetList


def UniqueItems(itemSetList):
    return list({item:1 for lst in itemSetList for item in lst}) # dict to list

def RemoveDups(itemSetList):
    '''
    Removes duplicate items appearing in the same transaction only.
    Input example:
    itemSetList = [['eggs', 'bacon', 'soup'],
               ['eggs', 'bacon', 'apple'],
               ['soup', 'bacon', 'banana'],
               ['soup', 'bacon', 'soup']] # removes extra soup 
    '''    
    l = []
    for transaction_id,row in enumerate(itemSetList):
        trans_items = {}
        for item_id in row:
            trans_items[item_id] = 1
        l.append(list(trans_items.keys()))
    return l

itemSetList = [['eggs', 'bacon', 'soup'],
               ['eggs', 'bacon', 'apple'],
               ['soup', 'bacon', 'banana'],
               ['soup', 'bacon', 'soup']] # removes extra soup 
RemoveDups(itemSetList)


def QueryResultConcise(queryResult, args=['cons','lift']): 
    return queryResult.loc[:,args]

def QueryResultList(queryResult, return1='cons'):
    return [z for z in queryResult[return1]]

def QueryModel(adf, edf, searchList, exactMatch=True, confMin=0.000001):
    '''
    cons is the main output of interest; the recommendations. Consequents is what it means.
    ants is what you searched for. Antecedents is what it means.
    Antecedents and consequents are association rules, meaning "people who liked A, also liked B."
    The way this works is that you tell me you like A, and I will tell you B, aka the consequent.
    adf is the model dataframe containing the association rules that were discovered when mining.
    edf is the dataframe made to speed up queries; it encodes as 1 and 0 the antecedents and 
    consequents lists that were output from the frequent pattern and association rules mining.
    This is working GREAT vs old version: Way faster, way lower memory use, equally good results.
    If it splits up your antecedent's characters, please instead pass a LIST in searchList!!!!!!!!!!!!!
    searchList can take up to 3 terms to search for, in a python list.
    Using more terms in searchList will return more precise recommendations. For example
    there will be fewer people in the universe who like both nfl and hockey, and the 
    recommendations it outputs will reflect their interests better than searching on hockey only.
    exactMatch: False says basically, I search for nfl, but it's ok to return some nba,nfl as long as nfl is in the antecedents.
    True says nfl only; return no other antecedents.
    confMin: 0.1 gives typical or mainstream results. 0.000001 is quirky or niche results.
    How it works: 
        - run queries first on edf, 
        - then use .loc[queryResultRows.index] to get those rows in adf, 
        - then query adf's confmin.
    '''
    cols_0 = list(set(edf.columns)-set(searchList))
    if exactMatch:
        cols_eq_0 = edf[cols_0].eq(0).all(1) # all these columns equal 0. ie, "matches exacly" on "nfl"
    else:
        cols_eq_0 = True # ie, "contains" term "nfl" but dont care if other terms are also in the rows
    cols_eq_1 = edf[searchList].eq(1).all(1); #cols_eq_1 # all these columns equal 1, ie, "contains" term "nfl"
    equeryResultRows = edf.loc[ cols_eq_0 & cols_eq_1 ] # important to not reassign vars edf and adf! it would mess up edf that was passed in for future queries and would require reloading model from disk!
    aqueryResultRows = adf.loc[equeryResultRows.index] # the edf informs us what adf rows to search
    #aqueryResultRows = aqueryResultRows.query('confidence >= @confMin') 
    aqueryResultRows = aqueryResultRows[aqueryResultRows.confidence >= float(confMin)]
    print(aqueryResultRows.shape)
    return aqueryResultRows

# ...but i want ants to ONLY contain the listed terms.
# so match the number of commas appearing
# PERFECT
def oldQueryModel(model, searchList, confmin=1.000001):
    '''
    If it splits up your antecedent's characters, please instead pass a LIST in searchList!!!!!!!!!!!!!
    '''
    querystr = f'not cons.str.contains(",") and '
    querystr += ''.join([f'ants.str.contains("{ant}") and ' for ant in searchList])
    querystr += f'confidence >= {confmin} and '    
    querystr += f'ants.str.count(",")<{len(searchList)}'
    #print(querystr)
    x = model.query(querystr, engine='python') 
    return x

def Append_Frozen_Str(adf,oldcolname,newcolname):
    ''' Transform frozenset to list of string. So, input fznstr and append lists of str actually lol
    '''
    adf[newcolname] = adf[oldcolname].apply(lambda x: ','.join(list(x))).astype("unicode")
    return adf

def TransformDataFPGrowthToPycaretRemoveDups(itemSetList):
    '''
    Removes duplicate items appearing in the same transaction only.
    Transforms format of list of lists as shown in demo for lib fpgrowth_py,
    into pd.dataframe as shown in demo for lib pycaret.arules.
    String value becomes item_id. Implicit row# (list#)  is transaction_id.
    Input example:
    itemSetList = [['eggs', 'bacon', 'soup'],
                    ['eggs', 'bacon', 'apple'],
                    ['soup', 'bacon', 'banana']]
    '''
    import pandas as pd
    l = []
    for transaction_id,row in enumerate(itemSetList):
        trans_items = {}
        for item_id in row:
            trans_items[item_id] = 1
        for item_id in trans_items.keys():
            l.append([item_id, transaction_id])
    return pd.DataFrame(l, columns=['item_id', 'transaction_id'])     
'''
itemSetList = [['eggs', 'bacon', 'soup'],
               ['eggs', 'bacon', 'apple'],
               ['soup', 'bacon', 'banana'],
               ['soup', 'bacon', 'soup']] # removes extra soup 
TransformDataFPGrowthToPycaretRemoveDups(itemSetList)
'''

def TransformDataFPGrowthToPycaret(itemSetList):
    '''
    Transforms format of list of lists as shown in demo for lib fpgrowth_py,
    into pd.dataframe as shown in demo for lib pycaret.arules.
    String value becomes item_id. Implicit row# (list#)  is transaction_id.
    Input example:
    itemSetList = [['eggs', 'bacon', 'soup'],
                    ['eggs', 'bacon', 'apple'],
                    ['soup', 'bacon', 'banana']]
    '''
    import pandas as pd
    l = []
    for transaction_id,row in enumerate(itemSetList):
        for item_id in row:
            l.append([item_id, transaction_id])
    return pd.DataFrame(l, columns=['item_id', 'transaction_id'])            

def EncodeTransactions_mlxtend(itemSetList):
    from mlxtend.preprocessing import TransactionEncoder   
    import pandas as pd
    te = TransactionEncoder() 
    # For small datasets:
    #te_ary = te.fit(itemSetList).transform(itemSetList)
    #df = pd.DataFrame(te_ary, columns=te.columns_)
    #For big datasets:
    fitted = te.fit(itemSetList)
    te_ary = fitted.transform(itemSetList, sparse=True) # seemed to work good
    df = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_) # seemed to work good
    return df    

def BuildRedditModel_mlxtend(data_path, metric='lift', threshold=1.000001, returnListOnly=False, min_support=0.001):
    '''For mlxtend lib. uses fpgrowth algo here, for speed.
    min_support=0.001 is safe, but min_support=0.0001 has caused 48+hours run and full swap usage! Caution!
    '''
    from mlxtend.frequent_patterns import fpgrowth, association_rules
    print(f"In the new model being trained, the min_support={min_support} Interrupt the kernel NOW if it's wrong value!!!")
    print(f"Loading dataset {data_path}...")
    itemSetList = BuildItemSetList(data_path)
    print(f"Length:{len(itemSetList)}")
    if returnListOnly:
        return itemSetList
    print("Encoding transactions...")
    itemSetList = RemoveDups(itemSetList)# Need to preprocess to remove unhelpful duplicate subreddits from transactions
    df = EncodeTransactions_mlxtend(itemSetList)
    print("Mining for frequent patterns using fpgrowth algorithm...")
    frequentItemSets = fpgrowth(df, min_support=min_support, use_colnames=True) 
    print("Mining for association rules...")
    model = association_rules(frequentItemSets, metric=metric, min_threshold=threshold)
    model = model.sort_values(metric, ascending=False)    
    #model = Append_Frozen_Str(model,'antecedents','ants')
    #model = Append_Frozen_Str(model,'consequents','cons')    
    return model

    
# Making mods to my fns is too slow when fns are in common.py due to mandatory restart of kernel needed which slows me down much.
# For saving a model df, I want to pass in float_format=x and columns=x which merely get passed along to df.to_csv()
# CONSTRASTINGLY for saving training data csv (not a model df) I want to not pass them in.
def writeCSVFiles(filenames, dfs, simulate=False, useFeather=False, **kwargsTowritecsv):
    ''' Write to disk the raw (not prepreprocessed yet) training, dev, testing (split) CSV files.
    columns=None means all -- thanks, pandas!
    '''
    from pathlib import Path
    import pandas as pd
    cnt = 0
    if simulate:
        for (f,d) in zip(filenames,dfs):
            print(f"f={f} d.shape={d.shape}")
    else:
        for (f,d) in zip(filenames,dfs): # zip iter cannot reset (reuse)                       
            if not Path(f).exists():
                print(f"Writing {f}")
                d.to_csv(f,index=False, **kwargsTowritecsv) # #kwargsTowritecsv like columns=columns, float_format="%.6f", compression='bz2'
                cnt+=1
            else:
                print(f"Not writing {f}")
    print(f"Wrote {cnt} files. {len(filenames)-cnt} files already exist. Delete files to create new files if wanted.")

def loadCSVFiles(filenames, **kwargsToreadcsv):  
    ''' Read from disk some split (train,dev,test) CSV files (raw or preprocessed). Returns list of pandas dataframe
        Use kwargsToreadcsv to set delimiter etc options to pd.read_csv()
    '''
    from pathlib import Path
    import pandas as pd
    cnt = 0
    dataframes = []
    for f in filenames:
        if Path(f).exists():
            dataframes.append(pd.read_csv(f, **kwargsToreadcsv)) 
            cnt += 1
        else:
            print(f"File not found: {f}")
    print(f"Loaded {cnt} files: {' '.join(filenames)}")
    return dataframes

def RMSE_pdstyle(a_model, a_df):
    from pycaret.regression import predict_model
    preds = predict_model(a_model, data=a_df)
    return RMSE_pdstyle_preds(preds)

def RMSE_pdstyle_preds(preds):    
    preds['SqrError'] = preds.apply(lambda row: (row['Label'] - row['target'])**2, axis=1)
    return math.sqrt(preds['SqrError'].mean())    
