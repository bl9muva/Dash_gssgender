import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


gss = pd.read_csv("https://github.com/bl9muva/Dash_gssgender/blob/main/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

##Markdown text
markdowntext='''
[Gender wage gap](https://en.wikipedia.org/wiki/Gender_pay_gap) is the difference between average wages of working men and women. Historically, men earn more than women. It is likely that this difference can be attributed to various reasons, for example, it may be due to the different types of jobs men and women used to have, different hours they work, different educational backgrounds. In order to characterize the true difference between two groups, it is imperative to use adjusted wage differences.

[The General Social Survey](http://www.gss.norc.org/About-The-GSS) is curated by [the NORC (the non-partisan and objective research organization at the University of Chicago)](https://www.norc.org/Pages/default.aspx). This survey data provides social scientists a comprehensive and contemporary statistical view into many aspects of American society.
'''

##Table
gss_table=gss_clean.groupby('sex').mean().round(2)[['income','job_prestige','socioeconomic_index','education']]
gss_table.columns=['Avg_income','Avg_job_prestige','Avg_socioecono','Avg_years_educ']
gss_table=gss_table.reset_index()
table=ff.create_table(gss_table)

##barplot
gss_bar=gss_clean.groupby(['male_breadwinner','sex']).size().\
            reindex(["strongly agree", "agree", "disagree", "strongly disagree"], level=0).\
            reset_index().rename({'male_breadwinner':'survey_male_bread',0:'count'},axis=1)

fig_bar=px.bar(gss_bar, x='survey_male_bread',y='count',color='sex',
               color_discrete_map = {'male':'blue', 'female':'red'},
               labels={'survey_male_bread':'survey choice to men_as_breadwinner'},
               barmode='group')

##scatter plot
fig_scatter=px.scatter(gss_clean, x='job_prestige',y='income', color='sex',
                       trendline='ols',
                       labels={'job_prestige':'Occupational Prestige','income':'Income'},
                       hover_data=['education','socioeconomic_index'])

##boxplot
fig_box_ic=px.box(gss_clean, x='sex',y='income',color='sex',
              labels={'sex':'','income':'Income'})
fig_box_ic.update_layout(showlegend=False)

fig_box_pstg=px.box(gss_clean, x='sex',y='job_prestige',color='sex',
              labels={'sex':'','job_prestige':'Occupational Prestige'})
fig_box_pstg.update_layout(showlegend=False)

##boxplot with 6 facets
newdf=gss_clean[['income','sex','job_prestige']].dropna()
newdf['prestige_range']=pd.cut(newdf['job_prestige'],bins=6)
newdf2=newdf.sort_values('prestige_range')

fig_box6=px.box(newdf2, x='sex',y='income',color='sex', 
                color_discrete_map = {'male':'blue', 'female':'red'},
                facet_col='prestige_range', 
                facet_col_wrap=3)


##setting up for dash


surveys=['satjob', 'relationship','male_breadwinner','men_bettersuited','child_suffer','men_overwork']
groups=['sex','region','education']

gss_clean['satjob']=gss_clean['satjob'].astype('category').cat.\
        reorder_categories(['very satisfied', 'mod. satisfied', 'a little dissat', 'very dissatisfied'])
gss_clean['relationship']=gss_clean['relationship'].astype('category').cat.\
        reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean['male_breadwinner']=gss_clean['male_breadwinner'].astype('category').cat.\
        reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean['men_bettersuited']=gss_clean['men_bettersuited'].astype('category').cat.\
        reorder_categories(['agree','disagree'])
gss_clean['child_suffer']=gss_clean['child_suffer'].astype('category').cat.\
        reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])
gss_clean['men_overwork']=gss_clean['men_overwork'].astype('category').cat.\
        reorder_categories(['strongly agree', 'agree', 'neither agree nor disagree', 'disagree', 'strongly disagree'])

survey={'satjob':'Responses to "On the whole, how satisfied are you with the work you do?"',
       'relationship':'Agree or disagree with: "A working mother can establish just as warm and secure <br> \
       a relationship with her children as a mother who does not work."',
       'male_breadwinner':'Agree or disagree with: "It is much better for everyone involved if the man <br> \
       is the achiever outside the home and the woman takes care of the home and family."',
       'men_bettersuited':'Agree or disagree with: "Most men are better suited emotionally <br> \
       for politics than are most women."',
       'child_suffer':'Agree or disagree with: "A preschool child is likely to suffer <br> \
       if his or her mother works."',
       'men_overwork':'Agree or disagree with: "Family life often suffers because men <br> \
       concentrate too much on their work."',}


## Dash App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap in 2019 General Social Survey"),
        
        dcc.Markdown(children = markdowntext),
        
        html.H2("Comparing Averages between Men and Women"),
        
        dcc.Graph(figure=table),
        
        html.H2("Income vs Occupational Prestige by Gender"),
        
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            
            html.H3("Income by Gender"),
            
            dcc.Graph(figure=fig_box_ic)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H3("Occupational Prestige by Gender"),
            
            dcc.Graph(figure=fig_box_pstg)
            
        ], style = {'width':'48%', 'float':'right'}),
                
        html.H2("Income vs Gender as arranged by different levels of Occupational Prestige"),
        
        dcc.Graph(figure=fig_box6),
        
        html.H2("Survey Results"),
        
        html.Div([
            
            html.H3("x-axis feature"),
            
            dcc.Dropdown(id='x-axis',
                         options=[{'label': i, 'value': i} for i in surveys],
                         value='satjob'),
            
            html.H3("colors"),
            
            dcc.Dropdown(id='color',
                         options=[{'label': i, 'value': i} for i in groups],
                         value='sex')
        ], style={'width':'25%', 'float':'left'}),
        
        html.Div([
            
            dcc.Graph(id='graph')
            
        ], style={'width':'70%','float':'right'})
                    
    ]
)

@app.callback(Output(component_id="graph",component_property="figure"), 
                  [Input(component_id='x-axis',component_property="value"),
                   Input(component_id='color',component_property="value")])

def make_figure(x, color):
    df=gss_clean.groupby([x,color]).size().reset_index().sort_values(x)
    return px.bar(
        x=df[x],
        y=df[0],
        color=df[color],
        labels={'x':survey.get(x),'y':'Counts'},
        barmode='group'
)


if __name__ == '__main__':
    app.run_server(debug=True)




