import streamlit as st
from opensearchpy import OpenSearch
import os

# Define the authentication details
host = os.getenv("HOST_OS")
username = os.getenv("USERNAME_OS")
password = os.getenv("PASSWORD_OS")

# Create a connection to your OpenSearch cluster with authentication
client = OpenSearch(
    hosts=[host],
    http_auth=(username, password),
    port=443,
    use_ssl=True,
)

st.title("Prüfungsordnungen Suche 🔎📜")

# Retrieve unique faculty values
query = {
    "aggs": {
        "unique_faculties": {
            "terms": {
                "field": "faculty.keyword",
                "size": 10000
            }
        }
    },
    "size": 0
}
response = client.search(index="slenert", body=query)
faculty_types = ["Bitte auswählen"] + [bucket["key"] for bucket in response["aggregations"]["unique_faculties"]["buckets"]]

# Select faculty type
faculty_type = st.selectbox("Fakultät auswählen", faculty_types)

if faculty_type != "Bitte auswählen":
    # Retrieve unique degree values for the selected faculty
    query = {
        "query": {
            "term": {
                "faculty.keyword": faculty_type
            }
        },
        "aggs": {
            "unique_degrees": {
                "terms": {
                    "field": "degree.keyword",
                    "size": 10000
                }
            }
        },
        "size": 0
    }
    response = client.search(index="slenert", body=query)
    degree_types = ["Bitte auswählen"] + [bucket["key"] for bucket in response["aggregations"]["unique_degrees"]["buckets"]]

    # Select degree type
    degree_type = st.selectbox("Art des Abschlusses auswählen", degree_types)

    if degree_type != "Bitte auswählen":
        # Retrieve unique program values for the selected faculty and degree
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"faculty.keyword": faculty_type}},
                        {"term": {"degree.keyword": degree_type}}
                    ]
                }
            },
            "aggs": {
                "unique_programs": {
                    "terms": {
                        "field": "program.keyword",
                        "size": 10000
                    }
                }
            },
            "size": 0
        }
        response = client.search(index="slenert", body=query)
        program_types = ["Bitte auswählen"] + [bucket["key"] for bucket in response["aggregations"]["unique_programs"]["buckets"]]

        # Select program type
        if len(program_types) > 1:
            program_type = st.selectbox("Bitte Programm auswählen", program_types)
        else:
            program_type = None

        if program_type != "Bitte auswählen":
            st.markdown("---")  # Add a visual divider
            
            # Select search mode
            search_mode = st.radio("Suchmodus auswählen", ("Fuzziness", "Exact"))

            # Enter search query
            search_query = st.text_input("Suche nach Inhalten", "")

            if search_query:
                # Construct the query
                query = {
                    "size": 10,
                    "query": {
                        "bool": {
                            "filter": [
                                {"term": {"degree.keyword": degree_type}},
                                {"term": {"faculty.keyword": faculty_type}},
                                {"term": {"program.keyword": program_type}}
                            ],
                            "must": [
                                {
                                    "match": {
                                        "content": {
                                            "query": search_query,
                                            "analyzer": "german",
                                            "fuzziness": "AUTO" if search_mode == "Fuzziness" else "0"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }

                # Execute the query
                response = client.search(index="slenert", body=query)

                # Display the search results
                st.subheader("Ergebnisse")
                hits = response["hits"]["hits"]
                for hit in hits:
                    score = hit["_score"]
                    content = hit["_source"]["content"]
                    response_element = hit["_source"]
                    st.write("Score:", score)
                    st.write("Content:", content)
                    st.json(response_element, expanded=False)
                    st.markdown("---")
                if len(hits) == 0:
                    st.write("Keine Ergebnisse gefunden")
