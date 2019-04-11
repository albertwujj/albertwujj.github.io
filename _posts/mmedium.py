import copy
import os
if __name__ == "__main__":
    post_url = input('Enter post url: ')
    # Title of post
    title = '-'.join(post_url.split('/')[-1].split('-')[:-1])
    date = input('Enter date (as 2018-10-05): ')
    # Read in the template
    with open('medium-to-markdown.js', 'r') as f:
        template = f.readlines()

    # Copy the template
    template_mod = copy.deepcopy(template)
    
    template_mod[2]=''
    # Update the js script with the url
    template_mod[2] = f'mediumToMarkdown.convertFromUrl("{post_url}")'

    # Write the new file
    with open('medium-to-markdown_mod.js', 'w') as f:
        f.writelines(template_mod)

    # Directory for saving post
    # File is automatically correctly named
    post_dir = f'{date}-{title}.md'

    # Run the new script
    r = os.system("node medium-to-markdown_mod.js >> %s" % post_dir)

    # If no errors, report save location
    if r == 0:
        print(f'Post saved as markdown to {post_dir}')
    else:
        print('Error somewhere along the way.')
