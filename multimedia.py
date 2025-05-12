import streamlit as st
import pandas as pd
 
# Document dictionary for mapping requested media files to spec types
documentDict = {
    "Installation Instructions": "Installation",
    "Warranty Document": "Warranty Card",
    "Use & Care Instructions": "Owners Manual",
    "Consumer Literature": "Brochure",
    "Specification Sheet": "Product Data",
    "Wiring Diagrams": "Wiring Diagrams",
    "Submittal Sheet": "Submittal"
}
 
# Streamlit app title
st.title("Document URL Fetcher")
 
# Cache file loading
@st.cache_data
def load_file(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
 
# Step 1: Upload the master file
st.header("Step 1: Upload Master File")
master_file = st.file_uploader("Upload the master CSV or XLSX file (containing 'Catalog Number', 'Spec Type', and 'URL')",
                              type=["csv", "xlsx"], key="master")
 
# Initialize session state to store the master DataFrame
if 'df' not in st.session_state:
    st.session_state.df = None
 
if master_file is not None:
    with st.spinner("Reading master file..."):
        st.session_state.df = load_file(master_file)
    
    if st.session_state.df is None:
        st.error("Failed to read the master file. Please check the file format and try again.")
        st.stop()
    
    # Verify required columns
    required_columns = ['Catalog Number', 'Spec Type', 'URL']
    if not all(col in st.session_state.df.columns for col in required_columns):
        st.error("Master file is missing required columns: 'Catalog Number', 'Spec Type', 'URL'")
        st.stop()
    
    st.success(f"Master File Uploaded Successfully! ({st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} columns)")
    
    # Option to display the full DataFrame
    if st.checkbox("Show full master DataFrame (may be slow for large files)"):
        st.dataframe(st.session_state.df)
    else:
        st.write("Preview of first 10 rows:")
        st.dataframe(st.session_state.df.head(10))
 
    # Step 2: Upload the request file
    st.header("Step 2: Upload Request File")
    request_file = st.file_uploader("Upload the request CSV or XLSX file (containing 'Item no.' and 'Media File Requested')",
                                   type=["csv", "xlsx"], key="request")
 
    if request_file is not None:
        with st.spinner("Reading request file..."):
            req = load_file(request_file)
        
        if req is None:
            st.error("Failed to read the request file. Please check the file format and try again.")
            st.stop()
        
        st.write("Request File Uploaded:")
        st.dataframe(req.head(10))  # Show preview to avoid slowdown
 
        # Process the data using the master DataFrame
        data = []
        progress_bar = st.progress(0)
        total_rows = len(req)
        
        for idx, (i, j) in enumerate(zip(req['Item no.'], req['Media File Requested'])):
            try:
                spec_type = documentDict.get(j)
                if not spec_type:
                    data.append("")
                    continue
                new_df = st.session_state.df[(st.session_state.df["Catalog Number"] == i) &
                                           (st.session_state.df['Spec Type'] == spec_type)]
                if new_df.empty:
                    data.append("")
                else:
                    data.append(new_df['URL'].values[0])
            except Exception as e:
                st.error(f"Error processing item {i} for {j}: {e}")
                data.append("")
            
            # Update progress bar
            progress_bar.progress((idx + 1) / total_rows)
 
        # Update the req DataFrame with the fetched URLs
        req["FileName or Path to File"] = data
 
        # Display the updated DataFrame
        st.header("Result")
        st.write("Updated Request Data with URLs:")
        st.dataframe(req)
 
        # Option to download the updated DataFrame
        with st.spinner("Preparing download..."):
            csv = req.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Updated CSV",
            data=csv,
            file_name="updated_document_urls.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload the master file to proceed.")