import os
import csv

SEARCH_VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS',
                 'TTS', "5' UTR", "3' UTR"]
OUTPUT_ANNOTATION = "annotation_output.txt"
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.getcwd()), 'results')
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)


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


def get_occurence_counts(col, values, files):
    """
        Data is fetched from get_count_lists and stored in a variable.
        Writes data into CSV file.

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
    # data = dict(zip(values, [get_count(col, value, files)
    #                          for value in values]))
    with open(os.path.join(OUTPUT_DIRECTORY, OUTPUT_ANNOTATION), 'w') as file:
        filewriter = csv.writer(file, delimiter='\t')
        filewriter.writerow(['Values'] + [filename[:filename.index(".anno")]
                                          for filename in files])
        data = []
        for value in values:
            print 'Getting counts for value: ' + value + '...'
            row = list(get_count(col, value, files))
            filewriter.writerow([value] + row)
            data.append(row)
        print 'Getting column totals...'
        filewriter.writerow(['Total'] + [sum(x) for x in zip(*data)])

        # pie_plot(data, files)


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


def pie_plot(filenames, rows):
    for i, file in enumerate(files):
        pass


def find_locations_of_gene(gene_name, files):
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
    print 'Finding occurences of values under the "Annotation" column... ', \
          '(does not have to be exact match)'

    os.chdir('..')
    os.chdir('Dm')
    files = next(os.walk('.'))[2]

    print files

    get_occurence_counts('Annotation', SEARCH_VALUES, [file for file in files if '.anno' in file])
    print 'Done. Output file is: \'%s\'' % OUTPUT_ANNOTATION
    print 'Find occurences of a gene under the "Gene Name" column.'
    user_input = raw_input('Enter a gene name: ')
    print 'Finding...'
    find_locations_of_gene(user_input, [file for file in files if '.anno' in file])
    print 'Done.'
