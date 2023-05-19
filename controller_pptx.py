import openai
from pptx import Presentation
import json

import logging
logging.basicConfig(level=logging.INFO, filename="app.log")

prompt_ppt = """
For every scenario I provide, I need at detailed response in a json format. Be critical and provide accurate facts and figures.

Here's a sample json body I want:

{
  "title": "Main Title",
  "subtitle": "Sub Heading"
  "slides": [
    {
      "id": 1,
      "title": "Title of Slide 1",
      "content": [
        {
          "type": "text",
          "value": "Some text on slide 1"
        },
        {
          "type": "bullet_points",
          "value": ["Bullet point 1", "Bullet point 2", "Bullet point 3"]
        }
      ]
    }
  ]
}

There should be only one slide title, one subheading, and multiple slides. The first slide should always be the Agenda slide.
The second slide should contain a brief history of the topic and an introduction. The last slide should be the conclusion slide.
Generate slides with a mix of both text and bullet points.
"""

def get_response(prompt, user, key):
    try: 
        print("Called response from pptx")
        openai.api_key = key
        resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
          ],
        max_tokens=3500,
        temperature=0
        )
        print("Showing response from pptx")
        print(resp)
    except Exception as e:
        logging.error(str(e))
        print("API error")
        pass
    
    # turbo ChatCompletion resp
    return resp.to_dict()["choices"][0]["message"]["content"].replace("\n", "").strip()


def create_pptx_from_json(json_text, filename):
    # Load the JSON
    data = json.loads(json_text)

    # Initialize the PowerPoint presentation
    prs = Presentation("./init_template.pptx")

    # Add the title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    title.text = data['title']
    subtitle = slide.placeholders[1]
    subtitle.text = data['subtitle']

    # Add the remaining slides
    for slide_data in data['slides']:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = slide_data['title']
        for content_data in slide_data['content']:
            if content_data['type'] == 'text':
                tf = slide.shapes.placeholders[1].text_frame
                p = tf.add_paragraph()
                p.text = content_data['value']
                p.level = 0
            elif content_data['type'] == 'bullet_points':
                tf = slide.shapes.placeholders[1].text_frame
                for point in content_data['value']:
                    p = tf.add_paragraph()
                    p.text = point
                    p.level = 1

    # Save the PowerPoint presentation
    prs.save(filename+".pptx")


def generate_pptx(prompt, user, key, filename):
    
    user = "Scenario: "+user
    print(user)
    # Get the response from the GPT-3 model
    print("Generating PowerPoint presentation...")
    resp = get_response(prompt_ppt, user, key)
    print("Done!")
    print(resp)
    
    # Create the PowerPoint presentation
    print("Creating PowerPoint presentation...LOL")
    create_pptx_from_json(resp, filename)
    print("PowerPoint presentation saved as "+filename+".pptx")