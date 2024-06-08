import re
from requests.structures import CaseInsensitiveDict


def find_ats(text: str):
    return re.findall(r"\B@\w+", text)


def create_names_dict(guild):
    members = guild.members
    result = CaseInsensitiveDict()
    for each in members:
        result[each.name] = each.id
        if each.nick is not None:
            result[each.nick] = each.id
        if each.global_name is not None:
            result[each.global_name] = each.id
    return result


def find_discord_id(name: str, guild):
    the_dict = create_names_dict(guild=guild)
    try:
        return the_dict[name]
    except:  # noqa: E722
        return None


# gets a @name, returns <@discord_id>
# if id is not found, returns the input
def get_discord_mention(at_name: str, guild):
    name = at_name.split("@")[1]
    id = find_discord_id(name=name, guild=guild)
    if id is None:
        return at_name
    return f"<@{id}>"


def replace(text: str, guild):
    with_at = find_ats(text=text)
    for each in with_at:
        text = text.replace(each, get_discord_mention(at_name=each, guild=guild))
    return text
