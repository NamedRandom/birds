#!/usr/bin/python3
import codecs
import os
import shutil
from lxml import html
import requests
import re


def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else None


class Bird:
    """ a bird datatype to make life easier  """

    def __init__(self, n):
        self.name = n.rstrip()
        # print(self.name)
        self.url = "https://www.allaboutbirds.org/guide/" + self.name.replace(" ", "_")
        self.imageurl = "https://www.allaboutbirds.org/guide/assets/photo/{}-480px.jpg"
        self.page = requests.get(self.url)
        # print(str(self.page.url))
        # print(str(self.page)+" "+ self.page.url)
        tree = html.fromstring(self.page.content)
        self.basic_description = tree.xpath('/html/body/div[3]/main/div[2]/div[1]/div/div[2]/p/text()')[0]
        # self.cool_facts = tree.xpath('/html/body/div[3]/main/div[2]/div[3]/ul/li/div/ul/*/text()')
        self.cool_facts = tree.xpath('/html/body/div[3]/main/div[2]/div[3]/ul/li/div/ul/descendant::*/text()')
        self.order = tree.xpath('/html/body/div[3]/main/div[2]/div[1]/div/div[1]/div[1]/div[2]/ul/li[1]/text()')[0]
        self.family = tree.xpath('/html/body/div[3]/main/div[2]/div[1]/div/div[1]/div[1]/div[2]/ul/li[2]/text()')[0]
        self.scientific_name = tree.xpath('/html/body/div[3]/main/div[2]/div[1]/div/div[1]/div[1]/div[2]/i/text()')[0]
        os.mkdir("./images/{}".format(self.name.replace(" ", "_")))
        file1 = open("./images/{}/image1.jpg".format(self.name.replace(" ", "_")), "wb")
        file2 = open("./images/{}/image2.jpg".format(self.name.replace(" ", "_")), "wb")
        if self.name not in noCap:
            self.caption1 = tree.xpath("/html/body/div[3]/main/div[1]/div/div/ul/li[1]/a/span/text()")[0]
            self.caption2 = tree.xpath("/html/body/div[3]/main/div[1]/div/div/ul/li[2]/a/span/text()")[0]
        else:
            self.caption1 = ""
            self.caption2 = ""

        image1 = self.imageurl.format(
            get_trailing_number(tree.xpath('/html/body/div[3]/main/div[1]/div/div/ul/li[1]/a/@href')[0]))
        image2 = self.imageurl.format(
            get_trailing_number(tree.xpath('/html/body/div[3]/main/div[1]/div/div/ul/li[2]/a/@href')[0]))
        resp1 = requests.get(image1, stream=True)
        resp2 = requests.get(image2, stream=True)
        resp1.raw.decode_content = True
        resp2.raw.decode_content = True
        shutil.copyfileobj(resp1.raw, file1)
        shutil.copyfileobj(resp2.raw, file2)
        print("Finished {}".format(self.name))

    def __str__(self):
        return 'A bird object, named {} at url {}'.format(self.name, self.page.url)


def latex_section(doc, bird):
    stuff = "\\section{" + bird.name + " \\textit{" + bird.scientific_name + "}}\n"
    stuff += "Order \\textit{" + bird.order + "} Family \\textit{" + bird.family + "}\n\n"
    stuff += bird.basic_description + "\n"
    stuff += """
\\begin{{figure}}[ht!]
\\centering
\\includegraphics[scale=.6]{{./images/{0}/image1.jpg}}
\\caption{{{1}}}
\\end{{figure}}
    """.format(bird.name.replace(" ","_"), bird.caption1)
    stuff += "\n\\subsection{Cool Facts}\n"
    stuff += "\\begin{itemize}"
    for fact in bird.cool_facts:
        stuff += "\\item " + fact.replace("$","\\$") + "\n"

    stuff += "\\end{itemize}"
    stuff += """
\\begin{{figure}}[ht!]
\\centering
\\includegraphics[scale=.6]{{./images/{0}/image2.jpg}}
\\caption{{{1}}}
\\end{{figure}}
    """.format(bird.name.replace(" ","_"), bird.caption2)
    if bird.name in noCap:
        for line in stuff:
            if "caption" in line:
                line = ""
    doc.write(stuff.replace("\u200b", "").replace("\u009D", "").replace("#", "\\#").replace("\u00b0", "").replace("&", "\\&"))


file = open("birds.txt")
if os.path.exists("birds.tex"):
    os.remove("birds.tex")
doc = codecs.open("birds.tex", "w+","utf-8")

if os.path.exists("./images"):
    shutil.rmtree("./images")
os.mkdir("./images")

noCap = {"Common Ground-Dove", "Rock Pigeon", "Chimney Swift", "Olive-sided Flycatcher", "Great Crested Flycatcher", "Black-billed Magpie", "Cactus Wren", "Marsh Wren", "Wood Thrush"}

doc.write("""
\\documentclass{article}
\\usepackage[utf8]{inputenc}

\\title{Birds}
\\author{McLean Highschool Science Olympiad}

\\usepackage{graphicx}

\\begin{document}

\\maketitle
""")

for line in file:
    if line != "\n":
        latex_section(doc,Bird(line))

doc.write("\\end{document}")

# os.system("pdflatex birds.tex")
