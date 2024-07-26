import urllib.request
import urllib.parse
import urllib.error
import json

SCRYFALL_BASE_URL = "https://api.scryfall.com/cards/named?fuzzy="

def parse_magic_card(card_name):
    try:
        card = json.loads(urllib.request.urlopen(SCRYFALL_BASE_URL + urllib.parse.quote(card_name)).read())
        return parse_slack_response(card)
    except urllib.error.HTTPError as e:
        print(str(e))
        if "404" in str(e):
            return "Sorry, card not found! Check your spelling, or be more specific, if there could be many cards that contain your search term."
        else:
            return "Oops. Something went wrong. Let Robert know what you were querying and he'll look into it."
    except Exception as e:
        print(str(e))
        return "Oops. Something went wrong. Let Robert know what you were querying and he'll look into it."


def parse_slack_response(card):
    # Image URIs on double-faced cards are stored inside the card_faces object, but are present in the top-level card object for single-faced cards.
    # However, cards with multiple "faces" that aren't double-sided (i.e. split cards) only have the image URI on the top-level card object.
    # To account for this ambiguity, parse image URIs first, then let parse_card_face handle the other relevant fields per face.
    try:
        image_uri = card["image_uris"]["normal"]
    except KeyError:
        image_uri = ""
        try:
            for face in card["card_faces"]:
                image_uri = image_uri + "\n" + face["image_uris"]["normal"]
        except KeyError:
            image_uri = "An error occurred retrieving this card's image URI."
    response = image_uri
    if "card_faces" in card.keys():
        # If card_faces exist, parse both faces individually and append.
        for face in card["card_faces"]:
            response = response + parse_card_face(face)
    else:
        # If single-faced, the top-level card object should still have all the info we need.
        # This may be fast and loose with type safety, but at least it's easy. Python dicts are fun!
        response = response + parse_card_face(card)
    response_lines = response.split("\n")
    for line in response_lines:
        if not line.strip():
            response_lines.remove(line)
    response = "\n".join(response_lines)
    return response


def parse_card_face(face):
    try:
        card_text = face["oracle_text"]
        # Italicize reminder text
        card_text = card_text.replace("(", "_(")
        card_text = card_text.replace(")", ")_")
    except KeyError:
        card_text = ""
    try:
        flavor_text_raw = face["flavor_text"].split("\n")
        flavor_text = []
        for line in flavor_text_raw:
            line = "_" + line + "_"
            flavor_text.append(line)
        flavor_text = "\n".join(flavor_text)
    except KeyError:
        flavor_text = ""
    if "Creature" in face["type_line"] or "Vehicle" in face["type_line"]:
        pt = face["power"] + "/" + face["toughness"]
    else:
        pt = ""
    if face["mana_cost"]:
        mana_cost = face["mana_cost"]
    else:
        mana_cost = ""
    if "Planeswalker" in face["type_line"]:
        loyalty = "Loyalty: " + face["type_line"]
    else:
        loyalty = ""

    response = """
*{cardname}* {mana_cost}
{type_line}
{oracle_text}
{flavor_text}
{PT}{loyalty}
    """.format(
        cardname=face["name"],
        mana_cost=replace_emojis(mana_cost),
        type_line=face["type_line"],
        oracle_text=replace_emojis(card_text),
        flavor_text=flavor_text,
        PT=pt.replace("*", "★"),
        loyalty=loyalty,
    )
    return response

def replace_emojis(response):
    # Bot responses on Slack sometimes don't render emojis right if the case doesn't match, particularly on mobile.
    # To fix this minor bug, an overcomplicated kludge goes through and forces all symbols (mana, tap, energy, etc) to lowercase.
    response_array = []
    response_split = response.split()
    for word in response_split:
        if word.startswith("{"):
            response_array.append(word.lower())
        else:
            response_array.append(word)
    response = " ".join(response_array)

    # this really should use regex but regex breaks my brain. spaghetti it is
    response = response.replace("½", "half")
    response = response.replace("∞", "inf")
    response = response.replace("{", ":mtg-")
    response = response.replace("}", ":")

    # remove the slash for phyrexian/hybrid
    response = response.replace("/P", "P")
    response = response.replace("/W", "W")
    response = response.replace("/U", "U")
    response = response.replace("/B", "B")
    response = response.replace("/R", "R")
    response = response.replace("/G", "G")

    # awkward hack for gleemax, which has the only mana symbol with no emoji
    response = response.replace(":mtg-1000000:", "{1000000}")

    return response
