import re
import os
import json

markdown_content = """
    # Review

    ## Summary

    ## Soundness

    ## Presentation

    ## Contribution

    ## Strengths

    ## Weaknesses

    ## Rating

    ## Questions

    ## Suggestions, Ideas, and Comments

    ## Limitations

    ## Ethics Review

    ## Confidence

    """

system = "You are an AI journal conference reviewer from openreview. Review the following paper's abstract and provide feedback."
instruction = "You are an AI journal conference reviewer from openreview. You need to read the abstract of a " \
                "paper and then review the paper as a reviewer " \
                "to give a rating on the IDEA or other metrics. You need to grade like a real reviewer as follows MarkDown " \
                "format:\n" \
                + markdown_content + \
                "Review the following paper's abstract and provide feedback.\n" \
                "[Abstract]:\n"


def clean_sentence(sentence):
    # Remove tab characters
    sentence = sentence.replace('\t', ' ')

    # Allow Markdown syntax characters and remove any other character that is not a letter, digit, punctuation, or whitespace
    sentence = re.sub(r'[^\w\s\d.,!?;:()#\[\]_\-*/]', '', sentence)

    # Replace multiple spaces with a single space
    sentence = re.sub(r'\s+', ' ', sentence)

    # Strip leading and trailing whitespace
    sentence = sentence.strip()

    return sentence


def clean_markdown_content(content):
    cleaned_content = []
    for line in content.split('\n'):
        cleaned_content.append(clean_sentence(line))
    return '\n'.join(cleaned_content)


def traverse_folders_and_process(root_folder_path):
    formatted_data = []
    count = 0
    for folder_name in os.listdir(root_folder_path):
        folder_path = os.path.join(root_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    processed_count, processed_data = process_json_file(
                        file_path)
                    count += processed_count
                    formatted_data.extend(processed_data)
    with open('formatted_reviews.json', 'w', encoding='utf-8') as outfile:
        json.dump(formatted_data, outfile, indent=2, ensure_ascii=False)
    print(
        f"Processed {count} JSON files and saved the formatted data to 'formatted_reviews.json'."
    )


def process_json_file(json_file_path):
    count = 0
    formatted_data = []
    with open(json_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        data = json.load(file)

    abstract = data['content']['abstract']

    for review in data['details']['replies']:
        review_content = ""
        sections = review['content'].keys()
        expected_keys = [
            "summary", "soundness", "presentation", "contribution",
            'strengths', 'weaknesses', 'questions', 'limitations', 'rating',
            'confidence'
        ]
        if len(set(expected_keys).intersection(set(sections))) > 0:
            pass
        else:
            print('Skipping review with missing keys!')
            continue

        for section in sections:
            if section != 'flag_for_ethics_review' and section != 'code_of_conduct':
                review_content += f"## {section.capitalize()}\n{review['content'][section]}\n\n"

        review_content = clean_markdown_content(review_content)

        entry = {
            "instruction": instruction,
            "input": abstract,
            "output": review_content.strip(),
            "system": system,
            "history": []
        }

        formatted_data.append(entry)
        count += 1
        print('Added review!')

    return count, formatted_data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--root_folder_path',
        type=str,
        default='NeurIPS.cc_2021_Conference',
        help='Path to the root folder containing the JSON files.')
    args = parser.parse_args()
    root_folder_path = './raw_data/{}'.format(args.root_folder_path)
    traverse_folders_and_process(root_folder_path)
