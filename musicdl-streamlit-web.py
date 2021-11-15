import os
import pathlib
import streamlit as st
import pandas as pd
from musicdl import musicdl
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode


st.set_page_config(layout='wide')

target_srcs = [
    'qq', 'migu', 'qianqian', 'joox', 'kugou', 'netease', 'yiting', 'kuwo', 'xiami', 'baiduFlac',
]
st.write("歌曲搜索范围选择:")
col_app = st.columns(5)
check_box_stat = []
for i in range(10):
    with col_app[i % 5]:
        if target_srcs[i] in ['qq', 'migu']:
            c = st.checkbox(target_srcs[i], value=True, key=target_srcs[i])
        else:
            c = st.checkbox(target_srcs[i], value=False, key=target_srcs[i])
        check_box_stat.append(c)


config = {'logfilepath': 'musicdl.log', 'savedir': 'downloaded', 'search_size_per_source': 10, 'proxies': {}}
client = musicdl.musicdl(config=config)


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
                        [str(idx), value['singers'], value['songname'], value['filesize'], value['duration'], value['ext'], value['album'],
                         value['source']])
                    records.update({str(idx): value})
                    idx += 1
            return items, records, title
    return None, None, None


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
downloaded_html = []
# streamlit本地静态资源目录 ~/miniconda3/lib/python3.7/site-packages/streamlit/static
st_static_path = pathlib.Path(st.__path__[0]) / 'static'
if len(selected_data) > 0:
    for value in selected_data:
        need_download_numbers.append(value['序号'])
    for id in need_download_numbers:
        songinfo = records.get(id, '').copy()
        # 文件下载后保存名称为 "歌曲名 - 歌手名"
        songinfo['savename'] = songinfo['songname'] + ' - ' + songinfo['singers']
        # st.write(songinfo)
        save_path = songinfo['savedir'] + '/' + songinfo['savename'] + '.' + songinfo['ext']
        full_path = st_static_path / save_path
        if os.path.exists(full_path):
            # st.write('{} exists'.format(save_path))
            pass
        else:
            songinfo['savedir'] = st_static_path / songinfo['savedir']
            songinfos.append(songinfo)
            download_music(songinfos)

        if os.path.exists(full_path):
            one_song = [songinfo['savename'] + '.' + songinfo['ext'], '<a href="{}" target="_blank" download="{}">下载</a>'.format(save_path, songinfo['savename'] + '.' + songinfo['ext'])]
        else:
            one_song = [songinfo['savename'] + '.' + songinfo['ext'], '<a>无法获取</a>'.format(save_path)]
        downloaded_html.append(one_song)

    download_frame = pd.DataFrame(downloaded_html, columns=['歌曲文件名称', '点击下载'])
    download_frame = download_frame.to_html(escape=False)
    st.write(download_frame,  unsafe_allow_html=True)
