
import requests
import time
from bs4 import BeautifulSoup
import psycopg2
import re
from dotenv import load_dotenv
import os

# Database configuration
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# GraphQL query
query = """
query getQuestionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    content
    difficulty
    likes
    dislikes
    topicTags {
      name
      slug
    }
  }
}
"""

with open("slugs.txt", "r") as f:
    slugs = [line.strip() for line in f.readlines() if line.strip()]

headers_base = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Loop over slugs
for slug in slugs:
    headers = headers_base.copy()
    headers["Referer"] = f"https://leetcode.com/problems/{slug}/"
    url = "https://leetcode.com/graphql"
    variables = {"titleSlug": slug}

    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        data = response.json()
        question = data["data"]["question"]

        if question is None:
            print(f"❌ Skipped slug '{slug}': No data returned.")
            continue

        soup = BeautifulSoup(question["content"], "html.parser")
        clean_description = soup.get_text()

        # Extract examples and constraints
        example_blocks = re.findall(r'Example \d+:(.*?)Constraints:', clean_description, re.DOTALL)
        examples = []
        for block in example_blocks:
            input_match = re.search(r'Input:\s*(.*)', block)
            output_match = re.search(r'Output:\s*(.*)', block)
            explanation_match = re.search(r'Explanation:\s*(.*)', block)
            if input_match and output_match:
                examples.append({
                    "input": input_match.group(1).strip(),
                    "output": output_match.group(1).strip(),
                    "explanation": explanation_match.group(1).strip() if explanation_match else None
                })

        constraint_block = re.search(r'Constraints:(.*)', clean_description, re.DOTALL)
        constraints = []
        if constraint_block:
            for line in constraint_block.group(1).split('\n'):
                line = line.strip()
                if line:
                    constraints.append(line)

        # Insert into problems table
        cur.execute("""
            INSERT INTO problems (title, slug, difficulty, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            RETURNING id
        """, (question['title'], slug, question['difficulty'], clean_description))
        problem_row = cur.fetchone()

        if problem_row:
            problem_id = problem_row[0]
        else:
            cur.execute("SELECT id FROM problems WHERE slug = %s", (slug,))
            problem_id = cur.fetchone()[0]

        # Insert tags and relations
        for tag in question['topicTags']:
            cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (tag['name'],))
            cur.execute("SELECT id FROM tags WHERE name = %s", (tag['name'],))
            tag_id = cur.fetchone()[0]
            cur.execute("INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (problem_id, tag_id))

        # Insert examples
        for ex in examples:
            cur.execute("""
                INSERT INTO examples (problem_id, input, output, explanation)
                VALUES (%s, %s, %s, %s)
            """, (problem_id, ex['input'], ex['output'], ex['explanation']))

        # Insert constraints
        for c in constraints:
            cur.execute("""
                INSERT INTO constraints (problem_id, constraint_text)
                VALUES (%s, %s)
            """, (problem_id, c))

        conn.commit()
        print(f"✅ Inserted: {question['title']}")

        # Be polite to LeetCode servers
        time.sleep(1.5)

    except Exception as e:
        print(f"❌ Error with slug '{slug}': {e}")
        conn.rollback()
        time.sleep(3)

cur.close()
conn.close()
print("🎉 All done!")
