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
 
# Step 1: Upload the master file
st.header("Step 1: Upload Master File")
master_file = st.file_uploader("Upload the master CSV file (containing 'Catalog Number', 'Spec Type', and 'URL')", type=["csv","xlsx"], key="master")
 
# Initialize session state to store the master DataFrame
if 'df' not in st.session_state:
    st.session_state.df = None
 
if master_file is not None:
    # Read and store the master file in session state
    st.session_state.df = pd.read_excel(master_file)
    st.write("Master File Uploaded Successfully:")
    st.dataframe(st.session_state.df)
 
    # Step 2: Upload the request file
    st.header("Step 2: Upload Request File")
    request_file = st.file_uploader("Upload the request CSV file (containing 'Item no.' and 'Media File Requested')", type=["csv","xlsx"], key="request")
 
    if request_file is not None:
        # Read the request file
        req = pd.read_excel(request_file)
        st.write("Request File Uploaded:")
        st.dataframe(req)
 
        # Process the data using the master DataFrame
        data = []
        for i, j in zip(req['Item no.'], req['Media File Requested']):
            try:
                new_df = st.session_state.df[(st.session_state.df["Catalog Number"] == i) & (st.session_state.df['Spec Type'] == documentDict.get(j))]
                if new_df.empty:
                    data.append("")
                else:
                    data.append(new_df['URL'].values[0])
            except Exception as e:
                st.error(f"Error processing item {i} for {j}: {e}")
 
        # Update the req DataFrame with the fetched URLs
        req["FileName or Path to File"] = data
 
        # Display the updated DataFrame
        st.header("Result")
        st.write("Updated Request Data with URLs:")
        st.dataframe(req)
 
        # Option to download the updated DataFrame
        csv = req.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Updated CSV",
            data=csv,
            file_name="updated_document_urls.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload the master file to proceed.")
 