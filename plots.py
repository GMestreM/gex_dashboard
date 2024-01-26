import numpy as np 
import pandas as pd
import plotly.graph_objs as go

def plotly_gex_strike_bars(gex_strikes, spot_price=None):
    if spot_price:
        from_strike = 0.85 * spot_price
        to_strike = 1.15 * spot_price
    
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=gex_strikes['Strikes'],
            y=gex_strikes['Gamma Exposure Calls'],
            base=0,
            marker={'color':'green'},
            name='Call exposure',
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=gex_strikes['Strikes'],
            y=gex_strikes['Gamma Exposure Puts'],
            base=0,
            marker={'color':'red'},
            name='Put exposure',
        )
    )
    
    # fig.add_trace(
    #     go.Scatter(
    #         x=[spot_price], 
    #         y=[dmin,dmax], 
    #         mode='lines', 
    #         line=dict(color='green', width=2, dash='dash'),
    #         name='2018-03-12',
    #     ),
    # )
    
    if spot_price:
        fig.add_vline(
            x=spot_price,
            line_dash="dash", 
            line_color="black",
            annotation_text='Spot price',
        )
    
    
    
    fig.update_layout(
        title='Gamma Exposure Per 1% Move',
        xaxis_range = [from_strike, to_strike],
        barmode='overlay',
        height=600,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            xanchor='center',
            y=-.25, 
            x=0.5,
        ),
        title_font_size=30,
        xaxis_title_font_size=20, 
        xaxis_tickfont_size=20, 
        hoverlabel_font_size=10, 
        legend_font_size=20,
    )
    
    return fig

def plotly_gex_profile(gex_levels, spot_price=None):
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=gex_levels['Strikes'],
            y=gex_levels['Gamma Exposure'],
            mode='lines',
            # marker={'color':'green'},
            name='Call exposure',
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=gex_levels['Strikes'],
            y=gex_levels['Gamma Exposure ExNext Expiry'],
            mode='lines',
            # marker={'color':'green'},
            name='Call exposure (excluding next expiration)',
            visible='legendonly',
        ),
    )
    
    fig.add_trace(
        go.Scatter(
            x=gex_levels['Strikes'],
            y=gex_levels['Gamma Exposure ExNext Friday'],
            mode='lines',
            # marker={'color':'green'},
            name='Call exposure (excluding next Friday)',
            visible='legendonly',
        ),
    )
    
    if spot_price:
        fig.add_vline(
            x=spot_price,
            line_dash="dash", 
            line_color="black",
            annotation_text='Spot price',
            annotation_position='bottom',
        )
        
        
    # Find Gamma Flip Point
    zero_cross_idx = np.where(np.diff(np.sign(gex_levels['Gamma Exposure'])))[0][0]

    neg_gamma = gex_levels['Gamma Exposure'][zero_cross_idx]
    pos_gamma = gex_levels['Gamma Exposure'][zero_cross_idx+1]
    neg_strike = gex_levels['Strikes'][zero_cross_idx]
    pos_strike = gex_levels['Strikes'][zero_cross_idx+1]

    zero_gamma = pos_strike - ((pos_strike - neg_strike) * pos_gamma/(pos_gamma-neg_gamma))
    # zero_gamma = zero_gamma[0]
    
    
    fig.add_vline(
        x=zero_gamma,
        line_dash="solid", 
        line_color="darkgrey",
        annotation_text='Gamma flip',
        annotation_position='top',
    )
    
    # Add background
    fig.add_vrect(
        x0=0,
        x1=zero_gamma,
        fillcolor="red",
        opacity=0.2,
        line_width=0,
    )
    fig.add_vrect(
        x0=zero_gamma,
        x1=gex_levels['Strikes'].max()*5,
        fillcolor="green",
        opacity=0.2,
        line_width=0,
    )
    
    # Add zero line
    fig.add_hline(
            y=0,
            line_color="black",
            line_width=0.5,
        )

    # fig.add_trace(
    #     go.Scatter(
    #         x=[gex_levels['Strikes'].min(), zero_gamma, zero_gamma, gex_levels['Strikes'].min()],
    #         y=[gex_levels['Gamma Exposure'].min(), gex_levels['Gamma Exposure'].min(), gex_levels['Gamma Exposure'].max(), gex_levels['Gamma Exposure'].max()],
    #         fill='tozeroy',
    #         fillcolor='green',
    #         mode='none',
    #         showlegend=False
    #     ),
    # )
    
    
    fig.update_layout(
        title=f'Gamma Exposure Profile (Gamma Flip: {zero_gamma:.1f})',
        xaxis_range = [gex_levels['Strikes'].min(), gex_levels['Strikes'].max()],
        height=600,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            xanchor='center',
            y=-.25, 
            x=0.5,
        ),
        title_font_size=30,
        xaxis_title_font_size=20, 
        xaxis_tickfont_size=20, 
        hoverlabel_font_size=10, 
        legend_font_size=20,
    )
    
    
    return fig

def plotly_candlestick_gex(ohlc, historic_gex=None):
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=ohlc.index,
            open=ohlc['Open'],
            high=ohlc['High'],
            low=ohlc['Low'],
            close=ohlc['Close'],
            # mode='lines',
            # marker={'color':'green'},
            name='SPX',
        )
    )
    
    # Add lines with historic gex
    fig.add_trace(
        go.Scatter(
            x=historic_gex.index,
            y=historic_gex['Zero Gamma'],
            mode='lines',
            marker={'color':'black'},
            name='Gamma flip',
            # visible='legendonly',
        ),
    )
    
    fig.update_layout(
        title=f'SPX Quotes',
        xaxis_range = [ohlc.index[-60], ohlc.index.max()],
        height=650,
        xaxis=dict(
            showspikes=True,
            spikecolor='rgba(0.6,0.6,0.6,0.6)',
            spikethickness=-2,
            spikemode="across",
            spikedash='solid',
        ),
        yaxis=dict(
            fixedrange=False  
        ),
        hovermode='x',
        title_font_size=30,
        xaxis_title_font_size=20, 
        xaxis_tickfont_size=20, 
        hoverlabel_font_size=10, 
        legend_font_size=20,
        # legend=dict(
        #     orientation='h',
        #     yanchor='bottom',
        #     xanchor='center',
        #     y=-.25, 
        #     x=0.5,
        # ),
    )
    
    
    return fig