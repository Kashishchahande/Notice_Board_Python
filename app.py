import os
from datetime import date, datetime
import pandas as pd
import streamlit as st

DATA_FILE = "notices.csv"
ADMIN_PASSWORD = os.getenv("NOTICE_ADMIN_PASSWORD", "admin123")
COLUMNS = ["ID", "Title", "Category", "Notice Date", "Description", "Posted On"]

def load_notices():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, dtype={"ID": str})
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS].fillna("")
        except Exception:
            pass
    return pd.DataFrame(columns=COLUMNS)

def save_notices(df):
    df[COLUMNS].to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Digital Notice Board", page_icon="📌", layout="wide")
st.markdown("""
<style>
.main {background-color: #f7f9fc;}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.2rem 1.5rem; border-radius: 16px; color: white;
       background: linear-gradient(120deg,#163a70,#2676b8); margin-bottom: 1rem;}
.notice-card {padding: 1rem; border: 1px solid #dfe6ef; border-radius: 12px;
              background: white; margin-bottom: .75rem;}
.small-muted {color: #637083; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

notices = load_notices()
st.markdown('<div class="hero"><h1>📌 Digital Notice Board System</h1><p>One place for campus updates, events and important announcements.</p></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Home / View Notices", "Administrator"])
st.sidebar.caption("Digital Notice Board • Python + Streamlit")

if menu == "Home / View Notices":
    st.subheader("Latest Notices")
    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input("Search notices", placeholder="Search title or description...")
    cats = ["All"] + sorted([x for x in notices["Category"].astype(str).unique() if x])
    category = c2.selectbox("Category", cats)
    sort_order = c3.selectbox("Sort by", ["Newest first", "Oldest first", "Category"])
    view = notices.copy()
    if search:
        mask = view["Title"].astype(str).str.contains(search, case=False, na=False) | view["Description"].astype(str).str.contains(search, case=False, na=False)
        view = view[mask]
    if category != "All":
        view = view[view["Category"] == category]
    if not view.empty:
        view["_date"] = pd.to_datetime(view["Notice Date"], errors="coerce")
        if sort_order == "Newest first":
            view = view.sort_values("_date", ascending=False, na_position="last")
        elif sort_order == "Oldest first":
            view = view.sort_values("_date", ascending=True, na_position="last")
        else:
            view = view.sort_values(["Category", "_date"], ascending=[True, False], na_position="last")
        st.caption(f"{len(view)} notice(s) found")
        for _, row in view.iterrows():
            st.markdown(f"""
            <div class="notice-card">
              <h3>{row['Title']}</h3>
              <p><b>Category:</b> {row['Category']} &nbsp; | &nbsp; <b>Notice date:</b> {row['Notice Date']}</p>
              <p>{row['Description']}</p>
              <p class="small-muted">Posted on: {row['Posted On']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No notices found. The administrator can add notices from the Administrator page.")
    st.download_button("Download visible notices (CSV)", view[COLUMNS].to_csv(index=False).encode("utf-8"),
                       file_name="visible_notices.csv", mime="text/csv", disabled=view.empty)

else:
    st.subheader("Administrator Panel")
    if not st.session_state.admin_logged_in:
        st.write("Sign in to manage notices.")
        with st.form("admin_login"):
            password = st.text_input("Administrator password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.caption("Demo password for local testing: admin123. Set NOTICE_ADMIN_PASSWORD before deployment.")
    else:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        tab_add, tab_edit, tab_delete, tab_all = st.tabs(["Add Notice", "Update Notice", "Delete Notice", "All Notices"])
        with tab_add:
            with st.form("add_notice", clear_on_submit=True):
                title = st.text_input("Notice title")
                category = st.selectbox("Category", ["General", "Academic", "Examination", "Events", "Placement", "Holiday", "Sports", "Urgent"])
                notice_date = st.date_input("Notice date", value=date.today())
                description = st.text_area("Notice description")
                add = st.form_submit_button("Publish Notice")
            if add:
                if not title.strip() or not description.strip():
                    st.error("Please enter both a title and description.")
                else:
                    current = load_notices()
                    next_id = str(max([int(x) for x in current["ID"] if str(x).isdigit()] + [0]) + 1)
                    new = pd.DataFrame([{"ID": next_id, "Title": title.strip(), "Category": category,
                                         "Notice Date": str(notice_date), "Description": description.strip(),
                                         "Posted On": str(date.today())}])
                    save_notices(pd.concat([current, new], ignore_index=True))
                    st.success("Notice published successfully.")
                    st.rerun()
        with tab_edit:
            current = load_notices()
            if current.empty:
                st.info("There are no notices to update.")
            else:
                ids = current["ID"].astype(str).tolist()
                selected_id = st.selectbox("Select notice ID", ids, key="edit_id")
                row = current[current["ID"].astype(str) == selected_id].iloc[0]
                with st.form("edit_notice"):
                    new_title = st.text_input("Title", value=str(row["Title"]))
                    categories = ["General", "Academic", "Examination", "Events", "Placement", "Holiday", "Sports", "Urgent"]
                    old_cat = str(row["Category"])
                    cat_index = categories.index(old_cat) if old_cat in categories else 0
                    new_category = st.selectbox("Category", categories, index=cat_index)
                    try:
                        old_date = date.fromisoformat(str(row["Notice Date"]))
                    except Exception:
                        old_date = date.today()
                    new_date = st.date_input("Notice date", value=old_date)
                    new_description = st.text_area("Description", value=str(row["Description"]))
                    update = st.form_submit_button("Save Changes")
                if update:
                    if not new_title.strip() or not new_description.strip():
                        st.error("Title and description cannot be empty.")
                    else:
                        current.loc[current["ID"].astype(str) == selected_id, COLUMNS[1:5]] = [
                            new_title.strip(), new_category, str(new_date), new_description.strip()]
                        save_notices(current)
                        st.success("Notice updated successfully.")
                        st.rerun()
        with tab_delete:
            current = load_notices()
            if current.empty:
                st.info("There are no notices to delete.")
            else:
                options = {f"{r['ID']} — {r['Title']}": str(r["ID"]) for _, r in current.iterrows()}
                label = st.selectbox("Select notice to delete", list(options.keys()))
                confirm = st.checkbox("I confirm that I want to delete this notice.")
                if st.button("Delete Selected Notice", type="primary"):
                    if confirm:
                        save_notices(current[current["ID"].astype(str) != options[label]])
                        st.success("Notice deleted.")
                        st.rerun()
                    else:
                        st.warning("Please confirm before deleting.")
        with tab_all:
            current = load_notices()
            if current.empty:
                st.info("No notices have been published yet.")
            else:
                st.dataframe(current, use_container_width=True, hide_index=True)
                st.download_button("Download all notices (CSV)", current.to_csv(index=False).encode("utf-8"),
                                   file_name="notices.csv", mime="text/csv")
