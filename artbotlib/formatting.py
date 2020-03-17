import re


def extract_plain_text(json_data):
    """
    Take data that looks like the following:

{'data': {'blocks': [{'block_id': 'a2J3',
                      'elements': [{'elements': [{'type': 'user',
                                                  'user_id': 'UTHKYT7FB'},
                                                 {'text': ' Which build of sdn '
                                                          'is in ',
                                                  'type': 'text'},
                                                 {'text': 'registry.svc.ci.openshift.org/ocp-s390x/release-s390x:4.4.0-0.nightly-s390
x-2020-02-21-235937',
                                                  'type': 'link',
                                                  'url': 'http://registry.svc.ci.openshift.org/ocp-s390x/release-s390x:4.4.0-0.nightl
y-s390x-2020-02-21-235937'}],
                                    'type': 'rich_text_section'}],
                      'type': 'rich_text'}],
                      ...

    and extract just the text parts to come up with:
    "Which build of sdn is in registry.svc.ci.openshift.org/ocp-s390x/release-s390x:4.4.0-0.nightly-s390x-2020-02-21-235937"
    """

    text = ""
    for block in json_data["data"]["blocks"]:
        for section in [el for el in block["elements"] if el["type"] == "rich_text_section"]:
            for element in [el for el in section["elements"] if "text" in el]:
                text += element["text"]

    # reformat to homogenize miscellaneous confusing bits
    return re.sub(r"\s+", " ", text).lstrip().rstrip(" ?").lower()


def repeat_in_chunks(so, name):
    """
    Repeat what the user says, one "sentence" at a time, in the indicated private channel.
    """

    # remove the directive at the beginning.
    text = re.sub(r"^[^:]+:", "", so.request_payload["data"]["text"])

    # split by eol and periods followed by a space. ignore formatting if possible.
    chunks = re.sub(r"(\S\S.)(\s+|$)", "\1\n", text, flags=re.M).splitlines()

    # find the requested channel
    channel = None
    for ch in so.web_client.conversations_list(types="private_channel"):
        if ch["name"] == name:
            channel = ch
            break
    if not channel:
        so.say(f"Sorry, I see no such channel {name}")
        return

    # send one message per chunk to private channel.
    for chunk in chunks:
        so.web_client.chat_postMessage(
            channel=channel["id"],
            text=chunk,
        )
