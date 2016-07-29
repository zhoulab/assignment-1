import os
import csv

BASE_DIR = os.path.dirname(os.getcwd())


def parse_anno_file(fpath):
    """
        Returns a generator object with each row in dictionary format.

        Returns
        -------
        ({header1: value1-1, header2: value1-2, ...},
         {header1: value2-1, header2: value2-2, ...}, ...)
            Where header(j) is the jth header in the file and
            value(i)-(j) is the value under the jth header and ith row in file.
    """
    with open(fpath) as f:
        reader = csv.reader(f, delimiter='\t')
        header = ['PeakID' if 'PeakID' in col_name else col_name
                  for col_name in reader.next()]
        for row in reader:
            yield dict(zip(header, (value for value in row)))


def get_occurence_counts(pth, col, values, files, output_dir, plots_dir):
    """
        Data is fetched from get_count_lists and stored in a variable.
        Writes data into CSV file.

        Parameters
        ----------
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
    folder = os.path.basename(pth)
    with open(os.path.join(output_dir, folder + '-results.txt'), 'w') as file:
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
            file_data[files[i]] = dict(zip(values, file_counts))
        pie_plot(file_data, values, folder, plots_dir)


def get_count(col, value, filepaths):
    """
        Returns
        -------
        (count_f1, count_f2, ...)
            Generator object of counts for instances of *value* under *col*
            (value does not have to be exact match)
    """
    for filepath in filepaths:
        yield len(list(get_occurences(col, value, filepath, exact=False)))


def pie_plot(file_data, values, folder, plots_dir):
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties

    font_props = FontProperties()
    font_props.set_size('small')

    for i, file in enumerate(file_data.keys()):
        if sum(file_data[file].values()) is 0:
            print 'No counts for {}.'.format(file)
            continue
        ax = plt.subplot(111)
        ax.axis('equal')

        counts = [file_data[file][value] for value in values]
        colors = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F',
                  '#B276B2', '#DECF3F']
        plt.title(file[:-5])
        wedges, texts = plt.pie(counts, colors=colors, startangle=90)
        for w in wedges:
            w.set_linewidth(0)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        labels = ['{} ({:.1f}%)'.format(value, 100 * file_data[file][value] / float(sum(file_data[file].values())))
                  for value in values]
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, .5), prop=font_props)
        plt.savefig(os.path.join(plots_dir, file[:-5] + '.jpg'))
        plt.gcf().clear()


def get_occurences(col, values, filepath, exact=True):
    """
        Parameters
        ----------
        col: str
        values: str or list
        filepath: str

        Returns
        -------
        (row1, row2, ...)
            Iterable of rows containing matching *value* under *col*.
    """
    if type(values) is str:
        values = [values]
    file_data = parse_anno_file(filepath)
    for row in file_data:
        if exact:
            if row[col] in values:
                yield row
        else:
            if any([val in row[col] for val in values]):
                yield row


def do_anno_analysis():
    search_values = ['non-coding', 'Intergenic', 'intron', 'exon',
                     'promoter-TSS', 'TTS', "5' UTR", "3' UTR"]
    output_dir = os.path.join(BASE_DIR, 'results/P53-ChIPSeq-Anno-results')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plots_dir = os.path.join(output_dir, 'plots')
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    folders = [os.path.join(BASE_DIR, 'data/Annos', f) for f in ['Dm', 'Mammals']]
    for folder_path in folders:
        fname = os.path.basename(folder_path)
        print ('{}: finding occurences of values under the '
               '"Annotation" column... ').format(fname)
        files = next(os.walk(folder_path))[2]

        get_occurence_counts(folder_path, 'Annotation', search_values,
                             [file for file in files if '.anno' in file],
                             output_dir, plots_dir)
        print 'Done. Output file is: "{}"'.format(fname + '-results.txt')
