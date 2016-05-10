import csv

FILENAMES = ['Akdemir_p53_Untr.anno', 'Botcheve_IMR90.anno',
             'Younger_Human_ChIP.anno', 'Akdemir_p53_DOX.anno']
SEARCH_VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS',
                 'TTS', "5' UTR", "3' UTR"]


def parse_file(filename):
    """
        Returns a generator object with each row in dictionary format.

        Returns
        -------
        ({header1: value1-1, header2: value1-2, ...},
         {header1: value2-1, header2: value2-2, ...}, ...)
            Where header(j) is the jth header in the file and
            value(i)-(j) is the value under the jth header and ith row in file.
    """
    with open(filename) as file:
        reader = csv.reader(file, delimiter='\t')
        header = reader.next()
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def assignment_2(col, values, files):
    """
        Data is fetched from get_count_lists and stored in a variable.
        Prints data in a formatted output.

        Parameters
        ----------
        col: str
            Column of .anno file to search under
        values: list of str
            Values to search for under col
        files: list of str
            Filenames of .anno files to search

        Data Structures
        ---------------
        data: {value1: [count_f1, count_f2, ...],
               value2: [count_f1, count_f2, ...], ...}
    """
    data = dict(zip(values, [get_count(col, value, files)
                             for value in values]))
    print '\033[1m' + '%-24s' % ('Values'),
    for filename in files:
        print '%-24s' % (filename[:filename.index(".")],),
    print '\033[0m',
    for value in values:
        print '\n%-24s' % (value,),
        for count in data[value]:
            print '%-24s' % (count,),


def get_count(col, value, files):
    """
        Returns
        -------
        (count_f1, count_f2, ...)
            Generator object of counts for instances of *value* under *col*
            (value does not have to be exact match)
    """
    for filename in files:
        yield len(get_occurences(col, value, filename, False))


def get_occurrences_of_gene(gene_name, files):
    """
        Data is fetched from get_occurences and stored in a variable
        then printed in a formatted output.

        Parameters
        ----------
        gene_name: str
            Gene name to search for under the column 'Gene Name'
        files: list of str

        Data Structures
        ---------------
        data: [(filename1, [row1, row2, ...]),
               (filename2, [row1, row2, ...]), ...]
    """
    data = [(filename, get_occurences('Gene Name', gene_name, filename))
            for filename in files]
    for (filename, list_of_rows) in data:
        print '\033[1m' + '%s:' % (filename[:filename.index(".")],),
        print '%i row(s) found with Gene Name=%r' % (len(list_of_rows),
                                                     gene_name),
        print '\033[0m'
        if list_of_rows:
            print '%-3s%-16s%-16s%-8s' % ("#", "Start", "End", "Length")

        for (i, row) in enumerate(list_of_rows):
            start = int(row["Start"])
            end = int(row["End"])
            print '%-3i%-16i%-16i%-8i' % (i + 1, start, end, end - start + 1)
        print


def get_occurences(col, value, filename, exact=True):
    """
        Parameters
        ----------
        col: str
        value: str
        filename: str
        exact: bool
            True:   will look for exact value under *col*
            False:  will look for values under *col* that contain *value*

        Returns
        -------
        [row1, row2, ...]
            List of rows containing matching *value* under *col*.
    """
    file_data = parse_file(filename)
    list_of_rows = []
    for row in file_data:
        if exact:
            if value == row[col]:
                list_of_rows.append(row)
        else:
            if value in row[col]:
                list_of_rows.append(row)
    return list_of_rows

if __name__ == "__main__":
    print 'Finding occurences of values under the "Annotation" column.', \
          '(does not have to be exact match)'
    assignment_2('Annotation', SEARCH_VALUES, FILENAMES)

    print '\n\nFinding occurences of a gene under the "Gene Name" column.'
    user_input = raw_input('Enter a gene name: ')
    get_occurrences_of_gene(user_input, FILENAMES)
