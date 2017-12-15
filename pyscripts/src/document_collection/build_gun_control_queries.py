#!/usr/bin/python

from random import shuffle

# query components

# components to indicate editorial/opinion

editorial_components = [
        'editorial',
        'opinion',
        '"letter to the editor"',
        '"op ed"',
        'column',
        'commentary',
        '"in my opinion"'
        ]

# components to indicate related to topic of guns


gun_control_components = [
        '"gun control"',
        '"gun laws"',
        '"gun rights"',
        '"gun banners"',
        '"open carry" gun',
        '"gun control legislation"',
        '"flood our streets" guns',
        '"gun grabber"',
        '"hands off our guns"',
        '"gun haters"',
        '"anti gunners"',
        '"common sense" gun',
        '"my gun rights"',
        '"their gun rights"',
        '"gun worshipper"',
        '"gun fanatic"',
        '"gun extremist"',
        '"2nd amendment fanatic"',
        '"gun lobby agenda"',
        '"gun control madness"',
        '"gun maniacs"',
        '"anti gun maniacs"',
        '"coming for our guns"',
        '"gun zealot"',
        '"stay away from our guns"',
        '"right to bear arms" gun',
        '"anti gun lobby"',
        '"gun control lobby"',
        'gun agenda'
        ]


# "striping" components

geography_components = [
        "",
        "Atlanta",
        "Baltimore",
        "Boston",
        "Chicago",
        "Cleveland",
        "Des Moines",
        "Detroit",
        "Miami",
        "Charlotte",
        "Richmond",
        "New York",
        "Los Angeles",
        "San Francisco",
        "San Diego",
        "Phoenix",
        "Portland",
        "Washington",
        "Kansas City",
        "Pittsburgh",
        "Philadelphia",
        "Memphis",
        "Dallas",
        "Toronto",
        "Houston",
        "San Antonio",
        "Milwaukee",
        "Seattle"
        ]

gun_control_sub_topics = [
        "NRA",
        "\"assault weapons ban\"",
        "\"background checks\"",
        "\"another Columbine\"",
        "\"another Sandy Hook\"",
        "Newtown",
        "\"gun show loophole\"",
        "\"tough gun laws\"",
        "\"semi automatic\"",
        "\"Elliot Rodger\"",
        "\"Adam Lanza\"",
        "need",
        "massacre",
        "\"common sense\"",
        "\"2nd Amendment\"",
        "\"mass shootings\"",
        "Columbine",
        "Sandy Hook",
        "\"Richard Martinez\"",
        "\"gun violence\"",
        "\"gun culture\"",
        "reform",
        "\"the time has come\"",
        "\"it is time\"",
        "enough",
        "children",
        "sensible",
        "ban"
        ]

if __name__ == "__main__":
    all_queries = []
    for e in editorial_components:
        for g in gun_control_components:
            for s in gun_control_sub_topics:
                new_query = e + " " + g + " " + s
                new_query = new_query.rstrip(" ").lstrip(" ")
                all_queries.append(new_query)
    shuffle(all_queries)
    for query in all_queries:
        print query
