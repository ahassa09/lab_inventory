# For browsing and searching the inventory only.
# This appliction does not allow users to edit, delete, or add items.

import streamlit as st
import sqlite3
import pandas as pd
import os

# Database shared between inventory viewer and admin files
DB_NAME = "inventory.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def get_items():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM items", conn)
    conn.close()
    return df


# Search function
st.title("Lab Inventory Search") 

items_df = get_items()

search = st.text_input("Search by name, category, or location")

if search and not items_df.empty:
    items_df = items_df[
        items_df["name"].str.contains(search, case=False, na=False) |
        items_df["category"].str.contains(search, case=False, na=False) |
        items_df["location"].str.contains(search, case=False, na=False)
    ]

if items_df.empty:
    st.info("No items found.")
else:
    for _, row in items_df.iterrows():
        col1, col2 = st.columns([1, 3])

        with col1:
            img = row["image_path"]

            if isinstance(img, str) and os.path.exists(img):
                st.image(img, width=150)
            else:
                st.write("No image")

            with col2:
                st.subheader(row["name"])
                st.write(f"Category: {row['category']}")
                st.write(f"Location: {row['location']}")
                st.write(f"Quantity: {row['quantity']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Notes: {row['notes']}")

                # Buttons to download documentation and video if they were provided
                doc = row["documentation"]

                if isinstance(doc, str) and os.path.exists(doc):
                    with open(doc, "rb") as pdf_file:
                        st.download_button(
                            label="Open / Download Documentation",
                        data=pdf_file,
                        file_name=os.path.basename(doc),
                            mime="application/pdf",
                            key=f"viewer_pdf_{row['id']}"
                    )
                else:
                    st.write("Documentation: None provided")

                app_notes = row["application_notes"]

                if isinstance(app_notes, str) and os.path.exists(app_notes):
                    with open(row["application_notes"], "rb") as notes_file:
                        st.download_button(
                            label="Open / Download Lab Application Notes",
                            data=notes_file,
                            file_name=os.path.basename(row["application_notes"]),
                            mime="application/pdf",
                            key=f"app_notes_{row['id']}"
                        )
                else:
                    st.write("Lab application notes: None provided")

                
                vid = row["video_path"]

                if isinstance(vid, str) and os.path.exists(vid):
                        with open(row["video_path"], "rb") as video_file:
                            st.download_button(
                                label="Download Video",
                                data=video_file,
                                file_name=os.path.basename(row["video_path"]),
                                mime="video/mp4",
                                key=f"download_video_{row['id']}"
                            )
                else:
                    st.write("Video: None provided")

        st.divider()