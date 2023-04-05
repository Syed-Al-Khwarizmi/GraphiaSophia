import openai
import json
import pandas as pd
import logging
import re
from pyvis.network import Network

logging.basicConfig(level=logging.INFO, filename="app.log")

# # Read the openai key from the secrets.env file and store it in the openai.api_key variable
# with open('secrets.env') as f:
#     openai.api_key = f.readline()

prompt = """
    For every scenario I provide, I need a json format response. The response should be a network graph with nodes and edges.
    Nodes have the fields: Name, Text, Color, Shape.
    Edges have the fields: Source, Destination, Label

    A Node contains: 
    Name: The actual name of the entity.
    Text: A small description of the node.
    Color: A web friendly light color in hex format, based on the context.
    
    An Edge contains:
    Source: Name of the source Node.
    Destination: Name of the destination Node
    Label: Shows a text relation between the two nodes.

    Text: A markdown bullet format conversion of the explanation in the following format:
    ### Heading
    - **Subheading**: List of detailed explanaied bullet points
    
    Both Source and Destinations MUST be in the Nodes list.
    I need at least 10 nodes.
    
    The message content should follow the format:
    {
        "Response": {
            "Nodes": [{field: value}],
            "Edges": [[field: value]],
            "Text": "Explanation converted into markdown bullet list format"
        }
    }
    Only return json objects and text. Every node must be connected to a node through an edge.
    
"""

def get_jsons(prompt, user, key):
    try:   
        openai.api_key = key
        resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
          ],
        max_tokens=3500,
        temperature=0
        )
    except Exception as e:
        logging.error(str(e))
        print("API error")
        pass
    
    # turbo ChatCompletion resp
    return resp.to_dict()["choices"][0]["message"]["content"].replace("\n", "").strip()


def generate_net(prompt, user, key):
    node_shape = "dot"
    user = "Scenario: "+user
    # Default nodes and edges:
    nodes = pd.DataFrame(
        {
            "Name": ["Uh Oh!"],
            "Text": ["Something went wrong!"],
            "Color": ["#FCFCFC"],
            "Shape": ["ellipse"],
        }
    )

    edges = pd.DataFrame(
        {
            "Source": ["Uh Oh!"],
            "Destination": ["Uh Oh!"],
            "Label": ["Wanna give it another shot?"],
        }
    )

    # Saving default net
    net = Network("700px", "1200px", directed=True, notebook=False)
    for n in nodes.iterrows():
        net.add_node(
            n_id = n[1]['Name'], 
            label = n[1]['Name'], 
            color = n[1]['Color'],
            shape = n[1]['Shape'],
            title = n[1]['Text'],
            physics = False,
        )

    for e in edges.iterrows():
        net.add_edge(
            arrowStrikethrough = False,
            source = e[1]['Source'],
            to = e[1]['Destination'],
            title = e[1]['Label'],
            physics = True
        )

    net.save_graph("experiment.html")

    logging.info("User input: " + user)
    try:
        jsons = get_jsons(prompt=prompt, user=user, key=key)
        print(jsons)
        print(prompt, user)

        match = re.search(r'\{.*\}', jsons)
        jsons = match.group(0)
        nodes = pd.read_json(json.dumps(json.loads(jsons)['Response']['Nodes']))
        nodes['Shape'] = node_shape
        edges = pd.read_json(json.dumps(json.loads(jsons)['Response']['Edges']))
        text = json.loads(jsons)['Response']['Text']

    except Exception as e:
        logging.error(str(e))
        print(e)
        print("JSON error")
        pass
  
    
    logging.info(nodes)
    logging.info(edges)

    try:
        net = Network("700px", "1200px", directed=True, notebook=False)
        net.repulsion(node_distance=120, central_gravity=0.011, spring_length=120, damping=0.2)
        # net.show_buttons(filter_=['physics'])
        for n in nodes.iterrows():
            net.add_node(
                n_id = n[1]['Name'], 
                label = n[1]['Name'], 
                color = n[1]['Color'],
                shape = n[1]['Shape'],
                title = n[1]['Text'],
                physics = False,
            )

        for e in edges.iterrows():
            net.add_edge(
                arrowStrikethrough = False,
                source = e[1]['Source'],
                to = e[1]['Destination'],
                title = e[1]['Label'],
        #         value = e[1]['Weight'],
                physics = True
            )
    except Exception as e:
        logging.error(str(e))
        print("Graph error")
        pass
    net.save_graph("experiment.html")
    return text

if __name__ == "__main__":
    generate_net(prompt=prompt, user="")


