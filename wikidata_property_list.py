# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import urllib2
import json
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf8')

def load_properties_list():

    with codecs.open("PROPERTIES_dict.txt", "r", "utf8") as properties_json:
        return json.loads(properties_json.read())


def load_from_property(property_code):

    blcontinue = '0|0'
    request_for_entities = "https://www.wikidata.org/w/api.php?action=query&list=backlinks&blnamespace=0&bllimit=500&" \
                           "bltitle=Property:"+property_code+"&blcontinue="+blcontinue+"&format=json"

    entities_json = json.loads(urllib2.urlopen(request_for_entities).read())

    items_list = [item["title"] for item in entities_json["query"]["backlinks"]]

    if "continue" not in entities_json:
        return items_list
    else:

        blcontinue = entities_json["continue"]["blcontinue"]
        bool_sign = "continue" in entities_json
        while bool_sign:

            request_for_entities = "https://www.wikidata.org/w/api.php?action=query&list=backlinks&blnamespace=0&" \
                                   "bllimit=500&bltitle=Property:"+property_code+"&blcontinue="+blcontinue+"&format=json"

            entities_json = json.loads(urllib2.urlopen(request_for_entities).read())
            for item in entities_json["query"]["backlinks"]:
                items_list.append(item["title"])

            bool_sign = "continue" in entities_json
            if bool_sign:
                blcontinue = entities_json["continue"]["blcontinue"]

        return items_list


def iterate_properties(properties_dict, semantics, subsemantics):

    items_set = []
    for property_code in properties_dict[semantics][subsemantics]:
        print(property_code)
        items_list = load_from_property(property_code)
        items_set += items_list

    return set(items_set)


def assign_entity_to_item(item):

    languages = "ru|en|de|fr|it|fi|es|pt|ja|zh-hans"
    request_for_item = "https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels|aliases|descriptions&" \
                       "ids="+item+"&format=json&languages="+languages

    item_json = json.loads(urllib2.urlopen(request_for_item).read())

    entity_data = []
    aliases = []
    alternative_names = []
    terms = []
    description = []

    # fill alternative terms in Russian
    if 'aliases' in item_json["entities"][str(item)]:
        if 'ru' in item_json["entities"][str(item)]["aliases"]:
            for inner_dict in item_json["entities"][str(item)]["aliases"]['ru']:
                aliases.append(inner_dict['value'])
            alternative_names.append(['ALTERNATIVE_RUSSIAN', aliases])
        else:
            alternative_names.append(['ALTERNATIVE_RUSSIAN', ['']])

    # fill description in Russian
    if 'descriptions' in item_json["entities"][str(item)]:
        if 'ru' in item_json["entities"][str(item)]["descriptions"]:
            description.append(['DESCRIPTION', item_json["entities"][str(item)]["descriptions"]["ru"]["value"]])
        else:
            description.append(['DESCRIPTION', ''])

    # fill list of terms
    if 'labels' in item_json["entities"][str(item)]:
        for default_lang in languages.split('|'):
            if default_lang not in item_json["entities"][str(item)]["labels"].keys():
                terms.append([default_lang.upper(), ''])
        for language, term_data in item_json["entities"][str(item)]["labels"].iteritems():
            terms.append([language.upper(), term_data["value"]])

    terms.sort()

    entity_data.append([terms, alternative_names, description])

    return entity_data


def enter_range(items_set):

    print "Выбранная семантика (подсемантика) содержит", len(items_set), "сущностей."
    print "Выберите, сколько сущностей Вы хотите получить:"
    print

    while True:
        lower_edge = input("Введите число, с которого начать выводить сущности: ")
        upper_edge = input("Введите число, которым следует закончить вывод сущностей: ")
        if isinstance(lower_edge, int) and isinstance(upper_edge, int):
            if lower_edge > upper_edge:
                return upper_edge, lower_edge
                break
            else:
                return lower_edge, upper_edge
                break
        else:
            print("Введите число")


def walk_through_items(items_set, lower_edge=0, upper_edge=500):

    all_entities = []
    items_list = list(items_set)
    for item in items_list[lower_edge:upper_edge]:
        print(item)
        entity = assign_entity_to_item(item)
        all_entities.append(entity)

    return all_entities


def save_to_csv(entities_list):

    with codecs.open(r'entities.csv', 'w', 'utf8') as outfile:
        outfile.write('GERMAN'+'\t'+'ENGLISH'+'\t'+'SPAIN'+'\t'+'FINNISH'+'\t'+'FRENCH'+'\t'+'ITALIAN'+'\t'+'JAPAN'+'\t'+'PORTUGUESE'+'\t'+'RUSSIAN'+'\t'+'CHINESE'+'\t'+'ALTERNATIVE_RUSSIAN'+'\t'+'DESCRIPTION'+'\n')

        for dummy_list in entities_list:
            for entity in dummy_list:
                for language in entity[0]:
                    outfile.write(language[1]+'\t')
                for item in entity[1]:
                    outfile.write(', '.join(item[1])+'\t')
                for descr in entity[2]:
                    outfile.write(descr[1]+'\n')


properties_dict = load_properties_list()
items_set = iterate_properties(properties_dict, "Награды", "Награды")
lower_edge, upper_edge = enter_range(items_set)
entities = walk_through_items(items_set, lower_edge, upper_edge)
save_to_csv(entities)
