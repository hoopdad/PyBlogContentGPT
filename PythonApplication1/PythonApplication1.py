import openai
import requests
import os
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Define the scope for the Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Set your OpenAI GPT-3 API key
openai.api_key = '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'

# Set your Blogger API key and blog ID
BLOGGER_API_KEY = 'AIzaSyDIfdKy0Fkv9muCl11axQDuVKahzGxxLYY'
BLOG_ID = '4009390686325870720'
blogger_url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/'
    
my_engine="gpt-3.5"
my_engine="gpt-3.5-turbo"
my_engine="text-davinci-002"
my_engine="gpt-3.5-turbo"
my_engine="gpt-4"
my_max_tokens=3000  # You can adjust this based on the desired length of the response

def authenticate_blogger():
    credentials = authenticate_with_google()
    #print("credentials")
    #print(credentials)

    headers = {
        'Authorization': f'Bearer {credentials.token}',
        'Content-Type': 'application/json'
    }
    return headers

# Function to authenticate with OAuth for a Google service
def authenticate_with_google():
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first time.
    creds = None

    # Load existing credentials from the file if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# Function to generate content using OpenAI GPT-3
def generate_content(actor, prompt):
    cntnt = ""
    if(my_engine=="text-davinci-002"):
        try:
            response = openai.Completion.create(
                engine=my_engine,
                prompt=prompt,
                max_tokens=my_max_tokens
            )
            cntnt =response.choices[0].text.strip()
        except openai.error.APIError as e:
            print(e)
            print(e.error.code)
            cntnt=generate_content(prompt)
    
    if(my_engine=="gpt-3.5-turbo" or my_engine=="gpt-3.5"):
        try:
            response = openai.ChatCompletion.create(
                model=my_engine,
                messages=[{"role":"system","content":actor},
                          {"role":"user","content":prompt}
                ])
            cntnt = response["choices"][0]["message"]["content"]
        except openai.error.APIError as e:
            print(e)
            print(e.error.code)
            cntnt=generate_content(prompt)

    if (my_engine=="gpt-4"):
        try:
            response = openai.ChatCompletion.create(
                model=my_engine,
                messages=[{"role":"system","content":actor},
                          {"role":"user","content":prompt}
                ])
            cntnt = response["choices"][0]["message"]["content"]
        except openai.error.APIError as e:
            print(e)
            cntnt = generate_content(prompt)
    
    cntnt = cleanup_content(cntnt)
    return cntnt

def cleanup_content(cntnt):
    try:
        indx = cntnt.index("<html>")
        if(indx>-1): cntnt = cntnt[(indx+len("<html>")):]
    except ValueError as e:
        print(e)
    
    try:
        indx = cntnt.index("</body>")
        if(indx>-1): cntnt = cntnt[:indx]
    except ValueError as e:
        print(e)
    
    return cntnt

# Function to create a new blog post on Blogger.com
def create_blog_post(title, content, labels):
    post_data = {
        'kind': 'blogger#post',
        'blog': {'id': BLOG_ID},
        'title': title,
        'content': content,
        'labels': labels
    }
    print(post_data)
    headers = authenticate_blogger()
    #print("****URL****")
    #print(url)
    #print("****Headers****")
    #print(headers)
    #print("****POST DATA****")
    #print(post_data)
    response = requests.post(blogger_url, headers=headers, json=post_data)

    if response.status_code == 200:
        post_id = response.json().get('id')
        return post_id
    else:
        print(f"Failed to create a blog post. Status Code: {response.status_code}")
        return None

# Function to publish a blog post on Blogger.com
def publish_blog_post(post_id):
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}/publish?key={BLOGGER_API_KEY}'

    headers = authenticate_blogger()

    #print("****URL****")
    #print(url)
    #print("****Headers****")
    #print(headers)
    #print("****POST_ID****")
    #print(post_id)

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("Blog post published successfully.")
    else:
        print(f"Failed to publish the blog post. Status Code: {response.status_code}")

# Main function to generate content and create/publish the blog post
def main():
    title=""
    actor=""
    labels="[]"
    prompt=""
    
    if(len(sys.argv)>1):
        actor=sys.argv[1]
    if(len(sys.argv)>2):
        # Title for the blog post
        title = sys.argv[2]
    if(len(sys.argv)>2):
        # Title for the blog post
        title = sys.argv[2]
    if(len(sys.argv)>3):
        # Title for the blog post
        labels = sys.argv[3]
       
    # Prompt for content generation
    if (title):
        prompt = "Generate a blog post in HTML syntax about "+title+", including sections for an overview, key uses and benefits, a path to expertise, links with HTML link syntax to popular sites with training materials, and links with HTML link syntax to sites with relevant certifications or products. Each section should use an HTML H2 section title and lists of links should use HTML UL. Include an Attribution section at the end that identifies this content as being created by ChatGPT and a human prompt engineer who has more than 25 years of experience in upskilling himself. Add keywords to help search engines find this post. Make sure to use HTML formatting as much as possible."
        prompt = "Generate a blog post in HTML syntax about "+title+", including sections for an overview, key uses and benefits, what to look for, what to watch out for, links with HTML link syntax to popular products, and who are customers of those products, . Each section should use an HTML H2 section title and lists of links should use HTML UL. Include an Attribution section at the end that identifies this content as being created by ChatGPT and a human prompt engineer who has more than 25 years of experience in upskilling himself. Add keywords to help search engines find this post. Make sure to use HTML formatting as much as possible."

    # Generate content using OpenAI GPT-3
    generated_content = generate_content(actor, prompt)

    # Combine the generated content with additional information
    full_content = f"{generated_content}"

    # Create and publish the blog post
    post_id = create_blog_post(title, full_content, labels)

    if post_id:
        # Publish the blog post
        publish_blog_post(post_id)

if __name__ == "__main__":
    main()

