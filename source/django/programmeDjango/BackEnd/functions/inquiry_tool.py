def inquiry_tool(rel_df, question, list_of_search_words, cluster, boolean_and=False):
    
    import functools
    import pandas as pd
    from IPython.core.display import HTML
    
    list_of_search_words = [word.lower() for word in list_of_search_words]
    rel_df = rel_df[rel_df['cluster']==cluster].copy()
    rel_df['Query'] = rel_df['Title'].str.lower() + rel_df['Abstract'].str.lower() + rel_df['Authors'].str.lower() + rel_df['DOI'].str.lower() + rel_df['Full_text'].str.lower() + rel_df['Date']
    
    if boolean_and == False:
        rel_df = rel_df[functools.reduce(lambda a,b : a|b, (rel_df['Query'].str.contains(s) for s in list_of_search_words))]
        boolean = 'OR'
    else:
        rel_df = rel_df[functools.reduce(lambda a,b : a&b, (rel_df['Query'].str.contains(s) for s in list_of_search_words))]
        boolean = 'AND'
        
    rel_df_index = rel_df.index

    rel_df['score'] = ''
    for index, row in rel_df.iterrows():
        result = row['Query'].split()
        score = 0
        for word in list_of_search_words:
            score += result.count(word)
        rel_df.loc[index,'score'] = score * (score/len(result))
    rel_df = rel_df.sort_values(by = ['score'], ascending = False).reset_index(drop=True)

    df_table = pd.DataFrame(columns = ['Date', 'Authors', 'Title', 'Excerpt', 'Abstract'])
    df_inquiry = pd.DataFrame(columns = ['Date', 'Authors', 'Title', 'Abstract', 'labels', 'cluster', 'Journal', 'URL'])
    
    for index, row in rel_df.iterrows():
        pub_sentence = ''
        sentences = row['Query'].split('. ')
        for sentence in sentences:
            missing = 0
            for word in list_of_search_words:
                if word not in sentence:
                    missing = 1
            if missing == 0 and len(sentence) < 1000 and sentence != '':
                if sentence[len(sentence)-1] != '.':
                    sentence += '.'
                pub_sentence += '<br><br>'+sentence.capitalize()

        df_table.loc[index] = [row['Date'],
                               row['Authors'].split(', ')[0] + ' et al.',
                               '<p align="left"><a href="{}">{}</a></p>'.format('https://doi.org/' + row['DOI'], row['Title']),
                               '<p fontsize=tiny" align="left">' + pub_sentence + '</p>',
                               row['Abstract']]
        
        df_inquiry.loc[index] = [row['Date'],
                                 row['Authors'],
                                 '<p align="left"><a href="{}">{}</a></p>'.format('https://doi.org/' + row['DOI'], row['Title']),
                                 row['Abstract'],
                                 row['labels'],
                                 row['cluster'],
                                 row['Journal'],
                                 row['URL']]

    display(HTML('<h3>'  + question + ' : Cluster ' + str(cluster) + ': ' + ' ,'.join(rel_df['labels'].unique()) + '</h3>'))
    
    count = df_table.shape[0]
    
    if count < 1:
        print('No article fitting the criteria could be found.')
    else:
        print('Number of articles retrieved from cluster ' + str(cluster) + ': ' + str(count))
        display(HTML(df_table.to_html(escape=False, index=False)))
        
    return df_inquiry, count, boolean, rel_df_index, rel_df