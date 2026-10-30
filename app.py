import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import datetime
import os
import warnings

from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from database import (
    init_db,
    get_all_books,
    get_borrowing_history,
    get_student_issued_books,
    get_demand_history_features,
    add_book_db,
    submit_book_request_db,
    approve_book_request_db,
    reject_book_request_db,
    return_book_db,
    delete_returned_transaction_db,
    delete_all_borrowing_history_db,
)

# Initialize DB
init_db()

# Load ML Models
@st.cache_resource
def load_models(regression_mtime, classification_mtime):
    if regression_mtime is None or classification_mtime is None:
        return None, None
    lr = joblib.load(os.path.join(BASE_DIR, 'demand_regression_model.pkl'))
    rf = joblib.load(os.path.join(BASE_DIR, 'demand_classification_model.pkl'))
    return lr, rf

lr_model, rf_model = load_models(
    os.path.getmtime(os.path.join(BASE_DIR, 'demand_regression_model.pkl'))
    if os.path.exists(os.path.join(BASE_DIR, 'demand_regression_model.pkl')) else None,
    os.path.getmtime(os.path.join(BASE_DIR, 'demand_classification_model.pkl'))
    if os.path.exists(os.path.join(BASE_DIR, 'demand_classification_model.pkl')) else None,
)


def get_prediction_for_inputs(week_issues):
    if lr_model is None or rf_model is None:
        return None, None
    sample = pd.DataFrame({
        'Previous_Week_Issues': [week_issues],
    })
    predicted_level = rf_model.predict(sample)[0]
    predicted_issues = int(np.round(float(lr_model.predict(sample)[0])))
    return predicted_level, predicted_issues


st.set_page_config(page_title="AI Library Book Demand System", page_icon="📚", layout="wide")

st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Go to", ["📊 Prediction Dashboard", "👨‍🎓 Student Portal", "👨‍💼 Librarian / Admin Module", "🌟 Mood & Interest Recommendation"])

# ----------------- 1. PREDICTION DASHBOARD -----------------
if menu == "📊 Prediction Dashboard":
    st.title("📊 AI Library Book Demand prediction")

    books_df = get_all_books()
    st.subheader("🔮 Predicted Book Demand")
    st.caption(
        "See the estimated number of issues per title for next week and a demand level "
        "of LOW (0–2), MEDIUM (3–6), or HIGH (7+) expected issues. "
        "These estimates use generated demo training data."
    )

    if lr_model is not None and rf_model is not None:
        if books_df.empty:
            st.info("Add books to the inventory to see demand predictions.")
        else:
            demand_features = get_demand_history_features()
            if demand_features['Historical_Issues'].sum() == 0:
                st.info(
                    "No issue history is recorded yet. Predictions use zero recent activity "
                    "and should be treated as illustrative until real transactions are recorded."
                )

            feature_columns = ['Previous_Week_Issues']
            dashboard_df = books_df[['book_id', 'book_name', 'category', 'total_copies', 'available_copies']].merge(
                demand_features, on='book_id', how='left'
            )
            X_pred = dashboard_df[feature_columns]
            dashboard_df['Predicted Issues'] = np.maximum(
                lr_model.predict(X_pred), 0
            )
            dashboard_df['Demand Level'] = rf_model.predict(X_pred)

            filter_col1, filter_col2 = st.columns([2, 1])
            with filter_col1:
                book_search = st.text_input(
                    "Search titles",
                    placeholder="Type a book title...",
                    key="dashboard_book_search",
                ).strip()
            with filter_col2:
                categories = ["All categories"] + sorted(
                    dashboard_df["category"].dropna().unique().tolist()
                )
                selected_category = st.selectbox(
                    "Filter by category",
                    categories,
                    key="dashboard_category_filter",
                )

            visible_dashboard_df = dashboard_df
            if book_search:
                visible_dashboard_df = visible_dashboard_df[
                    visible_dashboard_df["book_name"].str.contains(
                        book_search,
                        case=False,
                        na=False,
                        regex=False,
                    )
                ]
            if selected_category != "All categories":
                visible_dashboard_df = visible_dashboard_df[
                    visible_dashboard_df["category"] == selected_category
                ]

            if visible_dashboard_df.empty:
                st.info("No books match the current search and category filters.")
            else:
                st.caption(
                    f"Showing {len(visible_dashboard_df)} of {len(dashboard_df)} titles. "
                    "Recent issues update as soon as a loan is approved. Forecasts are estimates, "
                    "and demand categories change when predicted demand crosses a category threshold."
                )
                with st.expander("Issue Forecast", expanded=True):
                    st.caption("Predicted number of book issues next week")
                    st.metric(
                        "Total predicted issues",
                        f"{visible_dashboard_df['Predicted Issues'].sum():.1f}",
                    )
                    st.caption("Recent issue counts are the live transaction totals used to calculate each forecast.")
                    st.dataframe(
                        visible_dashboard_df[[
                            'book_name',
                            'Previous_Week_Issues',
                            'Predicted Issues',
                        ]].rename(columns={
                            'book_name': 'Book',
                            'Previous_Week_Issues': 'Issues (7 days)',
                        }),
                        column_config={
                            'Predicted Issues': st.column_config.NumberColumn(
                                'Predicted Issues',
                                format='%.1f',
                            ),
                        },
                        width='stretch',
                        hide_index=True,
                    )
                    st.caption(
                        "Actual borrowing history, including books currently issued "
                        "and books already returned."
                    )
                    issued_history = get_borrowing_history()
                    issued_history = issued_history[
                        issued_history["status"].isin(["Issued", "Returned"])
                        & issued_history["book_id"].isin(visible_dashboard_df["book_id"])
                    ]
                    issued_counts = (
                        issued_history.groupby(["book_id", "book_name"])
                        .size()
                        .rename("Books issued")
                        .reset_index()
                        .sort_values("Books issued", ascending=False)
                    )
                    if issued_counts.empty:
                        st.info("No books have been issued in the selected titles yet.")
                    else:
                        issued_figure = px.bar(
                            issued_counts,
                            x='Books issued',
                            y='book_name',
                            orientation='h',
                            text='Books issued',
                            labels={
                                'book_name': 'Book title',
                                'Books issued': 'Actual issues',
                            },
                            color_discrete_sequence=['#3fb8a7'],
                        )
                        issued_figure.update_traces(textposition='outside')
                        issued_figure.update_layout(
                            height=max(320, len(issued_counts) * 34),
                            margin=dict(l=10, r=30, t=20, b=20),
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e6efed'),
                            xaxis=dict(rangemode='tozero', gridcolor='#33454a'),
                            yaxis=dict(title=None, autorange='reversed'),
                        )
                        st.plotly_chart(issued_figure, width='stretch')

                with st.expander("Demand Category", expanded=True):
                    st.caption(
                        "Demand is based on issues in the last 7 days, not copies in stock. "
                        "LOW = 0–2 expected issues, MEDIUM = 3–6, and HIGH = 7 or more. "
                        "Only approved loans count; pending requests do not."
                    )
                    demand_counts = visible_dashboard_df['Demand Level'].value_counts()
                    metric_cols = st.columns(3)
                    for metric_col, level in zip(metric_cols, ['LOW', 'MEDIUM', 'HIGH']):
                        metric_col.metric(
                            f"{level} demand books",
                            int(demand_counts.get(level, 0)),
                        )

                    st.caption(
                        "A book can have new issues and stay LOW while its estimated demand is "
                        "below 3. The table shows the last 7 days of issues and the next-week estimate."
                    )
                    rf_week_input = st.slider(
                        "Issues in the last 7 days",
                        min_value=0,
                        max_value=30,
                        value=8,
                        step=1,
                    )
                    rf_pred_level, rf_pred_issues = get_prediction_for_inputs(rf_week_input)
                    if rf_pred_level is not None and rf_pred_issues is not None:
                        st.info(
                            f"With {rf_week_input} issues in the last 7 days, the forecast is "
                            f"{rf_pred_level} demand with about {rf_pred_issues} expected issues next week."
                        )
                        level_color = {
                            'LOW': '#14765f',
                            'MEDIUM': '#8c5c0d',
                            'HIGH': '#aa3c3c',
                        }
                        st.markdown(
                            f"<div style='padding:1rem 1.2rem; border-radius:12px; background:{level_color.get(rf_pred_level, '#e5f3f4')}; color:white; font-weight:700; text-align:center;'>"
                            f"Demand forecast: {rf_pred_level}</div>",
                            unsafe_allow_html=True,
                        )

                    st.dataframe(
                        visible_dashboard_df[[
                            'book_name',
                            'Previous_Week_Issues',
                            'Predicted Issues',
                            'Demand Level',
                        ]].rename(columns={
                            'book_name': 'Book',
                            'Previous_Week_Issues': 'Issues (7 days)',
                        }),
                        column_config={
                            'Predicted Issues': st.column_config.NumberColumn(
                                'Expected issues (next week)',
                                format='%.1f',
                            ),
                        },
                        width='stretch',
                        hide_index=True,
                    )
                    st.caption("Books by predicted demand level")
                    demand_chart_data = pd.DataFrame({
                        'Demand level': ['LOW', 'MEDIUM', 'HIGH'],
                        'Number of books': [
                            int(demand_counts.get(level, 0))
                            for level in ['LOW', 'MEDIUM', 'HIGH']
                        ],
                    })
                    demand_figure = px.bar(
                        demand_chart_data,
                        x='Number of books',
                        y='Demand level',
                        orientation='h',
                        text='Number of books',
                        color='Demand level',
                        color_discrete_map={
                            'LOW': '#2a9d8f',
                            'MEDIUM': '#e9a23b',
                            'HIGH': '#d9534f',
                        },
                        category_orders={
                            'Demand level': ['LOW', 'MEDIUM', 'HIGH'],
                        },
                        labels={
                            'Demand level': 'Predicted demand',
                            'Number of books': 'Number of books',
                        },
                    )
                    demand_figure.update_traces(textposition='outside')
                    demand_figure.update_layout(
                        height=350,
                        margin=dict(l=10, r=30, t=20, b=20),
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e6efed'),
                        xaxis=dict(
                            rangemode='tozero',
                            gridcolor='#33454a',
                        ),
                        yaxis=dict(title=None),
                    )
                    st.plotly_chart(
                        demand_figure,
                        width='stretch',
                    )
    else:
        st.error("ML Models not found! Please run `train_model.py` first.")

# ----------------- 2. STUDENT PORTAL -----------------
elif menu == "👨‍🎓 Student Portal":
    st.title("👨‍🎓 Student Book Search & Request Portal")
    
    with st.form("student_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("Student ID", "STU1092", key="request_student_id").strip()
            student_name = st.text_input("Full Name", "Alex Smith", key="request_student_name").strip()
            dept = st.selectbox("Department", ["CSE", "AIML", "ECE", "EEE", "Mechanical"])
        with col2:
            year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
            category_pref = st.selectbox(
                "Preferred Category",
                [
                    "All",
                    "Programming",
                    "AI/ML",
                    "Computer Science",
                    "Electronics",
                    "Technology",
                    "Business",
                    "Motivation",
                    "Self-Development",
                    "Stories",
                    "Fiction",
                    "Inspiration",
                    "History",
                ],
            )
            
        submitted = st.form_submit_button("Search & Recommend Books")
        
    if submitted:
        if not student_id or not student_name:
            st.session_state["student_request_error"] = (
                "Enter both your Student ID and full name before searching."
            )
            st.session_state["show_student_recommendations"] = False
        else:
            st.session_state["student_request_error"] = None
            st.session_state["show_student_recommendations"] = True
            st.session_state["saved_request_student_id"] = student_id
            st.session_state["saved_request_student_name"] = student_name
            st.session_state["request_category_pref"] = category_pref

    if st.session_state.get("student_request_error"):
        st.error(st.session_state.pop("student_request_error"))

    if st.session_state.get("show_student_recommendations", False):
        request_student_id = st.session_state.get(
            "saved_request_student_id",
            student_id,
        ).strip()
        request_student_name = st.session_state.get(
            "saved_request_student_name",
            student_name,
        ).strip()
        st.success(
            f"Welcome {request_student_name}! Here are your tailored book recommendations:"
        )
        st.caption(
            f"Book requests will be submitted as {request_student_name} "
            f"({request_student_id})."
        )
        books_df = get_all_books()
        selected_category_pref = st.session_state.get(
            "request_category_pref",
            category_pref,
        )
        if selected_category_pref != "All":
            books_df = books_df[books_df['category'] == selected_category_pref]
        active_student_books = get_borrowing_history()
        active_student_books = active_student_books[
            (active_student_books["student_id"] == request_student_id)
            & active_student_books["status"].isin(["Requested", "Issued"])
        ]
        active_book_ids = set(active_student_books["book_id"])
        available_books = books_df[
            (books_df["available_copies"] > 0)
            & ~books_df["book_id"].isin(active_book_ids)
        ].copy()

        if available_books.empty:
            st.info(
                "No books with available copies match this category that you have not "
                "already requested or borrowed."
            )
        else:
            if active_book_ids:
                st.caption(
                    "Books you already have requested or borrowed are omitted from "
                    "the selection list."
                )
            books_by_id = available_books.set_index("book_id").to_dict("index")
            selected_book_id = st.selectbox(
                "Select an available book",
                available_books["book_id"].tolist(),
                format_func=lambda book_id: (
                    f"{books_by_id[book_id]['book_name']} — "
                    f"{books_by_id[book_id]['author']} "
                    f"({books_by_id[book_id]['available_copies']} available)"
                ),
                key="student_selected_book_id",
            )
            selected_book = books_by_id[selected_book_id]
            st.write(
                f"**Category:** {selected_book['category']} · "
                f"**Publication year:** {selected_book['publication_year']} · "
                f"**Available:** {selected_book['available_copies']} "
                f"of {selected_book['total_copies']} copies"
            )
            if st.button(
                "Request selected book",
                key="submit_selected_book_request",
                type="primary",
            ):
                result = submit_book_request_db(
                    request_student_id,
                    request_student_name,
                    selected_book_id,
                    selected_book["book_name"],
                )
                if result == "submitted":
                    st.success(
                        f"Request for '{selected_book['book_name']}' sent to the "
                        "librarian for approval."
                    )
                elif result == "already_active":
                    st.warning(
                        "You already have a pending request or an active loan for this book."
                    )
                elif result == "invalid_student":
                    st.error("Enter both your Student ID and full name before requesting a book.")
                else:
                    st.error(
                        "This book is no longer in the current library inventory. "
                        "Refresh the recommendations and try another book."
                    )

    st.markdown("---")
    st.subheader("📥 Return a Borrowed Book")
    return_student_id = st.text_input(
        "Enter your Student ID to see your issued books",
        key="return_student_id",
    ).strip()
    if st.session_state.get("return_message"):
        st.success(st.session_state.pop("return_message"))

    if return_student_id:
        issued_books = get_student_issued_books(return_student_id)
        if issued_books.empty:
            st.info("There are no currently issued books for this Student ID.")
        else:
            st.write("Select the book you are returning:")
            for _, loan in issued_books.iterrows():
                    loan_id = int(loan["transaction_id"])
                    book_col, return_col = st.columns([3, 1])
                    with book_col:
                        st.write(
                            f"**{loan['book_name']}** ({loan['book_id']}) — "
                            f"Issued {loan['issue_date']}; due {loan['expected_return_date']}"
                        )
                    with return_col:
                        if st.button("Return book", key=f"return_loan_{loan_id}"):
                            result = return_book_db(loan_id, return_student_id)
                            if result == "returned":
                                st.session_state["return_message"] = (
                                    f"'{loan['book_name']}' returned successfully."
                                )
                            elif result == "inventory_error":
                                st.error("The return could not be recorded because inventory is inconsistent.")
                            else:
                                st.warning("This loan is no longer active for this Student ID.")
                            if result == "returned":
                                st.rerun()

# ----------------- 3. LIBRARIAN MODULE -----------------
elif menu == "👨‍💼 Librarian / Admin Module":
    st.title("👨‍💼 Librarian Management Portal")
    
    tab1, tab2, tab3 = st.tabs([
        "➕ Add New Book",
        "📚 View Inventory Status",
        "📖 Borrowing History",
    ])
    
    with tab1:
        st.subheader("Add New Book to Library")
        with st.form("add_book_form"):
            b_id = st.text_input("Book ID (e.g., B107)", "B107")
            b_name = st.text_input("Book Name")
            b_author = st.text_input("Author Name")
            b_cat = st.text_input("Category")
            b_copies = st.number_input("Total Copies", min_value=1, value=5)
            b_year = st.number_input("Publication Year", min_value=1950, max_value=2026, value=2022)
            b_dept = st.text_input("Department", "CSE")
            
            submit_book = st.form_submit_button("Add Book")
            if submit_book:
                res = add_book_db(b_id, b_name, b_author, b_cat, int(b_copies), int(b_year), b_dept)
                if res:
                    st.success(f"Book '{b_name}' added successfully!")
                else:
                    st.error("Book ID already exists or invalid data.")
                    
    with tab2:
        st.subheader("Current Library Inventory")
        df_inv = get_all_books()
        st.dataframe(df_inv, width='stretch')

    with tab3:
        st.subheader("Book Requests & Borrowing History")
        if st.session_state.get("history_delete_message"):
            st.success(st.session_state.pop("history_delete_message"))
        if st.session_state.get("all_history_delete_message"):
            st.success(st.session_state.pop("all_history_delete_message"))

        st.markdown("#### Delete returned book history")
        history_df = get_borrowing_history()
        if history_df.empty:
            st.info("No book requests or borrowing records yet.")
            st.info(
                "No requests are waiting for approval. A student must submit a book "
                "request from the Student Portal before it appears here."
            )
            st.info("There are no returned book records to delete right now.")
        else:
            pending_count = int((history_df["status"] == "Requested").sum())
            issued_count = int((history_df["status"] == "Issued").sum())
            returned_count = int((history_df["status"] == "Returned").sum())
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Borrowing Records", len(history_df))
            col2.metric("Pending Requests", pending_count)
            col3.metric("Currently Issued", issued_count)
            col4.metric("Returned", returned_count)

            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Requested", "Issued", "Returned", "Rejected"],
                key="borrowing_history_status",
            )

            pending_requests = history_df[history_df["status"] == "Requested"]
            display_history = history_df
            if status_filter != "All":
                display_history = history_df[history_df["status"] == status_filter]

            if not pending_requests.empty:
                st.markdown("#### Requests waiting for approval")
                for _, request in pending_requests.iterrows():
                    request_id = int(request["transaction_id"])
                    with st.container(border=True):
                        st.write(
                            f"**{request['book_name']}** ({request['book_id']}) — "
                            f"{request['student_name']} ({request['student_id']}) · "
                            f"Requested {request['issue_date']}"
                        )
                        approve_col, reject_col = st.columns(2)
                        with approve_col:
                            if st.button("Approve", key=f"approve_request_{request_id}"):
                                result = approve_book_request_db(request_id)
                                if result == "approved":
                                    st.success("Request approved and book marked as issued.")
                                elif result == "unavailable":
                                    st.error("Cannot approve: no copies are currently available.")
                                else:
                                    st.warning("This request is no longer pending.")
                                st.rerun()
                        with reject_col:
                            if st.button("Reject", key=f"reject_request_{request_id}"):
                                if reject_book_request_db(request_id):
                                    st.success("Book request rejected.")
                                else:
                                    st.warning("This request is no longer pending.")
                                st.rerun()
            else:
                st.info(
                    "No requests are currently waiting for approval. New student "
                    "requests will appear here automatically."
                )

            returned_history = history_df[history_df["status"] == "Returned"]
            if not returned_history.empty:
                st.warning(
                    "Deleting a record permanently removes only its borrowing history. "
                    "The book's inventory count will not change."
                )
                returned_ids = returned_history["transaction_id"].astype(int).tolist()
                selected_return_id = st.selectbox(
                    "Select a returned transaction to delete",
                    returned_ids,
                    format_func=lambda transaction_id: (
                        f"{returned_history.loc[returned_history['transaction_id'] == transaction_id, 'book_name'].iloc[0]} — "
                        f"{returned_history.loc[returned_history['transaction_id'] == transaction_id, 'student_name'].iloc[0]} "
                        f"({returned_history.loc[returned_history['transaction_id'] == transaction_id, 'return_date'].iloc[0]})"
                    ),
                    key="returned_history_delete_selection",
                )
                confirm_delete = st.checkbox(
                    "I understand this permanently deletes the selected returned record.",
                    key="confirm_returned_history_delete",
                )
                if st.button(
                    "Delete selected returned record",
                    disabled=not confirm_delete,
                    type="primary",
                ):
                    if delete_returned_transaction_db(selected_return_id):
                        st.session_state["history_delete_message"] = (
                            "Returned borrowing history record deleted."
                        )
                    else:
                        st.session_state["history_delete_message"] = (
                            "That record is no longer marked Returned, so it was not deleted."
                        )
                    st.rerun()
            else:
                st.info("There are no returned book records to delete right now.")

            display_history = display_history.rename(columns={
                "transaction_id": "Transaction ID",
                "student_id": "Student ID",
                "student_name": "Student Name",
                "book_id": "Book ID",
                "book_name": "Book Name",
                "issue_date": "Issue Date",
                "expected_return_date": "Expected Return Date",
                "return_date": "Return Date",
                "status": "Status",
            })
            st.dataframe(display_history, width='stretch', hide_index=True)

        st.markdown("#### Delete all borrowing history")
        st.warning(
            "This permanently deletes every request and borrowing record, including active loans. "
            "Available-copy counts will be restored for books currently marked Issued."
        )
        clear_history_confirmation_key = (
            f"confirm_delete_all_borrowing_history_"
            f"{st.session_state.get('clear_history_confirmation_version', 0)}"
        )
        confirm_delete_all = st.checkbox(
            "I understand this permanently deletes all borrowing records.",
            key=clear_history_confirmation_key,
        )
        if st.button(
            "Delete all borrowing history",
            type="primary",
            disabled=history_df.empty or not confirm_delete_all,
        ):
            deleted_count = delete_all_borrowing_history_db()
            st.session_state["all_history_delete_message"] = (
                f"Deleted {deleted_count} borrowing record(s). "
                "Inventory was updated for active loans."
            )
            st.session_state["clear_history_confirmation_version"] = (
                st.session_state.get("clear_history_confirmation_version", 0) + 1
            )
            st.rerun()

# ----------------- 4. MOOD RECOMMENDATION -----------------
elif menu == "🌟 Mood & Interest Recommendation":
    st.title("🌟 Reading Interest Recommendation")
    st.write("Choose the type of books you want right now. Each option shows the matching books only.")

    reading_type = st.radio(
        "What kind of books do you want?",
        ["Study", "Motivation", "Stories", "Inspiration", "Technology", "Business", "Self-Development", "Fiction", "History"],
        horizontal=True,
    )

    books_df = get_all_books()
    if reading_type == "Study":
        filtered_books = books_df[books_df['category'].isin(['Programming', 'AI/ML', 'Computer Science', 'Electronics', 'Technology'])]
        st.info("Here are the study-related books for learning and academic growth:")
    elif reading_type == "Motivation":
        filtered_books = books_df[books_df['category'].isin(['Motivation', 'Self-Development'])]
        st.info("These books are for focus, discipline, and personal growth:")
    elif reading_type == "Stories":
        filtered_books = books_df[books_df['category'].isin(['Stories', 'Fiction'])]
        st.info("These books are for relaxing, thinking, and reading a good story:")
    elif reading_type == "Inspiration":
        filtered_books = books_df[books_df['category'] == 'Inspiration']
        st.info("These books are uplifting and confidence-building for a positive mindset:")
    elif reading_type == "Technology":
        filtered_books = books_df[books_df['category'] == 'Technology']
        st.info("These books are useful for technical learning and modern digital skills:")
    elif reading_type == "Business":
        filtered_books = books_df[books_df['category'] == 'Business']
        st.info("These books are for entrepreneurship, leadership, and business thinking:")
    elif reading_type == "Self-Development":
        filtered_books = books_df[books_df['category'] == 'Self-Development']
        st.info("These are personal growth and habit-building books:")
    elif reading_type == "Fiction":
        filtered_books = books_df[books_df['category'] == 'Fiction']
        st.info("These are imaginative and enjoyable reading picks:")
    else:
        filtered_books = books_df[books_df['category'] == 'History']
        st.info("Explore historical narratives, past events, and biographies:")

    if filtered_books.empty:
        st.info(f"No books currently available in the '{reading_type}' category.")
    else:
        for _, row in filtered_books.iterrows():
            with st.expander(f"📖 {row['book_name']} ({row['category']})"):
                st.write(f"**Author:** {row['author']} | **Year:** {row['publication_year']}")
                st.write(f"**Available Copies:** {row['available_copies']} / {row['total_copies']}")
                status_color = "🔴 HIGH DEMAND" if row['available_copies'] <= 2 else "🟢 AVAILABLE"
                st.write(f"**Status:** {status_color}")