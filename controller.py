import openai
import json
import pandas as pd
import logging
import re
from pyvis.network import Network

logging.basicConfig(level=logging.INFO, filename="app.log")
logging.basicConfig(level=logging.WARNING, filename="app.log")
logging.basicConfig(level=logging.ERROR, filename="app.log")

# Read the openai key from the secrets.env file and store it in the openai.api_key variable
with open('secrets.env') as f:
    openai.api_key = f.readline()

prompt = """
        Nodes have: Name, Text, Color, Shape.
        Edges have: Source, Destination, Label.

        A Node contains: 
        - Name: actual entity name.
        - Text: small node description.
        - Color: web-friendly light hex color based on context.
            
        An Edge contains:
        - Source: Name of the source Node.
        - Destination: Name of the destination Node.
        - Label: Text relation between the two nodes.

        Markdown bullet format:
        ### Heading
        - **Subheading**: detailed explanation bullet points
            
        Requirements:
        - Both Source and Destination MUST be in the Nodes list.
        - At least 10 nodes are required.
        - All nodes must be connected through an edge.

        JSON format:
        {
            "Response": {
                "Nodes": [{field: value}],
                "Edges": [{field: value}],
                "Text": "Explanation converted to markdown bullet list format"
            }
        }
    
"""

def get_jsons(prompt, user):
    try:   
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


def generate_net(prompt, user):
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
    # net.repulsion(node_distance=150, central_gravity=0.4, spring_length=250, damping=0.5)
    # net.show_buttons(filter_=['physics'])
    for n in nodes.iterrows():
    #     shape = "square"
    #     if n[1]["Shape"] == "square":
    #         shape = "circle"
        net.add_node(
    #         shape = shape,
            n_id = n[1]['Name'], 
            label = n[1]['Name'], 
    #         value = n[1]['Node Value'], 
    #         group = n[1]['Node Portfolio'], 
            color = n[1]['Color'],
            shape = n[1]['Shape'],
            title = n[1]['Text'],
            physics = False,
    #         level = n[1]['Node Value'],
    #         mass = n[1]['Node Value']
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

    # customize the styles for #network and #config elements
    # net.set_options("""
    #     #network {
    #         "height": 100%,
    #         "width": 100%,
    #         "background-color": #ffffff,
    #         "position": relative,
    #         "float": left,
    #     }
    #     #config {
    #         "float": left,
    #         "width": 100%,
    #         "height": 100%
    #     }
    # """)
    net.save_graph("experiment.html")

    logging.info("User input: " + user)
    try:
        jsons = get_jsons(prompt=prompt, user=user)
        print(jsons)
        print(prompt, user)

        # # Split the string into two parts using "Edges:" as a delimiter
        # nodes_str, edges_str = jsons.split('Edges:')

        # # Convert the nodes string into a dictionary
        # nodes_dict = json.loads(nodes_str.replace('Nodes:', '').strip())

        # # Convert the edges string into a dictionary
        # edges_dict = json.loads(edges_str.strip())

        # # Convert the nodes dictionary into a dataframe
        # nodes = pd.read_json(
        # json.dumps(nodes_dict)
        # )
        # nodes['Node Shape'] = node_shape

        # edges = pd.read_json(
        #     json.dumps(edges_dict)
        # )
        #
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
        #     shape = "square"
        #     if n[1]["Shape"] == "square":
        #         shape = "circle"
            net.add_node(
        #         shape = shape,
                n_id = n[1]['Name'], 
                label = n[1]['Name'], 
        #         value = n[1]['Node Value'], 
        #         group = n[1]['Node Portfolio'], 
                color = n[1]['Color'],
                shape = n[1]['Shape'],
                title = n[1]['Text'],
                physics = False,
        #         level = n[1]['Node Value'],
        #         mass = n[1]['Node Value']
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
    # customize the styles for #network and #config elements
    # net.set_options("""
    #     #network {
    #         "height": 100%,
    #         "width": 100%,
    #         "background-color": #ffffff,
    #         "position": relative,
    #         "float": left
    #     },
    #     #config {
    #         "float": left,
    #         "width": 100%,
    #         "height": 100%,
    #     }
    # """)
    # print(net.get_options())
    net.save_graph("experiment.html")
    return text

if __name__ == "__main__":
    generate_net(prompt=prompt, user="")


