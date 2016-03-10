import csv

FILENAMES = ['Akdemir_p53_Untr.anno', 'Botcheve_IMR90.anno',
             'Younger_Human_ChIP.anno', 'Akdemir_p53_DOX.anno']
VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS', 'TTS',
          "5' UTR", "3' UTR"]

# data structure for file = [{header1: value1-1, header2: value1-2, ...}
#                            {header1: value2-1, header2: value2-2, ...} ...]


def parse_file(filename):
    header = get_header(filename)
    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def get_header(filename):
    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        return reader.next()


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


def get_count_lists():
    for value in VALUES:
        count_list = list(get_count(value, 'Annotation'))
        yield count_list


def get_count(value, col):
    for filename in FILENAMES:
        file_data = parse_file(filename)
        count = 0
        for row in file_data:
            if value in row[col]:
                count += 1
        yield count


# data structure = {filename1: [row1, row2, ...],
#                   filename2: [row1, row2, ...]}


def assignment_3(gene_name):
    for filename in FILENAMES:
        file_data = parse_file(filename)
        header = get_header(filename)
        count = 0
        list_of_rows = []
        for row in file_data:
            if row['Gene Name'] == gene_name:
                count += 1
                list_of_rows.append(row)
        print '\033[1m' + '%-24s ' % (filename,),
        print '%i row(s) found with Gene Name=%r' % (count, gene_name),
        print '\033[0m'
        for i, row in enumerate(list_of_rows):
            print '\033[1m' + '%i:' % (i + 1,) + '\033[0m'
            for key in header:
                if row[key] == gene_name:
                    print '\033[1m' + '%24s: %s' % (key, row[key]) + '\033[0m'
                else:
                    print '%24s: %s' % (key, row[key])
        print ''


def print_dict(dict):
    for key in dict:
        print '%24s:' % (key,),
        print dict[key]

if __name__ == "__main__":
    # assignment_2()
    print '\n'
    assignment_3('EMBP1')

    # for item in parse_file('test.anno'):
    #     print item

    # for filename in FILENAMES:
    #     with open(filename) as file:
    #         reader = csv.reader(file, delimiter='\t')
    #         # reader.next()
    #         print reader.next()[7]
