
def create_plot(damage, dash_date_range_filter, dash_category_filter):
    import plotly
    import plotly.graph_objs as go
    from sqlite3 import connect
    import pandas as pd
    import json
    from datetime import datetime, timedelta

    data = pd.DataFrame(damage, columns = ['id'
    , 'date'
    , 'platform'
    , 'description'
    , 'category'
    , 'damage'
    , 'date_short'])
    data.date = pd.to_datetime(data['date'])

    # Get date parameter
    date_param = (datetime.now() + timedelta(days=-1*dash_date_range_filter)).strftime("%Y-%m-%d")
    print(date_param)

    # Update data with new parameters 
    if dash_category_filter == "all":
        data = data[ (data.date >= date_param)]
    else:
        data = data[ (data.date >= date_param) & (data.category == dash_category_filter) ]

    category_data = data.groupby(['category'], as_index=False).sum().sort_values(by=['damage'], ascending=True)
    category_data_points =[
        go.Bar(
            y=category_data.category,
            x=category_data.damage,
            name='Total Damage',
            orientation='h',
            
        )
    ]



    graphJSON_cat = json.dumps(category_data_points, cls=plotly.utils.PlotlyJSONEncoder)

    date_fig = go.Figure()
    for platform in data.platform.unique():
            date_fig.add_trace(go.Scatter(
                x=data[data['platform']==platform]['date'],
                y=data[data['platform']==platform]['damage'],
                name=platform,
                hoverinfo='x+y',
                mode='lines',
            )
            )
    graphJSON_date = json.dumps(date_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON_cat, graphJSON_date, sum(data.damage)



    

    