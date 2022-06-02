from DataBase.models import *


def scatter_with_hover(research,path,fig=None, cols=None, name=None, marker='circle',
                       fig_width=1750, fig_height=900 ):
    
    
    # bokeh for interactive display
    from bokeh.palettes import d3

    from bokeh.plotting import figure, ColumnDataSource
    from bokeh.models import HoverTool, CategoricalColorMapper
    from bokeh.models.callbacks import CustomJS
    from bokeh.io import show, output_notebook, output_file, save
    from bokeh.transform import linear_cmap
    from bokeh.models import ColumnDataSource, OpenURL, TapTool
    """
    Plots an interactive scatter plot of `x` vs `y` using bokeh, with automatic
    tooltips showing columns from `df`.
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data to be plotted
    x : str
        Name of the column to use for the x-axis values
    y : str
        Name of the column to use for the y-axis values
    fig : bokeh.plotting.Figure, optional
        Figure on which to plot (if not given then a new figure will be created)
    cols : list of str
        Columns to show in the hover tooltip (default is to show all)
    name : str
        Bokeh series name to give to the scattered data
    marker : str
        Name of marker to use for scatter plot
    **kwargs
        Any further arguments to be passed to fig.scatter
    Returns
    -------
    bokeh.plotting.Figure
        Figure (the same as given, or the newly created figure)
    Example
    -------
    fig = scatter_with_hover(df, 'A', 'B')
    show(fig)
    fig = scatter_with_hover(df, 'A', 'B', cols=['C', 'D', 'E'], marker='x', color='red')
    show(fig)
    Author
    ------
    Robin Wilson <robin@rtwilson.com>
    with thanks to Max Albert for original code example
    """

    # If we haven't been given a Figure obj then create it with default
    # size etc.
    if fig is None:
        fig = figure(width=fig_width, height=fig_height, tools=['box_zoom', 'reset', 'save', 'tap'])

    df = dict()
    df["x"]=[]
    df["y"]=[]
    df["title"]=[]
    df["abstract"]=[]
    df["topic"] = []

    clusters_point = Cluster.objects.filter(research=research)
    for points in clusters_point:
        df['x'].append(points.pos_x)
        df['y'].append(points.pos_y)
        df['topic'].append(points.topic)
        df['title'].append(points.article.title)
        df['abstract'].append(points.article.abstract)

    unique_topic = list(set(df['topic']))
    palette = d3['Category10'][len(unique_topic)]
    color_map = CategoricalColorMapper(factors=unique_topic,palette=palette)
    # We're getting data from the given dataframe
    source = ColumnDataSource(data=df)

    # We need a name so that we can restrict hover tools to just this
    # particular 'series' on the plot. You can specify it (in case it
    # needs to be something specific for other reasons), otherwise
    # we just use 'main'
    if name is None:
        name = 'main'

    # Actually do the scatter plot - the easy bit
    # (other keyword arguments will be passed to this function)
    fig.scatter('x','y', source=source, name=name, marker=marker, color={'field': 'topic', 'transform': color_map},
          legend='topic') 

    # Now we create the hover tool, and make sure it is only active with
    # the series we plotted in the previous line
    hover = HoverTool(names=[name])

    if cols is None:
        # Display *all* columns in the tooltips
        hover.tooltips = [(c, '@' + c) for c in df.keys()]
    else:
        # Display just the given columns in the tooltips
        hover.tooltips = [(c, '@' + c) for c in cols]

    #hover.tooltips.append(('index', '$index'))

    # Finally add/enable the tool
    fig.add_tools(hover)

    save(fig,path)