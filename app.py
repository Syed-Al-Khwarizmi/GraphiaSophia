import logging
logging.info("Importing libraries")
import re
import time
import concurrent.futures
import streamlit as st
import streamlit.components.v1 as components
from controller import generate_net, prompt


print(st.__version__)
# Define a function to execute generate_net() in a separate thread
def generate_net_thread(prompt, user_input, openai_api_key):
    return generate_net(prompt=prompt, user=user_input, key=openai_api_key)


print(prompt)

logging.basicConfig(level=logging.INFO, filename="app.log")

logging.info("Starting app.py")
# Expand the default container width
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
    st.title("Mind The Map")
    
    # Create input fields for user input and OpenAI API key
    # st.sidebar.title("Input")
    user_input = st.sidebar.text_area("Enter your text here", max_chars=250)
    openai_api_key = st.sidebar.text_input("Enter your OpenAI API key here")
    
    # Create a container for the input and button
    input_col, button_col = st.columns([4, 1])
    with input_col:
        hide_input_label_css = """
            <style>
            div[data-testid="stText"][role="textbox"] > label {visibility: hidden;}
            </style>
            """
        st.markdown(hide_input_label_css, unsafe_allow_html=True)
    with button_col:
            # st.write("") # Add some empty space
            # st.write("") # Add some empty space
            generate_button = st.sidebar.button("Generate")

    # Call generate_net() function when Generate button is clicked
    if generate_button:
        # Add data validation to the input fields.
        # If the input fields are empty, show an error message
        if not user_input:
            st.error("Please enter your text")
        if not openai_api_key:
            st.error("Please enter your OpenAI API key")
        if not user_input or not openai_api_key:
            st.stop()

        bar_texts = ["Sent stuff to GPT...", "GPT making some cool decisions...", "Creating relationships...", "Generating graph..."]
        logging.info("Generating graph")
        progress_bar = st.progress(0, text="Generating graph...")
        start_time = time.time()
        time_limit = 30  # Set the time limit in seconds
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(generate_net_thread, prompt, user_input, openai_api_key)
            while time.time() - start_time < time_limit and not future.done():
                # Update the progress bar every second
                progress = (time.time() - start_time) / time_limit
                # Update the progress bar after every percentage of the time elapses
                if progress > 0.05 and progress < 0.15:
                    progress_bar.progress(int(progress * 100), text=bar_texts[0])
                elif progress > 0.15 and progress < 0.65:
                    progress_bar.progress(int(progress * 100), text=bar_texts[1])
                elif progress > 0.65 and progress < 0.85:
                    progress_bar.progress(int(progress * 100), text=bar_texts[2])
                elif progress > 0.85 and progress < 0.95:
                    progress_bar.progress(int(progress * 100), text=bar_texts[3])
                # reduce the sleep time if time elapsed is more than 90% of the time limit
                if time.time() - start_time > time_limit * 0.9:
                    time.sleep(0.1)
                else:
                    time.sleep(1)
            progress_bar.empty()
            text, nodes = future.result()
            # Update text based on words in DataFrame
            for name, color in zip(nodes['Name'], nodes['Color']):
                # Create a regex pattern that matches the word with the original capitalization
                pattern = r'\b{}\b'.format(re.escape(name))
                # Replace the matched word with the colored word
                text = re.sub(pattern, f'<span style="color:{color}">{name}</span>', text, flags=re.IGNORECASE)
            logging.info("Graph generated")
            # st.sidebar.title("Output")
            text_output = st.sidebar.empty()
            text_output.markdown("## Description for " + user_input)
            text_output.markdown(text, unsafe_allow_html=True)

    # Hide the Streamlit menu and footer to maximize white space
    # hide_menu_footer_css = """
    #     <style>
    #     #MainMenu, footer {visibility: hidden;}
    #     </style>
    #     """
    # st.markdown(hide_menu_footer_css, unsafe_allow_html=True)

# Open the experiment.html file in the HtmlFile variable and add it to the components.html
with open("experiment.html", "r") as HtmlFile:
    source_code = HtmlFile.read()
    html_url = "./experiment.html"
    components.html(source_code, scrolling=False, height=650)