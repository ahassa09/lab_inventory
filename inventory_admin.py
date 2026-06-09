# This application allows the user to browse and search the inventory.
# Users can also edit, add and delete items.

import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "inventory.db"
IMAGE_FOLDER = "images"
DOCUMENT_FOLDER = "documents"
VIDEO_FOLDER = "videos"

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(DOCUMENT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            location TEXT,
            documentation TEXT,
            application_notes TEXT,
            quantity INTEGER,
            status TEXT,
            notes TEXT,
            image_path TEXT,
            video_path TEXT
        )
    """)
    conn.commit()
    conn.close()


# Functions
def add_item(name, category, location, documentation, application_notes, quantity, status, notes, image_path, video_path):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items 
        (name, category, location, documentation, application_notes, quantity, status, notes, image_path, video_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, location, documentation, application_notes, quantity, status, notes, image_path, video_path))
    conn.commit()
    conn.close()

def get_items():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM items", conn)
    conn.close()
    return df

def get_item_by_id(item_id):
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM items WHERE id = ?", conn, params=(item_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def update_item(item_id, name, category, location, documentation, application_notes, quantity, status, notes, image_path, video_path):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET name = ?, category = ?, location = ?, documentation = ?, application_notes = ?, quantity = ?, status = ?, notes = ?, image_path = ?, video_path = ?
        WHERE id = ?
    """, (name, category, location, documentation, application_notes, quantity, status, notes, image_path, video_path, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

create_table()

if "page" not in st.session_state:
    st.session_state["page"] = "Inventory"

if "edit_item_id" not in st.session_state:
    st.session_state["edit_item_id"] = None

st.title("Lab Inventory")

tabs = ["Inventory", "Add Item", "Edit Item", "Delete Item"]

selected_tab = st.radio(
    "",
    tabs,
    horizontal=True,
    index=tabs.index(st.session_state["page"])
)

st.session_state["page"] = selected_tab
page = selected_tab

# Inventory page (viewing items)
if page == "Inventory":
    st.header("Inventory List")

    items_df = get_items()

    search = st.text_input("Search items")

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
                if row["image_path"] and os.path.exists(row["image_path"]):
                    st.image(row["image_path"], width=150)
                else:
                    st.write("No image")

            with col2:
                st.subheader(row["name"])
                st.write(f"ID: {row['id']}")
                st.write(f"Category: {row['category']}")
                st.write(f"Location: {row['location']}")
                st.write(f"Quantity: {row['quantity']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Notes: {row['notes']}")

            # Buttons to download documentation and video if they have been provided 
            if row["documentation"] and os.path.exists(row["documentation"]):
                with open(row["documentation"], "rb") as pdf_file:
                    st.download_button(
                        label="Open / Download Documentation (PDF)",
                        data=pdf_file,
                        file_name=os.path.basename(row["documentation"]),
                        mime="application/pdf",
                        key=f"download_pdf_{row['id']}"
                    )
            else:
                st.write("Documentation: None provided")

            if row["application_notes"] and os.path.exists(row["application_notes"]):
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

            if row["video_path"] and os.path.exists(row["video_path"]):
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

# Add item page
elif page == "Add Item":
    st.header("Add New Item")

    with st.form("add_item_form"):
        name = st.text_input("Item name")
        category = st.text_input("Category")
        location = st.text_input("Location") 
        documentation_file = st.file_uploader("Upload documentation (PDF)", type=["pdf"])
        application_notes_file = st.file_uploader("Upload lab application notes (PDF)", type=["pdf"])
        quantity = st.number_input("Quantity", min_value=0, step=1)
        status = st.selectbox("Status", ["Available", "In use", "Broken", "Missing"])
        notes = st.text_area("Notes")
        image = st.file_uploader("Upload item image", type=["jpg", "jpeg", "png"])
        video = st.file_uploader("Upload item video", type=["mp4", "mov", "avi"])

        submitted = st.form_submit_button("Save Item")
        if submitted:
            if not name:
                st.error("Item name is required.")
            else:
                image_path = ""
                documentation_path = ""
                video_path = ""
                application_notes_path = ""

                # Showing documentation, image, video
                if documentation_file is not None:
                    documentation_path = os.path.join(DOCUMENT_FOLDER, documentation_file.name)
                    with open(documentation_path, "wb") as f:
                        f.write(documentation_file.getbuffer())

                if application_notes_file is not None:
                    application_notes_path = os.path.join(DOCUMENT_FOLDER, application_notes_file.name)
                    with open(application_notes_path, "wb") as f:
                        f.write(application_notes_file.getbuffer())

                if image is not None:
                    image_path = os.path.join(IMAGE_FOLDER, image.name)
                    with open(image_path, "wb") as f:
                        f.write(image.getbuffer())

                if video is not None:
                    video_path = os.path.join(VIDEO_FOLDER, video.name)
                    with open(video_path, "wb") as f:
                        f.write(video.getbuffer())

                add_item(name, category, location, documentation_path, application_notes_path, quantity, status, notes, image_path, video_path)
                st.success("Item added successfully.")

    if st.button("Back to Inventory"):
        st.session_state["page"] = "Inventory"
        st.rerun()

# Edit item page
elif page == "Edit Item":
    st.header("Edit Item")

    items_df = get_items()

    if items_df.empty:
        st.info("No items available to edit.")
    else:
        item_options = {
            f"{row['id']} - {row['name']}": row["id"]
            for _, row in items_df.iterrows()
        }

        selected_label = st.selectbox("Select item to edit", list(item_options.keys()))
        selected_id = item_options[selected_label]

        item = get_item_by_id(selected_id)

        if item is not None:
            current_image_path = item["image_path"] if pd.notna(item["image_path"]) else ""

            if current_image_path and os.path.exists(current_image_path):
                st.image(current_image_path, width=200)

            current_documentation_path = item["documentation"] if pd.notna(item["documentation"]) else ""

            if current_documentation_path and os.path.exists(current_documentation_path):
                with open(current_documentation_path, "rb") as pdf_file:
                    st.download_button(
                        label="Current Documentation",
                        data=pdf_file,
                        file_name=os.path.basename(current_documentation_path),
                        mime="application/pdf",
                        key=f"current_doc_{selected_id}"
                    )

            current_application_notes_path = item["application_notes"] if pd.notna(item["application_notes"]) else ""

            if current_application_notes_path and os.path.exists(current_application_notes_path):
                with open(current_application_notes_path, "rb") as app_file:
                    st.download_button(
                        label="Current Lab Application Notes",
                        data=app_file,
                        file_name=os.path.basename(current_application_notes_path),
                        mime="application/pdf",
                        key=f"current_app_notes_{selected_id}"
                    )

            current_video_path = item["video_path"] if pd.notna(item["video_path"]) else ""

            if current_video_path and os.path.exists(current_video_path):
                st.video(current_video_path)
            with st.form("edit_item_form"):
                name = st.text_input("Item name", value=item["name"])
                category = st.text_input("Category", value=item["category"] or "")
                location = st.text_input("Location", value=item["location"] or "")
                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    step=1,
                    value=int(item["quantity"]) if pd.notna(item["quantity"]) else 0
                )

                status_options = ["Available", "In use", "Broken", "Missing"]
                current_status = item["status"] if item["status"] in status_options else "Available"

                status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(current_status)
                )

                new_documentation_file = st.file_uploader("Upload documentation (PDF)", type=["pdf"])
                new_application_file = st.file_uploader("Upload lab application (PDF)", type=["pdf"])

                notes = st.text_area("Notes", value=item["notes"] or "")
                new_image = st.file_uploader("Upload new image", type=["jpg", "jpeg", "png"])
                new_video = st.file_uploader("Upload new video", type=["mp4", "mov", "avi"])

                submitted = st.form_submit_button("Update Item")

                # Name is required field, should there be other required fields too ?  location ?
                if submitted:
                    if not name:
                        st.error("Item name is required.")
                    else:
                        image_path = current_image_path

                        if new_image is not None:
                            image_path = os.path.join(IMAGE_FOLDER, new_image.name)
                            with open(image_path, "wb") as f:
                                f.write(new_image.getbuffer())

                        documentation_path = current_documentation_path

                        if new_documentation_file is not None:
                            documentation_path = os.path.join(DOCUMENT_FOLDER, new_documentation_file.name)
                            with open(documentation_path, "wb") as f:
                                f.write(new_documentation_file.getbuffer())

                        application_notes_path = current_application_notes_path

                        if new_application_file is not None:
                            application_notes_path = os.path.join(DOCUMENT_FOLDER, new_application_file.name)
                            with open(application_notes_path, "wb") as f:
                                f.write(new_application_file.getbuffer())
                        
                        video_path = current_video_path

                        if new_video is not None:
                            video_path = os.path.join(VIDEO_FOLDER, new_video.name)
                            with open(video_path, "wb") as f:
                                f.write(new_video.getbuffer())

                        update_item(
                            selected_id,
                            name,
                            category,
                            location,
                            documentation_path,
                            application_notes_path,
                            quantity,
                            status,
                            notes,
                            image_path,
                            video_path
                        )

                        st.success("Item updated successfully.")
                        st.rerun()

# Delete item page
elif page == "Delete Item":
    st.header("Delete Item")

    items_df = get_items()

    if items_df.empty:
        st.info("No items available to delete.")
    else:
        item_options = {
            f"{row['id']} - {row['name']}": row["id"]
            for _, row in items_df.iterrows()
        }

        selected_label = st.selectbox("Select item to delete", list(item_options.keys()))
        selected_id = item_options[selected_label]

        item = get_item_by_id(selected_id)

        if item is not None:
            st.warning(f"You are about to delete: {item['name']}")

            confirm = st.checkbox("Are you sure you want to delete this item?")

            if st.button("Delete Item"):
                if confirm:
                    delete_item(selected_id)
                    st.success("Item deleted successfully.")
                    st.rerun()
                else:
                    st.error("Please confirm deletion.")