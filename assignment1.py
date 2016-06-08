import os
import csv

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

SEARCH_VALUES = ['non-coding', 'Intergenic', 'intron', 'exon', 'promoter-TSS',
                 'TTS', "5' UTR", "3' UTR"]
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.getcwd()), 'results')
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)

FOLDERS = ['Dm', 'Mammals']


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


def get_occurence_counts(folder, pth, col, values, files):
    """
        Data is fetched from get_count_lists and stored in a variable.
        Writes data into CSV file.

        Parameters
        ----------
        folder: str
            Name of folder that files are under
        pth: str
            Path of *folder* directory
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
        file_data: {fname1: {v1: count_v1, v2: count_v2, ...},
                    fname2: {v1: count_v1, v2: count_v2, ...}, ...}
    """
    with open(os.path.join(OUTPUT_DIRECTORY, folder + '-results.txt'), 'w') as file:
        filewriter = csv.writer(file, delimiter='\t')
        filewriter.writerow(['Values'] + [filename[:filename.index(".anno")]
                                          for filename in files])
        data = []
        for value in values:
            print 'Getting counts for value: ' + value + '...'
            row = list(get_count(col, value, [os.path.join(pth, f) for f in files]))
            filewriter.writerow([value] + row)
            data.append(row)
        print 'Getting column totals...'
        filewriter.writerow(['Total'] + [sum(x) for x in zip(*data)])

        print 'Making pie plots'
        file_data = {}
        for i, file_counts in enumerate(zip(*data)):
            file_data[files[i]] = dict(zip(SEARCH_VALUES, file_counts))
        pie_plot(file_data, folder)


def get_count(col, value, filepaths):
    """
        Returns
        -------
        (count_f1, count_f2, ...)
            Generator object of counts for instances of *value* under *col*
            (value does not have to be exact match)
    """
    for filepath in filepaths:
        yield len(get_occurences(col, value, filepath, False))


def pie_plot(file_data, folder):
    plots_dir = os.path.join(os.path.dirname(os.getcwd()), folder + '_plots')
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    fontP = FontProperties()
    fontP.set_size('small')

    for i, file in enumerate(file_data.keys()):
        if sum(file_data[file].values()) is 0:
            print 'No counts for {}.'.format(file)
            continue
        ax = plt.subplot(111)
        ax.axis('equal')

        counts = [file_data[file][value] for value in SEARCH_VALUES]
        colors = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F',
                  '#B276B2', '#DECF3F']
        plt.title(file[:-5])
        wedges, texts = plt.pie(counts, colors=colors, startangle=90)
        for w in wedges:
            w.set_linewidth(0)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        labels = ['{} ({:.1f}%)'.format(value, 100 * file_data[file][value] / float(sum(file_data[file].values())))
                  for value in SEARCH_VALUES]
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, .5), prop=fontP)
        plt.savefig(os.path.join(plots_dir, file[:-5] + '.jpg'))
        plt.gcf().clear()


def get_occurences(col, value, filepath, exact=True):
    """
        Parameters
        ----------
        col: str
        value: str
        filepath: str
        exact: bool
            True:   will look for exact value under *col*
            False:  will look for values under *col* that contain *value*

        Returns
        -------
        [row1, row2, ...]
            List of rows containing matching *value* under *col*.
    """
    file_data = parse_file(filepath)
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
    for folder in FOLDERS:
        print '%s: finding occurences of values under the "Annotation" column... ' % folder
        pth = os.path.join(os.path.dirname(os.getcwd()), folder)
        files = next(os.walk(pth))[2]

        get_occurence_counts(folder, pth, 'Annotation', SEARCH_VALUES,
                             [file for file in files if '.anno' in file])
        print 'Done. Output file is: \'%s\'' % (folder + '-results.txt')
