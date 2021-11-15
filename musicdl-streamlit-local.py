import os
import streamlit as st
import pandas as pd
from musicdl import musicdl
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

st.set_page_config(layout='wide')
target_srcs = [
    'qq', 'lizhi', 'migu', 'fivesing', 'qianqian', 'joox', 'kugou', 'netease', 'yiting', 'kuwo', 'xiami', 'baiduFlac',
]
st.write("歌曲搜索范围选择:")
col_app = st.columns(6)
check_box_stat = []
for i in range(len(target_srcs)):
    with col_app[i % 6]:
        if target_srcs[i] in ['qq', 'lizhi', 'migu', 'fivesing']:
            c = st.checkbox(target_srcs[i], value=True, key=target_srcs[i])
        else:
            c = st.checkbox(target_srcs[i], value=False, key=target_srcs[i])
        check_box_stat.append(c)

config = {'logfilepath': 'musicdl.log', 'savedir': 'downloaded', 'search_size_per_source': 10, 'proxies': {}}
client = musicdl.musicdl(config=config)


# def make_clickable(link):
#     text = 'Download'
#     return f'<div><a href="{link}" download="true" type="audio/mpeg">{text}</a></div>'


# js = JsCode("""
# function(e) {
#     let api = e.api;
#     let rowCount = api.getSelectedNodes().length;
#     window.alert('selection changed, ' + rowCount + ' rows selected');
# };
# """)

@st.cache()
def search_music(musicname):
    if musicname:
        search_target = []
        for i in target_srcs:
            if st.session_state[i]:
                search_target.append(i)
        with st.spinner('搜索中, 请稍等片刻...'):
            search_results = client.search(musicname, search_target)
            title = ['序号', '歌手', '歌名', '大小', '时长', '类型', '专辑', '来源']
            items, records, idx = [], {}, 0
            for key, values in search_results.items():
                for value in values:
                    items.append(
                        [str(idx), value['singers'], value['songname'], value['filesize'], value['duration'],
                         value['ext'], value['album'],
                         value['source']])
                    records.update({str(idx): value})
                    idx += 1
            return items, records, title
    return None, None, None
            # df = pd.DataFrame(items, columns=title)
            # # df['来源'] = df['来源'].apply(make_clickable)
            # gb = GridOptionsBuilder.from_dataframe(df)
            # gb.configure_selection(selection_mode="multiple", use_checkbox=True)
            # gb.configure_grid_options(onSelectionChanged=js)
            # # gb.configure_pagination()
            # gridOptions = gb.build()
            # # AgGrid(df, editable=True, gridOptions=gridOptions)
            # ag = AgGrid(df,
            #               gridOptions=gridOptions,
            #               fit_columns_on_grid_load=True,
            #               # enable_enterprise_modules=True,
            #               allow_unsafe_jscode=True)
            #               # theme='streamlit',
            #               # key='myaggrid'
            #               # update_mode=GridUpdateMode.SELECTION_CHANGED)
            # st.write(ag)
            # df = df.to_html(escape=False)
            # st.write(df, unsafe_allow_html=True)
        # st.success('Done!')


music_name = st.text_input('请输入搜索关键词(歌曲名、歌手名):', value='')

items, records, title = search_music(music_name)
selected_data = []
if items is not None:
    df = pd.DataFrame(items, columns=title)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridOptions = gb.build()
    ag = AgGrid(df,
                gridOptions=gridOptions,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED)
    selected_data = ag['selected_rows']


def download_music(songinfos):
    client.download(songinfos)


need_download_numbers = []
songinfos = []
download_save_dir = 'downloaded'
if len(selected_data) > 0:
    for value in selected_data:
        need_download_numbers.append(value['序号'])
    for id in need_download_numbers:
        songinfo = records.get(id, '').copy()
        # 文件下载后保存名称为 "歌曲名 - 歌手名"
        songinfo['savename'] = songinfo['songname'] + ' - ' + songinfo['singers']
        # 文件保存路径为 downloaded/[singger]/[songname] - [ext]
        if not os.path.exists(download_save_dir):
            os.mkdir(download_save_dir)
        file_save_path = download_save_dir + '/' + songinfo['singers']
        full_path = file_save_path + '/' + songinfo['savename'] + '/' + songinfo['ext']
        if os.path.exists(full_path):
            st.write('{} exists'.format(full_path))
            pass
        else:
            songinfo['savedir'] = file_save_path
            songinfos.append(songinfo)
            download_music(songinfos)
            st.write('{} save to {}'.format(songinfo['savename'], songinfo['savedir']))


# container = st.container()
# my_button = container.button('开始搜索', key='start', on_click=search_music(music_name))
