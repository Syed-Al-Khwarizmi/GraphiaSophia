import logging
import re
import io
import time
import base64
import concurrent.futures
import streamlit as st
import streamlit.components.v1 as components

from controller import generate_net, prompt
from controller_pptx import generate_pptx, prompt_ppt



class MindTheMap:
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


    def display_text(self, text):
        st.sidebar.markdown(self.text, unsafe_allow_html=True)


    def run(self):
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
        st.title("Mind The Map")

        # Create a text input field where users can enter text.
        user_input = st.text_area("Enter your text here", max_chars=350)

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

            # Call generate_net() function.
            self.text, nodes = self.controller(prompt=prompt, user=user_input, key=openai_api_key)

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

            # Call generate_pptx() function.
            self.controller_pptx(prompt=prompt_ppt, user=user_input, key=openai_api_key, filename=filename)
            # Convert pptx file to base64
            with open(f"{filename}.pptx", "rb") as file:
                file_b64 = base64.b64encode(file.read()).decode()


            # Encode the PPTX file to base64
            # file_b64 = base64.b64encode(pptx_file.read()).decode()

            # Generate the hyperlink to the PPTX file
            pptx_file_url = f"data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{file_b64}"
            pptx_file_link = f'<a href="{pptx_file_url}" target="_blank">Click here to download the PPTX file</a>'
            st.markdown(f'{pptx_file_link}', unsafe_allow_html=True)

        # Open the experiment.html file in the HtmlFile variable and add it to the components.html
        with open("experiment.html", "r") as HtmlFile:
            source_code = HtmlFile.read()
            html_url = "./experiment.html"
            components.html(source_code, scrolling=False, height=650)


if __name__ == "__main__":
    # Create an instance of the MindTheMap class.
    mind_the_map = MindTheMap()

    # Run the web application.
    mind_the_map.run()