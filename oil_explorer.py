import streamlit as st, pandas as pd, numpy as np, plotly.express as px
import streamlit.components.v1 as components
# from pivottablejs import pivot_ui

st.set_page_config(layout="wide")

# st.image('renewell.jpg')

#set title
st.title ('U.S. Well Analytics')

file='Field_Data.csv'

#cache the data to eliminate annoying repetitive loading
@st.cache
def load_field_data():
    df_fields=pd.read_csv(file)
    df_fields['Water Cut, %']=df_fields['Water Cut, %'].fillna(0)
    df_fields['Daily Liquid Rate, bpd']=df_fields['Daily Liquid Rate, bpd'].fillna(0)
    df_fields['Daily Gas Rate, Mscfpd']=df_fields['Daily Gas Rate, Mscfpd'].fillna(0)
    df_fields['GOR, Mscf/BO']=df_fields['GOR, Mscf/BO'].fillna(0)
    df_fields['EOR_Technology']=df_fields['EOR_Technology'].fillna('NA')
    df_fields['EOR_Technology_flag']=df_fields['EOR_Technology'].map(lambda x: 5 if x!='NA' else 0)
    return df_fields

@st.cache()
def load_well_data():
    df_wells=pd.read_parquet('All_IOR_Field_Wells.parquet')
    return df_wells

#load in data
df_fields = load_field_data()
df_wells = load_well_data()

cols=df_fields.columns.unique()

#set up columns
col1,col2,col3=st.columns(3)
with col1:
    #user defined map settings
    map_style=st.radio('Choose Map Style',['Satellite','Topographic'])
with col2:
    # set up color scale based choice for nicer maps
    colorby=st.selectbox('Choose Map Color By Property',['Status','Type','INJ Type','EOR_Technology'])

if colorby=='Status':
    color_discrete_map = {'Active': 'rgb(0,255,0)', 'Shut-in': 'rgb(0,0,0)', 'End of Life': 'rgb(255,0,0)'}
elif colorby=='Type':
    color_discrete_map={'Oil':'rgb(0,255,0)','Gas':'rgb(255,0,0)','Shut-in':'rgb(0,0,0)'}
elif colorby=='INJ Type':
    color_discrete_map={'WATER':'rgb(0,0,255)','GAS':'rgb(255,0,0)','UNKNOWN':'rgb(50,50,50)'}
elif colorby=='EOR_Technology':
    color_discrete_map={'WATER':'rgb(0,0,255)','GAS':'rgb(255,0,0)','UNKNOWN':'rgb(50,50,50)'}
else:
    color_discrete_map={}
    

if colorby=='EOR_Technology':
    sizeby='EOR_Technology_flag'
    size_max=8
else:
    with col3:
        sizeby=st.selectbox('Choose the Size by Property',['Number Non-PA Wells','Daily Liquid Rate, bpd','Daily Gas Rate, Mscfpd','Water Cut, %','GOR, Mscf/BO',None])
    if sizeby==None:
        if colorby=='EOR_Technology':
            sizeby='EOR_Technology_flag'
            size_max=8
        else:
            sizeby=[5 for x in df_fields.index]
            size_max=5
    if sizeby=='Water Cut, %':
        avg_sizeby=df_fields[df_fields[sizeby]>0][sizeby].mean()
        sizeby=[35 if x<35 else x for x in df_fields[sizeby] ]
        size_max=15
    else:
        avg_sizeby=df_fields[df_fields[sizeby]>0][sizeby].mean()
        sizeby=[avg_sizeby if x<avg_sizeby else x for x in df_fields[sizeby] ]
        size_max=40
# st.text(avg_sizeby)
fig = px.scatter_mapbox(df_fields, lat='Lat', lon='Lon', size=sizeby, size_max=size_max, height=600,color=colorby,hover_data=cols,color_discrete_map=color_discrete_map,zoom=3)
if map_style == 'Topographic':
    fig.update_layout(mapbox_style="open-street-map")
else:
    fig.update_layout(mapbox_style="white-bg",mapbox_layers=[{"below": 'traces',"sourcetype": "raster","sourceattribution": "United States Geological Survey",
    "source": ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]}])

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

##*************************************** individual field section **********************************************
st.header('Search Individual Fields')

fields=sorted(df_fields['Field Name'].unique().tolist())
field=st.selectbox('Select a Field to View',fields,index=360)
df_field_temp=df_fields[df_fields['Field Name']==field]
df_wells_temp=df_wells[df_wells['Field']==field]
well_cols=df_wells_temp.columns.tolist()
# st.table(fields)
df_field_temp[['Field Name','Number Non-PA Wells','Water Cut, %','GOR, Mscf/BO','Daily Liquid Rate, bpd','Daily Gas Rate, Mscfpd','Type','Status','EOR_Technology','INJ Types (All)']]

#make maps
fig_field = px.scatter_mapbox(df_field_temp, lat='Lat', lon='Lon', size=[30],size_max=30, height=600,color=[field],color_discrete_map={field:'rgb(0,0,0)'},hover_data=cols,zoom=11)
fig_field2=px.scatter_mapbox(df_wells_temp,lat='Surface Latitude (WGS84)',lon='Surface Longitude (WGS84)',size=[10 for x in df_wells_temp.index],size_max=10,hover_data=well_cols,color='Operator Company Name',zoom=11,height=600)

if map_style == 'Topographic':
    fig_field2.update_layout(mapbox_style="open-street-map")
else:
    fig_field2.update_layout(mapbox_style="white-bg",mapbox_layers=[{"below": 'traces',"sourcetype": "raster","sourceattribution": "United States Geological Survey",
    "source": ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]}])

fig_field2.add_trace(fig_field.data[0])
fig_field2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_field2, use_container_width=True)


# st.header('Field Data Pivot Table')
# # pivot table
# t = pivot_ui(df_fields)
# with open(t.src) as t:
#     components.html(t.read(), width=900, height=1000, scrolling=True)




