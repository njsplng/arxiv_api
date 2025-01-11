import xml.etree.ElementTree as ET
import requests
import time
import datetime

########## Setting parameters for the query
base_url = "http://export.arxiv.org/api/query?"  # Base URL for the API. Do not change

query_keywords = [
    "fracture",
    "phase-field",
    "phase field",
    "variational energy",
    "computational mechanics",
    "brittle fracture",
]  # Keywords to search for

researchers_of_interest = [
    "Somdatta Goswami",
    "George em Karniadakis",
    "Laura de Lorenzis",
]  # Researchers of interest (will get parsed as keywords too)

query_settings = {
    "max_results": 20,  # 2000 is the maximum number of results that can be returned
    "start": 0,  # Start from the first results
    "sortBy": "submittedDate",  # Sort by date
    "sortOrder": "descending",  # Get the newest results first
}

request_delay = (
    3  # ArXiv asks for a delay of 3 seconds between requests. It's up to you to be nice
)

filter_keywords = [
    "deep operator",
    "deeponet",
    "neural operator",
    "physics informed",
    "physics-informed",
    "neural network",
    "PINN",
    "operator networks",
]  # Keywords which must be present in the title or abstract

date_offset = -30  # Number of days to look back

output_filename = "output.md"  # Output filename


########## Define helper functions
def xml_to_dict(xml_text):
    root = ET.fromstring(xml_text)
    entries = []

    # Define namespaces for easier tag lookup
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    for entry in root.findall("atom:entry", ns):
        entry_dict = {}

        ## Initialize lists for fields that can have multiple entries
        multi_fields = {
            "author": [],
            "link": [],
            "category": [],
            "primary_category": [],
        }

        for child in entry:
            ## Extract tag without namespace
            tag = child.tag.split("}")[-1]

            ## Special handling for authors
            if tag == "author":
                name_elem = child.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    name_text = (
                        name_elem.text.replace("\n ", "").replace("\n", " ").strip()
                    )
                    multi_fields["author"].append(name_text)
            ## Handling for elements expected to have attributes (and possibly text)
            elif tag in ["link", "category", "primary_category"]:
                ## Store attribute dictionaries; include text if available
                data = child.attrib.copy()
                if child.text and child.text.strip():
                    data["text"] = (
                        child.text.replace("\n ", "").replace("\n", " ").strip()
                    )
                multi_fields[tag].append(data)
            else:
                ## Default handling for other tags: store text content
                text = child.text or ""
                text = text.replace("\n ", "").replace("\n", " ").strip()
                entry_dict[tag] = text

        ## After processing all children, add multi-field lists to entry_dict if they were populated
        for field, values in multi_fields.items():
            if values:  # Only add if list is not empty
                entry_dict[field] = values

        entries.append(entry_dict)

    return entries


def filter_unique_entries(entries):
    unique_entries = []
    seen_ids = set()
    for entry in entries:
        entry_id = entry.get("id")
        if entry_id and entry_id not in seen_ids:
            seen_ids.add(entry_id)
            unique_entries.append(entry)
    return unique_entries


def dict_to_output_text(entries):
    output_text = ""
    for entry in entries:
        title = entry.get("title")
        authors = entry.get("author")
        summary = entry.get("summary")
        updated_date = entry.get("updated")
        link = entry.get("link")
        if title:
            output_text += f"**Title**: {title}\n"
        if authors:
            output_text += f"**Authors**: {', '.join(authors)}\n"
        if summary:
            output_text += f"**Summary**: {summary}\n"
        if updated_date:
            output_text += f"**Published**: {updated_date}\n"
        if link:
            output_text += f"**Link**: {link[0]["href"]}\n"
        output_text += "\n"
    return output_text


########## Execute query and filtering
## Form query string
query_setting_string = "&".join(
    [f"{key}={value}" for key, value in query_settings.items()]
)

## Retrieve results
retrieved_results = []
for keyword in query_keywords + researchers_of_interest:
    ## Form query URL
    query_url = f'{base_url}{query_setting_string}&search_query=all:"{keyword}"'

    ## Retrieve data
    data = requests.get(query_url)

    ## Parse to dict
    entries = xml_to_dict(data.text)

    ## Aggregate
    retrieved_results += entries

    ## Time out to be nice
    time.sleep(request_delay)

## Filter results
filtered_results = []
for entry in retrieved_results:
    ## Check for date compatibility first
    if datetime.datetime.strptime(
        entry.get("updated", ""), "%Y-%m-%dT%H:%M:%SZ"
    ) < datetime.datetime.now() + datetime.timedelta(days=date_offset):
        continue

    ## Filter by keywords
    for filter_keyword in filter_keywords:
        if (
            filter_keyword.lower() in entry.get("title", "").lower()
            or filter_keyword.lower() in entry.get("summary", "").lower()
        ):
            filtered_results.append(entry)
            break

## Remove duplicates
filtered_results = filter_unique_entries(filtered_results)

## Convert to output text
output_text = dict_to_output_text(filtered_results)

## Write to file
with open(output_filename, "w") as f:
    f.write(output_text)
