# Outlier romeval
def outlier_removal_by_pvalue(all_data, numerical_cols, p_value = 1.1102230246251565e-16):
    prob = 1 - p_value
    z_score = stats.norm.ppf(prob)
    
    zscores_condition_respected = (np.abs(stats.zscore(all_data[numerical_cols])) < z_score).all(axis=1)
    zscores_condition_unrespected = len(zscores_condition_respected) - sum(zscores_condition_respected)
    df_zscores_boolean = (np.abs(stats.zscore(all_data[numerical_cols])) >= z_score)
    
    evidence_value = pd.DataFrame()
    for index, row in df_zscores_boolean.iterrows():
        if True in list(row):
            evidence_value[all_data.iloc[index]['name']] = np.array(row) * all_data.iloc[index][numerical_cols]
                
    evidence_value = evidence_value.T.sort_index()
    print('Outlier excluded for (p = {}):\n{}\n'.format(round(p_value,20),zscores_condition_unrespected))
    print(evidence_value)
        
    return all_data[zscores_condition_respected]


#• Time format
def check_unique_time_format(a_string):
    if (a_string[-3] == ':') & (a_string[-6] == ':'):
        res = True
    else:
        res = False
    return res


# Time conversion
def convert_time_in_seconds(a_string):
    try:
        second = int(a_string[-2:]) + int(a_string[-5:-3])*60 + int(a_string[-8:-6])*3600
    except:
        try:
            second = int(a_string)
        except:
            second = 0
    return second