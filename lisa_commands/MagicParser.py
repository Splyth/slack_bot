import package.scrython as scrython

"""
Magic card search functionality moved in from CardBot
"""


def parse_magic_card(card_name):
    try:
        card = scrython.cards.Named(fuzzy=card_name)
        if "transform" in card.layout() or "split" in card.layout() or "flip" in card.layout()\
                or "adventure" in card.layout():
            return parse_slack_response_multi_faced(card)
        else:
            return parse_slack_response(card)
    except Exception as e:
        print(str(e))
        if "No cards found matching" in str(e):
            return "Sorry, card not found!"
        elif "Too many cards match ambiguous name" in str(e):
            return "Too many cards matched your query. Try a more specific request."
        else:
            return "Oops. Something went wrong. Let Robert know what you were querying and he'll look into it."


def parse_slack_response(card):
    try:
        image_uri = card.image_uris(image_type="normal")
    except Exception as e:
        print(str(e))
        image_uri = "*An error occurred while retrieving this card's image URL.*"
    try:
        card_text = card.oracle_text()
        # Italicize reminder text
        card_text = card_text.replace("(", "_(")
        card_text = card_text.replace(")", ")_")
    except KeyError:
        card_text = ""
    try:
        flavor_text_raw = card.flavor_text().split("\n")
        flavor_text = []
        for line in flavor_text_raw:
            line = "_" + line + "_"
            flavor_text.append(line)
        flavor_text = "\n".join(flavor_text)
    except KeyError:
        flavor_text = ""
    if "Creature" in card.type_line() or "Vehicle" in card.type_line():
        pt = card.power() + "/" + card.toughness()
    else:
        pt = ""
    if card.mana_cost():
        mana_cost = card.mana_cost()
    else:
        mana_cost = ""
    if "Planeswalker" in card.type_line():
        loyalty = "Loyalty: " + card.loyalty()
    else:
        loyalty = ""

    response = """
{imageurl}
*{cardname}* {mana_cost}
{type_line}
{oracle_text}
{flavor_text}
{PT}{loyalty}
    """.format(
        cardname=card.name(),
        mana_cost=replace_emojis(mana_cost),
        type_line=card.type_line(),
        oracle_text=replace_emojis(card_text),
        flavor_text=flavor_text,
        PT=pt.replace("*", "★"),
        loyalty=loyalty,
        imageurl=image_uri
    )
    response_lines = response.split("\n")
    for line in response_lines:
        if not line.strip():
            response_lines.remove(line)
    response = "\n".join(response_lines)
    return response


def parse_slack_response_multi_faced(card):
    response = ""
    if "transform" not in card.layout():
        try:
            response += card.image_uris(image_type="normal")
        except Exception as e:
            print(str(e))
            response += "*An error occurred while retrieving this card's image URL.*"
        transform = False
    else:
        transform = True
    for face in card.card_faces():
        try:
            card_text = face["oracle_text"]
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
        loyalty = ""
        if "loyalty" in face.keys():
            loyalty = "Loyalty: " + face["loyalty"]
        if transform:
            try:
                image_uri = face["image_uris"]["normal"]
            except Exception as e:
                print(str(e))
                image_uri = "*An error occurred while retrieving the image URL of the back face of this card.*"
        else:
            image_uri = ""

        response += """
{imageurl}
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
                imageurl=image_uri
        )
    response_lines = response.split("\n")
    for line in response_lines:
        if not line.strip():
            response_lines.remove(line)
    response = "\n".join(response_lines)
    return response


def replace_emojis(response):
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
