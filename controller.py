import openai
import json
import pandas as pd
import logging
import os
import hashlib
from io import StringIO
import re
import random
from pyvis.network import Network

logging.basicConfig(level=logging.INFO, filename="app.log")

# # Read the openai key from the secrets.env file and store it in the openai.api_key variable
# with open('secrets.env') as f:
#     openai.api_key = f.readline()

# Define the cache directory
cache_dir = "cache"

# def get_prompt(n_nodes = 10):
#     json_format = """{
#                 "Response": {
#                     "Nodes": [{field: value}],
#                     "Edges": [[field: value]],
#                     "Text": "The explanation, converted to a markdown bullet list format. All newline characters should be removed."
#                 }
#             }
#             """
#     prompt = """
#             Please provide a JSON response for each scenario, containing a network graph with nodes and edges.

#             Each node should have the following fields:
#             - Name: The name of the entity
#             - Color: A random dark, web-friendly color in hex format
#             I need at least {} nodes.

#             Each edge should have the following fields:
#             - Source: The name of the source node.
#             - Destination: The name of the destination node.
#             - Label: A text label that describes the relationship between the two nodes.

#             Text: A markdown bullet format conversion of the explanation of all nodes in the following format:
#             ### Heading
#             - **Subheading**: List of detailed explained bullet points

#             Nodes and edges should be connected to form a network graph. The generated graph should have the maximum number of edges between the nodes.

#             The JSON should be formatted as follows:
#             {}
#             Only return JSON object.
#         """.format(n_nodes, json_format)
#     return prompt


def get_prompt(n_nodes = 10):
    out_format = """{
                "Response": {
                    "Graph": csv data,
                    "Text": A markdown bullet format conversion of the explanation of all nodes in the following format:
                        ### Heading
                        - **Subheading**: List of detailed explained bullet points
                }
            }
            """
    prompt = """
            For every scenario I provide, you'll provide me a response in a csv format and a markdown text enclosed within a json object.
            The csv format should have the following columns:
            Source, Destination, Label.
            Source should be the source entity. Destination should be a destination entity, and Relation should be a small text that explains how the two entities are related. 
            I need exactly {} csv rows. Not more than {} rows should be returned.
            The output format should be:
            {}
        """.format(n_nodes, n_nodes, out_format)
    return prompt.strip()

def get_jsons(prompt, user, key):
    try:   
        openai.api_key = key
        resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": get_prompt()},
                {"role": "user", "content": user},
          ],
        max_tokens=3500,
        temperature=0
        )
    except Exception as e:
        logging.error(str(e))
        logging.info("API error")
        pass
    
    # turbo ChatCompletion resp
    return resp.to_dict()["choices"][0]["message"]["content"].replace("\n", "").strip()



#Dataframe to net
def df_to_net(df_nodes, df_edges):
    net = Network("600px", "100%", directed=True, notebook=False)
    
    # Check if source or destination text is missing in nodes DataFrame
    missing_nodes = set(df_edges['Source'].unique()) | set(df_edges['Destination'].unique()) - set(df_nodes['Name'].unique())
    logging.info(missing_nodes)
    # Create a DataFrame for the missing nodes
    missing_nodes_df = pd.DataFrame({
        'Name': list(missing_nodes),
        # 'Text': list(missing_nodes),
        'Color': df_nodes['Color'].sample(n=len(missing_nodes), replace=True).reset_index(drop=True),
        'Shape': 'dot'
    })
    logging.info("Missing Nodes")
    logging.info(missing_nodes_df)
    # Concatenate existing nodes DataFrame with missing nodes DataFrame
    df_nodes = pd.concat([df_nodes, missing_nodes_df], ignore_index=True)
    logging.info("New nodes df after adding missing nodes")
    logging.info(df_nodes)


    for n in df_nodes.iterrows():
        net.add_node(
            n_id = n[1]['Name'], 
            label = n[1]['Name'], 
            color = n[1]['Color'],
            shape = n[1]['Shape'],
            # title = n[1]['Text'],
            physics = False,
        )

    for e in df_edges.iterrows():
        net.add_edge(
            arrowStrikethrough = False,
            source = e[1]['Source'],
            to = e[1]['Destination'],
            title = e[1]['Label'],
            physics = True
        )
    return net


def generate_net(prompt, user, key):
    node_shape = "dot"
    # Default text, nodes and edges:
    text = "Uh oh! Something went wrong! Please try again or modify the input a bit."
    nodes = pd.DataFrame(
        {
            "Name": ["Uh Oh!"],
            "Text": ["Something went wrong!"],
            "Color": ["#FCFCFC"],
            "Shape": ["dot"],
        }
    )

    edges = pd.DataFrame(
        {
            "Source": ["Uh Oh!"],
            "Destination": ["Uh Oh!"],
            "Label": ["Wanna give it another shot?"],
        }
    )

    net = df_to_net(nodes, edges)
    # # Saving default net
    # net = Network("600px", "100%", directed=True, notebook=False)
    # for n in nodes.iterrows():
    #     net.add_node(
    #         n_id = n[1]['Name'], 
    #         label = n[1]['Name'], 
    #         color = n[1]['Color'],
    #         shape = n[1]['Shape'],
    #         title = n[1]['Text'],
    #         physics = False,
    #     )

    # for e in edges.iterrows():
    #     net.add_edge(
    #         arrowStrikethrough = False,
    #         source = e[1]['Source'],
    #         to = e[1]['Destination'],
    #         title = e[1]['Label'],
    #         physics = True
    #     )

    # net.save_graph("experiment.html")
    # Generate a unique filename based on user information
    user_hash = hashlib.md5(user.encode()).hexdigest()
    logging.info("Default Saving with user: " + user)
    logging.info("Default Saving with hash: " + user_hash)
    filename = f"experiment_{user_hash}.html"
    cache_file = os.path.join(cache_dir, filename)
    net.save_graph(cache_file)

    logging.info("User input: " + user)
#     try:

    print(prompt, user)
    jsons = get_jsons(prompt=prompt, user=user, key=key)
    logging.info(jsons)
    # logging.info(prompt, user)

    match = re.search(r'\{.*\}', jsons)
    jsons = match.group(0)
    # nodes = pd.read_json(json.dumps(json.loads(jsons)['Response']['Nodes']))
    # nodes['Shape'] = node_shape
    # edges = pd.read_json(json.dumps(json.loads(jsons)['Response']['Edges']))
    # text = json.loads(jsons)['Response']['Text']
    print(jsons)
    print(type(jsons))
    
    jsons = json.loads(jsons)
    print(jsons)
    print(type(jsons))
    
    edges = pd.read_csv(StringIO(jsons['Response']['Graph']))
    text = jsons['Response']['Text']
#     edges = pd.read_json(json.loads(jsons)['Response']['Graph'])
#     text = json.loads(jsons)['Text']

    # Apply strip to all columns in the DataFrame
    edges = edges.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    # Assuming you have a pandas DataFrame called df
    edges = edges.rename(columns=lambda x: x.strip())

    print("**************************\nEdges: \n{}".format(edges))
    print("**************************\nEdges: \n{}".format(edges.columns))
    print("**************************\nText: \n{}".format(text))

    # logging.info("**************************\nEdges: \n{}".format(edges))
    # logging.info("**************************\nText: \n{}".format(text))

    color_ref = [
        "#40E0D0", "#DE3163", "#FF7F50", "#FFBF00", "#6495ED", "#CD7F3", "#7393B3", "#228B22", "#009E60", "#CC5500",
        "#FF5F1F", "#E30B5C", "#E37383", "#5D3FD3", "#FFD700"
    ]

    # Assuming you have a pandas DataFrame called df
    unique_values = pd.concat([edges['Source'], edges['Destination']]).unique().tolist()
    data = {'Name': unique_values, 'Color': random.sample(color_ref, len(unique_values))}
    nodes = pd.DataFrame(data)
    nodes['Shape'] = node_shape

    # nodes = pd.read_json(json.dumps(json.loads(jsons)['nodes']))
    # nodes['Shape'] = node_shape
    # edges = pd.read_json(json.dumps(json.loads(jsons)['edges']))
#     text = json.loads(jsons)['text']

#     except Exception as e:
#         logging.error(str(e))
#         logging.info(e)
#         logging.info("JSON error")
#         pass
  
    
    logging.info(nodes)
    logging.info(edges)

#     try:
    net = df_to_net(nodes, edges)
#     except Exception as e:
#         logging.error(str(e))
#         logging.info("Graph error")
#         pass

    # net.show_buttons(filter_=['physics'])
    # net.save_graph("experiment.html")

    user_hash = hashlib.md5(user.encode()).hexdigest()
    logging.info("Saving with user: " + user)
    logging.info("Saving with hash: " + user_hash)
    filename = f"experiment_{user_hash}.html"
    cache_file = os.path.join(cache_dir, filename)
    net.save_graph(cache_file)
    # Disable node physics
    # Originally, node physics are enabled so that nodes are rendered in a structured format.
    # Later, node physics are disabled so that nodes can be dragged around.
    # net.toggle_physics(False)
    # net.save_graph("experiment.html")
    return text, nodes

if __name__ == "__main__":
    generate_net(prompt=prompt, user="")


