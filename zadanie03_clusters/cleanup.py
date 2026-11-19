import csv
import json

def convert_ratings_csv_to_json(csv_filepath, json_filepath):
    ratings_dict = {}

    with open(csv_filepath, mode='r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        
        for row in reader:
            # Skip empty rows just in case
            if not row:
                continue
                
            name = row[0].strip()
            movie_data = {}
            
            # Start at index 1 and jump by 2 to grab (movie, mark) pairs
            for i in range(1, len(row), 2):
                # Ensure we don't go out of bounds if a row has an odd number of columns
                if i + 1 < len(row):
                    movie = row[i].strip()
                    mark_str = row[i+1].strip()
                    
                    # Ignore empty cells (common in CSVs with variable row lengths)
                    if movie and mark_str:
                        try:
                            # Convert the mark to an integer (e.g., 4)
                            movie_data[movie] = int(mark_str)
                        except ValueError:
                            print(f"Warning: Could not convert '{mark_str}' to a number for {name}. Skipping.")
            
            ratings_dict[name] = movie_data

    # Write the dictionary to a JSON file with a 4-space indent for readability
    with open(json_filepath, mode='w', encoding='utf-8') as json_file:
        json.dump(ratings_dict, json_file, indent=4, ensure_ascii=False)
        
    print(f"Successfully converted {csv_filepath} to {json_filepath}")

import json

def count_unique_movies(json_filepath):
    unique_movies = set()

    with open(json_filepath, mode='r', encoding='utf-8') as json_file:
        ratings_dict = json.load(json_file)
        
        # Go through each person's data
        for person, movies in ratings_dict.items():
            # Add all their movie titles to the set
            # Sets automatically ignore duplicates
            unique_movies.update(movies.keys())
            
    print(f"Total unique movies: {len(unique_movies)}")
    with open('titles.txt', mode='w', encoding='utf-8') as txt_file:
        for movie in sorted(unique_movies):
            txt_file.write(f"{movie}\n")


count_unique_movies('output2.json')
#convert_ratings_csv_to_json('dataset1.csv', 'output2.json')