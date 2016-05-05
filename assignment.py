import csv

FILENAMES = ['Akdemir_p53_Untr.anno', 'Botcheve_IMR90.anno',
             'Younger_Human_ChIP.anno', 'Akdemir_p53_DOX.anno']
VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS', 'TTS',
          "5' UTR", "3' UTR"]


def parse_file(filename):
    """
        Returns parsed data of file in a data structure:
            ({header1: value1-1, header2: value1-2, ...}
             {header1: value2-1, header2: value2-2, ...} ...)
        Where header(j) is the jth header in the file and
        value(i)-(j) is the value under the jth header and ith row in the file.
    """
    header = get_header(filename)
    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def get_header(filename):
    """Returns the elements of the first row in a list."""

    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        return reader.next()


def assignment_2():
    """
        Data is fetched from get_count_lists and stored in a variable.
        Prints data in a formatted output.
        Data structure:
            {value1: [count_f1, count_f2, ...],
             value2: [count_f1, count_f2, ...], ...}
    """
    data = dict(zip(VALUES, get_count_lists()))
    print '%24s' % (''),
    for name in FILENAMES:
        print '%-24s' % (name,),
    for value in VALUES:
        print '\n%-24s' % (value,),
        for count in data[value]:
            print '%-24s' % (count,),


def get_count_lists():
    """
        For each value, returns a generator object of
        list of counts for each file.

        Data structure:
            ([count_f1, count_f2, ...],
             [count_f1, count_f2, ...], ...)
    """
    for value in VALUES:
        count_list = get_count(value, 'Annotation')
        yield count_list


def get_count(value, col):
    """
        For each file, returns a generator object of counts
        for instances of the value under a column.

        Data structure:
            (count_f1, count_f2, ...)
    """
    for filename in FILENAMES:
        file_data = parse_file(filename)
        count = 0
        for row in file_data:
            if value in row[col]:
                count += 1
        yield count


def assignment_3(gene_name):
    """
        Data is fetched from get_data and stored in a variable
        then printed in a formatted output.

        Data structure:
            ((filename1, [row1, row2, ...]),
             (filename2, [row1, row2, ...]), ...)
    """
    data = get_data(gene_name)
    for (filename, list_of_rows) in data:
        header = get_header(filename)
        print '\033[1m' + '%24s:' % (filename,),
        print '%i row(s) found with Gene Name=%r' % (len(list_of_rows),
                                                     gene_name),
        print '\033[0m'
        for i, row in enumerate(list_of_rows):
            # print row number for formatted list
            print '\033[1m' + '%i:' % (i + 1,) + '\033[0m'
            for key in header:
                # special cases to bold Gene Name and truncate PeakID headers
                if row[key] == gene_name:
                    print '\033[1m' + '%24s: %s' % (key, row[key]) + '\033[0m'
                elif 'PeakID' in key:
                    print '%24s: %s' % ('PeakID', row[key])
                else:
                    print '%24s: %s' % (key, row[key])
        print ''


def get_data(gene_name):
    """
        For each file, returns generator object of tuple with
        filename and list of rows containing matching gene name.

        Data structure:
            ((filename1, [row1, row2, ...]),
             (filename2, [row1, row2, ...]), ...)
    """
    for filename in FILENAMES:
        file_data = parse_file(filename)
        count = 0
        list_of_rows = []
        for row in file_data:
            if row['Gene Name'] == gene_name:
                count += 1
                list_of_rows.append(row)
        yield (filename, list_of_rows)

if __name__ == "__main__":
    print 'Assignment 2:'
    assignment_2()
    print '\n\nAssignment 3:'
    user_input = raw_input('Enter a gene name: ')
    assignment_3(user_input)
