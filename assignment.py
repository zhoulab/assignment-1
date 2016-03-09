import csv

FILENAMES = ['Akdemir_p53_Untr.anno', 'Botcheve_IMR90.anno',
             'Younger_Human_ChIP.anno', 'Akdemir_p53_DOX.anno']
VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS', 'TTS',
          "5' UTR", "3' UTR"]

# data structure for file = [{header1: value1-1, header2: value1-2, ...}
#                            {header1: value2-1, header2: value2-2, ...} ...]


def parse_file(filename):
    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        header = reader.next()
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def get_count(value, col):
    for filename in FILENAMES:
        with open(filename) as file:
            reader = csv.reader(file, delimiter='\t')
            count = 0
            for row in reader:
                if value in row[col]:
                    count += 1
            yield count


def get_count_lists():
    for value in VALUES:
        count_list = list(get_count(value, 7))
        yield count_list


# data structure = {value1: [count_f1, countf2, ...],
#                   value2: [count_f1, countf2, ...], ...}


def assignment_2():
    count_lists = get_count_lists()
    data = dict(zip(VALUES, count_lists))
    print '%24s' % (''),
    for name in FILENAMES:
        print '%-24s' % (name,),
    for value in VALUES:
        print '\n%-24s' % (value,),
        for count in data[value]:
            print '%-24s' % (count,),


# data structure = {filename1: [row1, row2, ...],
#                   filename2: [row1, row2, ...]}


def print_dict(dict):
    for key in dict:
        print key,
        print dict[key],
        print '\n\t'


def assignment_3(gene_name):
    for filename in FILENAMES:
        with open(filename) as file:
            print '%-24s' % (filename,)
            reader = csv.reader(file, delimiter='\t')
            header = reader.next()
            for row in reader:
                if row[15] == gene_name:
                    row_info = dict(zip(header, row))
                    print_dict(row_info)
            print ''

if __name__ == "__main__":
    # assignment_2()
    print '\n'
    # assignment_3('EMBP1')

    # for item in parse_file('test.anno'):
    #     print item
    for filename in FILENAMES:
        with open(filename) as file:
            reader = csv.reader(file, delimiter='\t')
            # reader.next()
            print reader.next()[7]
