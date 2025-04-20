import functions
import elements
import gzip
import csv
import sqlite3


# Step 1: Read and extract .tsv.gz file
def read_tsv_gz(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            yield row

# Step 2: Create SQLite table
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            tconst TEXT PRIMARY KEY,
            titleType TEXT,
            primaryTitle TEXT,
            originalTitle TEXT,
            isAdult INTEGER,
            startYear INTEGER,
            endYear INTEGER,
            runtimeMinutes TEXT,
            genres TEXT
        )
    ''')
    conn.commit()

# Step 3: Insert data
def insert_data(conn, data):
    cursor = conn.cursor()
    for row in data:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['tconst'],
                row['titleType'],
                row['primaryTitle'],
                row['originalTitle'],
                int(row['isAdult']) if row['isAdult'] != '\\N' else 0,
                int(row['startYear']) if row['startYear'] != '\\N' else None,
                int(row['endYear']) if row['endYear'] != '\\N' else None,
                row['runtimeMinutes'],
                row['genres']
            ))
        except Exception as e:
            print(f"Skipping row due to error: {e}")
    conn.commit()

# Step 4: Query by genre and release year
def get_movies_by_any_genre(conn, genres, year=None):
    cursor = conn.cursor()
    
    # Start building the query
    query = '''
        SELECT primaryTitle, startYear, genres
        FROM movies
        WHERE (
    '''
    query += ' OR '.join(['genres LIKE ?' for _ in genres])
    query += ')'

    params = [f'%{genre}%' for genre in genres]

    # Add year filter if provided
    if year is not None:
        query += ' AND startYear = ?'
        params.append(year)

    query += ' ORDER BY primaryTitle'

    cursor.execute(query, params)
    return cursor.fetchall()


#sort movies according to genre, release date, movie name, cast


# Title
elements.title.pack(pady=10)

# Search bar frame
elements.search_frame.pack(pady=10)
elements.search_icon.pack(side="left")
elements.search_entry.pack(side="left")
elements.search_button.pack(side="left")

# Filters frame
elements.filters_frame.pack(pady=20)

# Cast
elements.cast_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
elements.cast_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

# Genre
elements.genre_label.grid(row=0, column=3, padx=5, pady=5, sticky="e")
elements.crew_combo.grid(row=0, column=4, columnspan=2, padx=5, pady=5)

# Release Date
elements.release_label.grid(row=1, column=0, padx=2, pady=3, sticky="e")
elements.release_min_date_label.grid(row=1, column=1, padx=3, pady=3, sticky="e")
elements.release_scale_min.grid(row=1, column=2, padx=2, pady=3)
elements.release_max_date_label.grid(row=1, column=3, padx=3, pady=3, sticky="e")
elements.release_scale_max.grid(row=1, column=4, padx=5, pady=3)

# Rating
elements.rating_label.grid(row=2, column=0, padx=2, pady=3, sticky="e")
elements.rating_min_date_label.grid(row=2, column=1, padx=3, pady=3, sticky="e")
elements.release_rate_min.grid(row=2, column=2, padx=2, pady=3)
elements.rating_max_date_label.grid(row=2, column=3, padx=3, pady=3, sticky="e")
elements.release_rate_max.grid(row=2, column=4, padx=5, pady=3)

# Run the app
elements.root.mainloop()

# ---- Main usage ----
if __name__ == "__main__":
    filename = 'title.basics.tsv.gz'  # Replace with your file name
    conn = sqlite3.connect('movies.db')

    create_table(conn)
    insert_data(conn, read_tsv_gz(filename))

    # Example query: Find Comedy movies released in 2010
    results = get_movies_by_genre_year(conn, genre='Comedy', year=2010)
    for movie in results[:10]:  # Just print top 10 for demo
        print(movie)

    conn.close()
