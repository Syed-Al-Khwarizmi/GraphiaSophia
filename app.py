import logging
import re
import io
import os
import hashlib
import time
import base64
import shutil
import threading
import concurrent.futures
import streamlit as st
import streamlit.components.v1 as components

from controller import generate_net, get_prompt
from controller_pptx import generate_pptx, prompt_ppt


class GraphiaSophia:
    def __init__(self):
        self.logging = logging
        self.re = re
        self.io = io
        self.time = time
        self.base64 = base64
        self.concurrent = concurrent.futures
        self.streamlit = st
        self.streamlit_components = components
        self.controller = generate_net
        self.controller_pptx = generate_pptx
        self.text = ""
        # Create a cache directory, don't use the absolute path
        self.cache_dir = os.path.join(".", "cache")

    def display_text(self, text):
        st.sidebar.markdown(self.text, unsafe_allow_html=True)
    
    def clear_cache_directory(self):
        current_time = time.time()
        expiration_time = 900  # 15 minutes in seconds

        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            try:
                if os.path.isfile(file_path):
                    file_creation_time = os.path.getctime(file_path)
                    if current_time - file_creation_time >= expiration_time:
                        os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {str(e)}")


    def run(self):
        # Create a cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        # Start the background thread to clear the cache directory
        clear_cache_thread = threading.Thread(target=self.clear_cache_directory)
        clear_cache_thread.start()
        # Set the page configuration
        st.set_page_config(layout="wide")
        with st.container():
            # Add CSS styles to adjust margins and padding
            st.markdown("""
                <style>
                .stApp {
                    margin-top: -90px;
                }
                .stApp > div:first-child {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
                </style>
            """, unsafe_allow_html=True)
        st.title("GraphiaSophia")

        # # Create a text input field where users can enter text.
        # user_input = st.text_area("Enter your text here", max_chars=350)
        # # Create a number selector for the node count
        # node_count = st.number_input(
        #     "Select the number of nodes (5-20)",
        #     min_value=5,
        #     max_value=20,
        #     value=10,
        #     step=1
        # )

        # Create a two-column layout
        col1, col2 = st.columns([2, 1])

        # Create a text input field where users can enter text.
        user_input = col1.text_area("Enter your text here", max_chars=350, height=128)

        # Create a number selector for the node count
        with col2:
            node_count = col2.number_input(
            "Select the number of nodes (5-20)",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )

        # Create a dropdown for the education level
        with col2:
            complexity_level = col2.selectbox(
            "Select your complexity level",
            options=["1st Grader", "5th Grader", "Middle Schooler", "High Schooler", "Graduate Level", "Postgraduate Level"]
        )

        # Create a text input field for the OpenAI API key.
        openai_api_key = st.sidebar.text_input("Enter your OpenAI API key here", type="password")

        gen_button, gen_ppt_button = st.sidebar.columns([1, 1])
        with gen_button:
            generate_button = st.button("Generate Map", key="generate_button")

        with gen_ppt_button:
            generate_pptx_button = st.button("Generate PPT", key="generate_pptx_button")

        # Call generate_net() function when Generate button is clicked.
        if generate_button:
            # Add data validation to the input fields.
            # If the input fields are empty, show an error message
            if not user_input:
                st.error("Please enter your text")
            if not openai_api_key:
                st.error("Please enter your OpenAI API key")

            # Concatenate complxiety level with user input
            user_input = f"Scenario: {user_input}. Explain to me as if I'm a {complexity_level}."
            # Call generate_net() function.
            self.text, nodes= self.controller(prompt=get_prompt(n_nodes=node_count), user=user_input, key=openai_api_key)

            # Update text based on words in DataFrame
            for name, color in zip(nodes['Name'], nodes['Color']):
                # Create a regex pattern that matches the word with the original capitalization
                pattern = r'\b{}\b'.format(re.escape(name))
                # Replace the matched word with the colored word
                self.text = re.sub(pattern, f'<span style="color:{color}">{name}</span>', self.text, flags=re.IGNORECASE)

            # Display the text.
            print("THIS GETS SHOWN JUUUUUST FIIIINE!!!")
            print(self.text)
            self.display_text(self.text)

        # Call generate_pptx() function when Generate PPT button is clicked.
        if generate_pptx_button:
            # Add data validation to the input fields.
            # If the input fields are empty, show an error message
            filename = "MTM_Presentation"
            if not user_input:
                st.error("Please enter your text")
            if not openai_api_key:
                st.error("Please enter your OpenAI API key")
            
            # Concatenate complxiety level with user input
            user_input = f"Scenario: {user_input}. Explain to me as if I'm a {complexity_level}."
            # Call generate_pptx() function.
            self.display_text(self.text)
            self.controller_pptx(prompt=prompt_ppt, user=user_input, key=openai_api_key, filename=filename)
            # Convert pptx file to base64
            # Generate a unique filename based on user information
            user_hash = hashlib.md5(user_input.encode()).hexdigest()
            print("Saving with user: " + user_input)
            print("Saving with hash: " + user_hash)
            filename = f"presentation_{user_hash}.pptx"
            cache_file = os.path.join(self.cache_dir, filename)
            with open(f"{cache_file}", "rb") as file:
                file_b64 = base64.b64encode(file.read()).decode()


            # Encode the PPTX file to base64
            # file_b64 = base64.b64encode(pptx_file.read()).decode()

            # Generate the hyperlink to the PPTX file
            pptx_file_url = f"data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{file_b64}"
            pptx_file_link = f'<a href="{pptx_file_url}" target="_blank">Click here to download the PPTX file</a>'
            st.markdown(f'{pptx_file_link}', unsafe_allow_html=True)

        # Open the experiment.html file in the HtmlFile variable and add it to the components.html
        user_hash = hashlib.md5(user_input.encode()).hexdigest()
        filename = f"experiment_{user_hash}.html"
        cache_file = os.path.join(self.cache_dir, filename)
        print("Opening with user: " + user_input)
        print("cache_file: " + cache_file)
        # If not exists the cache_file, then cache_file = "experiment.html"
        if not os.path.exists(cache_file):
            cache_file = "./experiment.html"
        # Get the user's cookie value from the Streamlit request context
        with open(cache_file, "r") as HtmlFile:
            source_code = HtmlFile.read()
            components.html(source_code, scrolling=False, height=650)



if __name__ == "__main__":
    # Create an instance of the MindTheMap class.
    graphia_sophia = GraphiaSophia()

    # Run the web application.
    graphia_sophia.run()