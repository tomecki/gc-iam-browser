from collections import defaultdict
import json

from lxml import html
import requests

def permission_to_roles(row):
    permission = row.xpath('./td/code')[0].text
    roles = [role.text for role in row.xpath('./td/li/code')]
    return (permission, roles)

URL = "https://cloud.google.com/iam/docs/permissions-reference"
def main():
    result = {}
    response = requests.get(URL)
    tree = html.fromstring(response.content)
    rows = tree.xpath("//table/tbody/tr")
    for row in rows:
        permission, roles = permission_to_roles(row)
        result[permission] = roles

    role2permission = defaultdict(list)
    for permission, roles in result.items():
        for role in roles:
            role2permission[role].append(permission)

    with open('permission2role.json', 'w') as f:
        json.dump(result, f)

    with open('role2permission.json', 'w') as f:
        json.dump(role2permission, f)

    

    


if __name__ == "__main__":
    main()