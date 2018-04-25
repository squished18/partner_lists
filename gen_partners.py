#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gen_partners.py
© 2018 DAVID LAU ALL RIGHTS RESERVED
'''

import sys
import re
import copy
from operator import itemgetter, attrgetter, methodcaller

def read_class_file(file_name) :
    class_list = open(file_name, "r")

    lines = []
    for line in class_list :
        line = re.sub("#", "", line)
        line = re.split(",", line)
        if line[2] != 'Test' :
            line = filter(None, [element.strip() for element in line])
            lines.append(line)
    del lines[0][-1]

    class_list.close()

    header = lines[0]
    del lines[0]
    return [header, lines]

def get_lab_field(header) :
    print "Fields: "
    field_count = 0
    for element in header :
        print str(field_count) + ": " + element
        field_count = field_count + 1

    print
    field_number = input("Enter field number for lab section: ")

    while (field_number < 0 or field_number > field_count - 1) :
        field_number = input("Enter field number for lab section: ")

    return field_number

def get_TA_names(file_name) :
    TA_names = []
    TA_file = open(file_name, "r")
    for TA_name in TA_file :
        TA_names.append(TA_name.strip())

    return TA_names

def split_by_lab_section(input_lines, lab_field_number) :
    # identify the unique names of each lab section
    lab_section_names = []
    for line in input_lines :
        lab_section_names.append(line[lab_field_number])
    lab_section_names_unique = list(set(lab_section_names))

    # create list of lists
    split_list = []
    for section_index in range(len(lab_section_names_unique)) :
        split_list.append([])
    for line in input_lines :
        split_list[lab_section_names_unique.index(line[lab_field_number])].append(line[0:3])

    return [lab_section_names_unique, split_list]

def TA_grouping_indices(students_by_lab_section, TA_names) :
    section_index = 0
    index_bounds_by_TA = []
    for section in students_by_lab_section :
        index_bounds_by_TA.append([])
        print "section: " + str(section_index)
        print "size: " + str(len(section))
        average_num_students_per_TA = len(section) / len(TA_names)
        print "average size: " + str(average_num_students_per_TA)
        student_index = 0
        for TA_index in range(len(TA_names)) :
            student_index = student_index + average_num_students_per_TA
            # minimize groups with odd number of students
            if student_index % 2 == 1 :
                student_index = student_index - 1
            if (TA_index != len(TA_names) - 1) :
                index_bounds_by_TA[section_index].append(student_index - 1)
            else :
                index_bounds_by_TA[section_index].append(len(section) - 1)
        section_index = section_index + 1

    return index_bounds_by_TA

def group_by_TA(students_by_lab_section, TA_names) :
    index_bounds_by_TA = TA_grouping_indices(students_by_lab_section, TA_names)

    section_index = 0
    student_groups_by_TA = []
    for section in students_by_lab_section :
        student_groups_by_TA.append([])
        student_index = 0
        TA_index = 0
        student_groups_by_TA[section_index].append([])
        while student_index < len(section) :
            student_groups_by_TA[section_index][TA_index].append(section[student_index])
            if student_index == index_bounds_by_TA[section_index][TA_index] :
                TA_index = TA_index + 1
                if TA_index < len(TA_names) :
                    student_groups_by_TA[section_index].append([])
            student_index = student_index + 1
        section_index = section_index + 1

    return student_groups_by_TA

def assign_partners(student_list, start_number, offset) :
    student_list_copy = copy.deepcopy(student_list)
    new_student_list = []
    index = 0
    partner_number = start_number
    next_partner = 0
    while len(student_list_copy) > 0 :
        new_student_list.append(student_list_copy[index])
        new_student_list[-1].append(partner_number)
        partner_number = partner_number + next_partner
        next_partner = (next_partner + 1) % 2
        del student_list_copy[index]
        if (len(student_list_copy) > 0) :
            index = (index + offset) % len(student_list_copy)

    return [new_student_list, partner_number]

if len(sys.argv) < 2 :
    print "Usage: python gen_partners.py <class list file>"
    sys.exit(1)

TA_names = get_TA_names("TA_names.txt")
[header, input_lines] = read_class_file(sys.argv[1])
lab_field_number = get_lab_field(header)

input_lines = sorted(input_lines, key=itemgetter(lab_field_number,1))

[lab_section_names, students_by_lab_section] = split_by_lab_section(input_lines, lab_field_number)
student_groups_by_TA = group_by_TA(students_by_lab_section, TA_names)

counter = 0
for section_index in range(len(lab_section_names)) :
    print lab_section_names[section_index]
    for TA_index in range(len(TA_names)) :
        print TA_names[TA_index]
        for student in student_groups_by_TA[section_index][TA_index] :
            print str(counter) + ": " + str(student)
            counter = counter + 1

for assignment_num in range(1,10) :
    out_file = open("assignment-"+str(assignment_num)+"-partners.txt","w")
    for section_index in range(len(lab_section_names)) :
        out_file.write("Section: " + str(lab_section_names[section_index]) + "\n")
        group_number = 1
        for TA_index in range(len(TA_names)) :
            [assigned_partners,group_number] = assign_partners(student_groups_by_TA[section_index][TA_index], group_number, assignment_num - 1)
            assigned_partners = sorted(assigned_partners, key=itemgetter(1))
            for student in assigned_partners :
                out_file.write("{0:8} ".format(TA_names[TA_index]))
                out_file.write("{0:10}{3:5}  {1:20}{2:30}\n".format(*student))
        out_file.write("\n\n")
    out_file.close()
