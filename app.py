import streamlit as st
import pandas as pd
import re
from io import BytesIO

@st.cache_data
def load_excel(file, usecols=None):
    return pd.read_excel(file, usecols=usecols)

@st.cache_data
def update_request_attributes(pim_df, req_df):
    # Precompute values efficiently
    req_df['Processed Attribute Name'] = req_df['Attribute Name'].apply(
        lambda x: "-".join(re.sub(r'\(.*?\)', '', x).strip().split()).lower()
    )

    # Map values based on Catalog Number and Processed Attribute Name
    req_df['Attribute Value'] = req_df.apply(
        lambda row: pim_df.loc[pim_df['catalog-number'] == row['Item no.'], row['Processed Attribute Name']].values[0]
        if row['Processed Attribute Name'] in pim_df.columns and not pim_df.loc[pim_df['catalog-number'] == row['Item no.']].empty
        else 'Null',
        axis=1
    )

    # Remove temporary column used for processing
    req_df.drop(columns=['Processed Attribute Name'], inplace=True)
    return req_df

st.title('PIM Data Attribute Query')

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    return output.getvalue()

# pagination
PAGE_SIZE = 50000

if 'page' not in st.session_state:
    st.session_state.page = 0

if 'visited_data' not in st.session_state:
    st.session_state.visited_data = pd.DataFrame()

pim_file = st.file_uploader('Upload Master DataSheet', type='xlsx')
if pim_file:
    pim_df = load_excel(pim_file)

request_file = st.file_uploader('Upload Request File', type='xlsx')
if request_file:
    request_df = load_excel(request_file)

    if pim_file:
        total_rows = len(request_df)
        start_idx = st.session_state.page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        paged_request_df = request_df[start_idx:end_idx]
        updated_request_df = update_request_attributes(pim_df, paged_request_df)

        st.session_state.visited_data = pd.concat(
            [st.session_state.visited_data, updated_request_df], ignore_index=True
        ).drop_duplicates()

        st.write(f'Displaying rows {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}')
        st.dataframe(updated_request_df)
        st.download_button(
            label="Download Output",
            data=to_excel(st.session_state.visited_data),
            file_name="Updated Request.xlsx",
            mime="application/vnd.openpyxl"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous") and st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
        with col2:
            if st.button("Next") and end_idx < total_rows:
                st.session_state.page += 1
                st.rerun()
       
