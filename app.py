import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import zipfile
import re
import io
import tempfile


st.title('Syllabus Sustainability Analizer')

uploaded_zip = st.file_uploader("Upload Folder (ZIP Only)", type="zip", max_upload_size=1715)
if uploaded_zip:

    st.write("you uploaded a zip")

    temp_folder = tempfile.TemporaryDirectory()
    temp_path = Path(temp_folder.name)

    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read())) as z:
        z.extractall(temp_path)
        st.success("Files extracted")

    all_files = [f for f in temp_path.rglob("*") if f.is_file()]
    file_extensions = [f.suffix for f in all_files]

    file_count = len(all_files)
    st.write(f"Total files unzipped: {file_count}")
    

    file_data = {"filename" : all_files, "extension" : file_extensions}
    
    df = pd.DataFrame(file_data, columns=("filename", "extension"))
    st.dataframe(df)

    extension_data = df['extension'].value_counts().to_dict()
    st.bar_chart(extension_data, horizontal=True)