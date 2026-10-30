import os
import sqlite3
import pandas as pd
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "library.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Books Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            book_name TEXT,
            author TEXT,
            category TEXT,
            total_copies INTEGER,
            available_copies INTEGER,
            publication_year INTEGER,
            department TEXT
        )
    ''')
    
    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            book_id TEXT,
            book_name TEXT,
            issue_date TEXT,
            expected_return_date TEXT,
            return_date TEXT,
            status TEXT
        )
    ''')
    
    # Pre-populate a wider set of books so the library has motivational, story, and inspiration titles.
    sample_books = [
        ("B101", "Python Programming", "Guido van Rossum", "Programming", 10, 5, 2021, "CSE"),
        ("B102", "Machine Learning", "Tom Mitchell", "AI/ML", 8, 2, 2019, "AIML"),
        ("B103", "Data Structures", "Mark Allen", "Computer Science", 12, 6, 2020, "CSE"),
        ("B104", "Operating Systems", "Silberschatz", "Computer Science", 15, 9, 2018, "CSE"),
        ("B105", "Digital Electronics", "M. Morris Mano", "Electronics", 10, 8, 2017, "ECE"),
        ("B106", "Artificial Intelligence", "Stuart Russell", "AI/ML", 6, 1, 2020, "AIML"),
        ("B107", "Atomic Habits", "James Clear", "Motivation", 8, 5, 2018, "General"),
        ("B108", "The Power of Habit", "Charles Duhigg", "Motivation", 7, 4, 2012, "General"),
        ("B109", "The Alchemist", "Paulo Coelho", "Stories", 9, 6, 1988, "General"),
        ("B110", "The Little Prince", "Antoine de Saint-Exupéry", "Stories", 10, 8, 1943, "General"),
        ("B111", "Earn the Right to Win", "Tommy ""Tom"" Caldwell", "Inspiration", 6, 3, 2020, "General"),
        ("B112", "The Monk Who Sold His Ferrari", "Robin Sharma", "Inspiration", 7, 5, 1997, "General"),
        ("B113", "Clean Code", "Robert C. Martin", "Technology", 9, 4, 2008, "CSE"),
        ("B114", "Deep Work", "Cal Newport", "Technology", 8, 5, 2016, "General"),
        ("B115", "The Lean Startup", "Eric Ries", "Business", 7, 3, 2011, "Management"),
        ("B116", "Rich Dad Poor Dad", "Robert Kiyosaki", "Business", 8, 4, 1997, "General"),
        ("B117", "The 7 Habits of Highly Effective People", "Stephen Covey", "Self-Development", 10, 7, 1989, "General"),
        ("B118", "Ikigai", "Héctor García & Francesc Miralles", "Self-Development", 9, 6, 2017, "General"),
        ("B119", "Pride and Prejudice", "Jane Austen", "Fiction", 10, 8, 1813, "General"),
        ("B120", "The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 7, 4, 1925, "General"),
        ("B121", "Sapiens", "Yuval Noah Harari", "History", 8, 5, 2014, "General"),
        ("B122", "The Story of My Experiments with Truth", "Mahatma Gandhi", "History", 6, 3, 1927, "General")
    ]

    existing_ids = {row[0] for row in cursor.execute("SELECT book_id FROM books").fetchall()}
    missing_books = [book for book in sample_books if book[0] not in existing_ids]
    if missing_books:
        cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)", missing_books)

    additional_books = [
        ("Automate the Boring Stuff with Python", "Al Sweigart", "Programming", 2015, "CSE"),
        ("Think Python", "Allen B. Downey", "Programming", 2015, "CSE"),
        ("Effective Python", "Brett Slatkin", "Programming", 2015, "CSE"),
        ("Fluent Python", "Luciano Ramalho", "Programming", 2015, "CSE"),
        ("Eloquent JavaScript", "Marijn Haverbeke", "Programming", 2018, "CSE"),
        ("The Pragmatic Programmer", "Andrew Hunt & David Thomas", "Programming", 1999, "CSE"),
        ("Head First Java", "Kathy Sierra & Bert Bates", "Programming", 2003, "CSE"),
        ("The C Programming Language", "Brian W. Kernighan & Dennis M. Ritchie", "Programming", 1978, "CSE"),
        ("Java: The Complete Reference", "Herbert Schildt", "Programming", 1997, "CSE"),
        ("Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "Aurélien Géron", "AI/ML", 2017, "AIML"),
        ("Deep Learning", "Ian Goodfellow, Yoshua Bengio & Aaron Courville", "AI/ML", 2016, "AIML"),
        ("Pattern Recognition and Machine Learning", "Christopher M. Bishop", "AI/ML", 2006, "AIML"),
        ("Deep Learning with Python", "François Chollet", "AI/ML", 2017, "AIML"),
        ("Data Mining: Concepts and Techniques", "Jiawei Han, Micheline Kamber & Jian Pei", "AI/ML", 2000, "AIML"),
        ("AI for Humans", "Jeff Heaton", "AI/ML", 2015, "AIML"),
        ("The Hundred-Page Machine Learning Book", "Andriy Burkov", "AI/ML", 2019, "AIML"),
        ("Machine Learning Yearning", "Andrew Ng", "AI/ML", 2018, "AIML"),
        ("Algorithms", "Robert Sedgewick & Kevin Wayne", "Computer Science", 1983, "CSE"),
        ("Introduction to Algorithms", "Thomas H. Cormen et al.", "Computer Science", 1990, "CSE"),
        ("Computer Networking: A Top-Down Approach", "James Kurose & Keith Ross", "Computer Science", 2000, "CSE"),
        ("Database System Concepts", "Abraham Silberschatz, Henry Korth & S. Sudarshan", "Computer Science", 1986, "CSE"),
        ("Computer Organization and Design", "David A. Patterson & John L. Hennessy", "Computer Science", 1994, "CSE"),
        ("Compilers: Principles, Techniques, and Tools", "Alfred V. Aho et al.", "Computer Science", 1986, "CSE"),
        ("Discrete Mathematics and Its Applications", "Kenneth H. Rosen", "Computer Science", 1984, "CSE"),
        ("Computer Systems: A Programmer's Perspective", "Randal E. Bryant & David R. O'Hallaron", "Computer Science", 2002, "CSE"),
        ("Microelectronic Circuits", "Adel S. Sedra & Kenneth C. Smith", "Electronics", 1982, "ECE"),
        ("Electronic Devices and Circuit Theory", "Robert L. Boylestad & Louis Nashelsky", "Electronics", 1972, "ECE"),
        ("Digital Design", "M. Morris Mano & Michael D. Ciletti", "Electronics", 1979, "ECE"),
        ("Fundamentals of Electric Circuits", "Charles K. Alexander & Matthew N. O. Sadiku", "Electronics", 2000, "ECE"),
        ("Embedded Systems", "Raj Kamal", "Electronics", 2003, "ECE"),
        ("Modern Control Engineering", "Katsuhiko Ogata", "Electronics", 1970, "ECE"),
        ("Electronic Principles", "Albert Malvino & David Bates", "Electronics", 1967, "ECE"),
        ("Principles of CMOS VLSI Design", "Neil H. E. Weste & David Money Harris", "Electronics", 1985, "ECE"),
        ("Signals and Systems", "Alan V. Oppenheim & Alan S. Willsky", "Electronics", 1983, "ECE"),
        ("Mindset", "Carol S. Dweck", "Motivation", 2006, "General"),
        ("Grit", "Angela Duckworth", "Motivation", 2016, "General"),
        ("Can't Hurt Me", "David Goggins", "Motivation", 2018, "General"),
        ("Drive", "Daniel H. Pink", "Motivation", 2009, "General"),
        ("The 5 AM Club", "Robin Sharma", "Motivation", 2018, "General"),
        ("Make Your Bed", "William H. McRaven", "Motivation", 2017, "General"),
        ("You Are a Badass", "Jen Sincero", "Motivation", 2013, "General"),
        ("The Compound Effect", "Darren Hardy", "Motivation", 2010, "General"),
        ("Animal Farm", "George Orwell", "Stories", 1945, "General"),
        ("The Old Man and the Sea", "Ernest Hemingway", "Stories", 1952, "General"),
        ("The Kite Runner", "Khaled Hosseini", "Stories", 2003, "General"),
        ("Life of Pi", "Yann Martel", "Stories", 2001, "General"),
        ("The Book Thief", "Markus Zusak", "Stories", 2005, "General"),
        ("To Kill a Mockingbird", "Harper Lee", "Stories", 1960, "General"),
        ("A Thousand Splendid Suns", "Khaled Hosseini", "Stories", 2007, "General"),
        ("The Hobbit", "J. R. R. Tolkien", "Stories", 1937, "General"),
        ("Long Walk to Freedom", "Nelson Mandela", "Inspiration", 1994, "General"),
        ("Wings of Fire", "A. P. J. Abdul Kalam & Arun Tiwari", "Inspiration", 1999, "General"),
        ("Tuesdays with Morrie", "Mitch Albom", "Inspiration", 1997, "General"),
        ("Man's Search for Meaning", "Viktor E. Frankl", "Inspiration", 1946, "General"),
        ("Unbroken", "Laura Hillenbrand", "Inspiration", 2010, "General"),
        ("Born a Crime", "Trevor Noah", "Inspiration", 2016, "General"),
        ("Educated", "Tara Westover", "Inspiration", 2018, "General"),
        ("Becoming", "Michelle Obama", "Inspiration", 2018, "General"),
        ("Code: The Hidden Language of Computer Hardware and Software", "Charles Petzold", "Technology", 1999, "CSE"),
        ("The Innovators", "Walter Isaacson", "Technology", 2014, "CSE"),
        ("The Phoenix Project", "Gene Kim, Kevin Behr & George Spafford", "Technology", 2013, "CSE"),
        ("Site Reliability Engineering", "Betsy Beyer et al.", "Technology", 2016, "CSE"),
        ("Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", 2017, "CSE"),
        ("The Soul of a New Machine", "Tracy Kidder", "Technology", 1981, "CSE"),
        ("The Art of Computer Programming", "Donald E. Knuth", "Technology", 1968, "CSE"),
        ("The Design of Everyday Things", "Don Norman", "Technology", 1988, "CSE"),
        ("Good to Great", "Jim Collins", "Business", 2001, "Management"),
        ("Zero to One", "Peter Thiel & Blake Masters", "Business", 2014, "Management"),
        ("Think and Grow Rich", "Napoleon Hill", "Business", 1937, "Management"),
        ("The E-Myth Revisited", "Michael E. Gerber", "Business", 1986, "Management"),
        ("Start with Why", "Simon Sinek", "Business", 2009, "Management"),
        ("Measure What Matters", "John Doerr", "Business", 2018, "Management"),
        ("Blue Ocean Strategy", "W. Chan Kim & Renée Mauborgne", "Business", 2005, "Management"),
        ("The Hard Thing About Hard Things", "Ben Horowitz", "Business", 2014, "Management"),
        ("How to Win Friends and Influence People", "Dale Carnegie", "Self-Development", 1936, "General"),
        ("Mindfulness in Plain English", "Bhante Henepola Gunaratana", "Self-Development", 1991, "General"),
        ("Essentialism", "Greg McKeown", "Self-Development", 2014, "General"),
        ("The Four Agreements", "Don Miguel Ruiz", "Self-Development", 1997, "General"),
        ("Thinking, Fast and Slow", "Daniel Kahneman", "Self-Development", 2011, "General"),
        ("The Subtle Art of Not Giving a F*ck", "Mark Manson", "Self-Development", 2016, "General"),
        ("The Art of Happiness", "The Dalai Lama & Howard C. Cutler", "Self-Development", 1998, "General"),
        ("Emotional Intelligence", "Daniel Goleman", "Self-Development", 1995, "General"),
        ("1984", "George Orwell", "Fiction", 1949, "General"),
        ("Jane Eyre", "Charlotte Brontë", "Fiction", 1847, "General"),
        ("Wuthering Heights", "Emily Brontë", "Fiction", 1847, "General"),
        ("Frankenstein", "Mary Shelley", "Fiction", 1818, "General"),
        ("The Catcher in the Rye", "J. D. Salinger", "Fiction", 1951, "General"),
        ("Dune", "Frank Herbert", "Fiction", 1965, "General"),
        ("Fahrenheit 451", "Ray Bradbury", "Fiction", 1953, "General"),
        ("The Picture of Dorian Gray", "Oscar Wilde", "Fiction", 1890, "General"),
        ("India After Gandhi", "Ramachandra Guha", "History", 2007, "General"),
        ("The Discovery of India", "Jawaharlal Nehru", "History", 1946, "General"),
        ("Guns, Germs, and Steel", "Jared Diamond", "History", 1997, "General"),
        ("The Diary of a Young Girl", "Anne Frank", "History", 1947, "General"),
        ("The Silk Roads", "Peter Frankopan", "History", 2015, "General"),
        ("SPQR: A History of Ancient Rome", "Mary Beard", "History", 2015, "General"),
        ("The Wright Brothers", "David McCullough", "History", 2015, "General"),
        ("The Guns of August", "Barbara W. Tuchman", "History", 1962, "General"),
    ]

    book_counts = dict(cursor.execute(
        "SELECT category, COUNT(*) FROM books GROUP BY category"
    ).fetchall())
    existing_titles = {
        row[0].casefold()
        for row in cursor.execute("SELECT book_name FROM books").fetchall()
    }
    next_book_number = 123
    for book_name, author, category, publication_year, department in additional_books:
        if book_counts.get(category, 0) >= 10 or book_name.casefold() in existing_titles:
            continue

        while f"B{next_book_number}" in existing_ids:
            next_book_number += 1
        book_id = f"B{next_book_number}"
        next_book_number += 1
        cursor.execute(
            """
            INSERT INTO books
                (book_id, book_name, author, category, total_copies, available_copies, publication_year, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (book_id, book_name, author, category, 5, 5, publication_year, department),
        )
        existing_ids.add(book_id)
        existing_titles.add(book_name.casefold())
        book_counts[category] = book_counts.get(category, 0) + 1
        
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)

def get_all_books():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM books", conn)
    conn.close()
    return df

def get_borrowing_history():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            transaction_id,
            student_id,
            student_name,
            book_id,
            book_name,
            issue_date,
            expected_return_date,
            return_date,
            status
        FROM transactions
        ORDER BY issue_date DESC, transaction_id DESC
        """,
        conn,
    )
    conn.close()
    return df

def get_student_issued_books(student_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT transaction_id, book_id, book_name, issue_date, expected_return_date
        FROM transactions
        WHERE student_id = ? AND status = ?
        ORDER BY issue_date, transaction_id
        """,
        conn,
        params=(student_id, "Issued"),
    )
    conn.close()
    return df

def return_book_db(transaction_id, student_id):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        loan = conn.execute(
            """
            SELECT book_id
            FROM transactions
            WHERE transaction_id = ? AND student_id = ? AND status = ?
            """,
            (transaction_id, student_id, "Issued"),
        ).fetchone()
        if loan is None:
            conn.rollback()
            return "not_issued"

        stock_update = conn.execute(
            """
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE book_id = ? AND available_copies < total_copies
            """,
            (loan[0],),
        )
        if stock_update.rowcount != 1:
            conn.rollback()
            return "inventory_error"

        conn.execute(
            """
            UPDATE transactions
            SET status = ?, return_date = ?
            WHERE transaction_id = ? AND student_id = ? AND status = ?
            """,
            ("Returned", date.today().isoformat(), transaction_id, student_id, "Issued"),
        )
        conn.commit()
        return "returned"
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def submit_book_request_db(student_id, student_name, book_id, book_name):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        student_id = student_id.strip()
        student_name = student_name.strip()
        if not student_id or not student_name:
            conn.rollback()
            return "invalid_student"

        existing_request = conn.execute(
            """
            SELECT 1
            FROM transactions
            WHERE student_id = ? AND book_id = ? AND status IN (?, ?)
            LIMIT 1
            """,
            (student_id, book_id, "Requested", "Issued"),
        ).fetchone()
        if existing_request is not None:
            conn.rollback()
            return "already_active"

        book_exists = conn.execute(
            "SELECT 1 FROM books WHERE book_id = ? LIMIT 1",
            (book_id,),
        ).fetchone()
        if book_exists is None:
            conn.rollback()
            return "book_not_found"

        conn.execute(
            """
            INSERT INTO transactions
                (student_id, student_name, book_id, book_name, issue_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, student_name, book_id, book_name, date.today().isoformat(), "Requested"),
        )
        conn.commit()
        return "submitted"
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def approve_book_request_db(transaction_id):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            "SELECT status FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()
        if request is None:
            conn.rollback()
            return "not_found"
        if request[0] != "Requested":
            conn.rollback()
            return "not_pending"

        book_id = conn.execute(
            "SELECT book_id FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()[0]
        stock_update = conn.execute(
            """
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE book_id = ? AND available_copies > 0
            """,
            (book_id,),
        )
        if stock_update.rowcount != 1:
            conn.rollback()
            return "unavailable"

        today = date.today()
        conn.execute(
            """
            UPDATE transactions
            SET status = ?, issue_date = ?, expected_return_date = ?
            WHERE transaction_id = ? AND status = ?
            """,
            (
                "Issued",
                today.isoformat(),
                (today + timedelta(days=14)).isoformat(),
                transaction_id,
                "Requested",
            ),
        )
        conn.commit()
        return "approved"
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def reject_book_request_db(transaction_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE transactions
            SET status = ?
            WHERE transaction_id = ? AND status = ?
            """,
            ("Rejected", transaction_id, "Requested"),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()

def delete_returned_transaction_db(transaction_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            DELETE FROM transactions
            WHERE transaction_id = ? AND status = ?
            """,
            (transaction_id, "Returned"),
        )
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_all_borrowing_history_db():
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        issued_loans = conn.execute(
            """
            SELECT book_id, COUNT(*)
            FROM transactions
            WHERE status = ?
            GROUP BY book_id
            """,
            ("Issued",),
        ).fetchall()

        for book_id, loan_count in issued_loans:
            conn.execute(
                """
                UPDATE books
                SET available_copies = MIN(total_copies, available_copies + ?)
                WHERE book_id = ?
                """,
                (loan_count, book_id),
            )

        deleted_count = conn.execute("DELETE FROM transactions").rowcount
        conn.commit()
        return deleted_count
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_demand_history_features():
    today = date.today()
    week_start = today - timedelta(days=6)
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            b.book_id,
            SUM(CASE WHEN t.status IN ('Issued', 'Returned') THEN 1 ELSE 0 END) AS Historical_Issues,
            SUM(CASE
                WHEN t.status IN ('Issued', 'Returned')
                    AND date(t.issue_date) BETWEEN date(?) AND date(?) THEN 1 ELSE 0
            END) AS Previous_Week_Issues
        FROM books AS b
        LEFT JOIN transactions AS t ON t.book_id = b.book_id
        GROUP BY b.book_id
        """,
        conn,
        params=(week_start.isoformat(), today.isoformat()),
    )
    conn.close()
    return df

def add_book_db(book_id, name, author, category, total_copies, pub_year, dept):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (book_id, name, author, category, total_copies, total_copies, pub_year, dept))
        conn.commit()
        success = True
    except Exception as e:
        success = False
    conn.close()
    return success

def issue_book_db(student_id, student_name, book_id, book_name, issue_date, return_date):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check available copies
    cursor.execute("SELECT available_copies FROM books WHERE book_id = ?", (book_id,))
    res = cursor.fetchone()
    if res and res[0] > 0:
        # Decrease available copies
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))
        # Insert transaction
        cursor.execute("INSERT INTO transactions (student_id, student_name, book_id, book_name, issue_date, expected_return_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (student_id, student_name, book_id, book_name, issue_date, return_date, "Issued"))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False