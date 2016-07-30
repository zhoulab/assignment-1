import os
import csv
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.getcwd())


def create_dir(dirpath):
    """Return `dirpath` and create if it doesn't exist
    **The directory `os.path.dirname(dirpath)` must already exist.
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath


def parse_anno_file(fpath):
    """Return each row in a dictionary format.
    Use name 'PeakID' for column name rather than 'PeakID (...)'

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


def generate_occurence_count_files(fpaths, col, values, output_dir,
                                   plots_dir, val_colors):
    """Write occurence count data into tab-delimited txt file.
    Data is fetched from get_occurences and stored in `file_data`.

    Parameters
    ----------
    fpaths : list of str
        Filepaths of .anno files to search.
        All must be under the same folder (see variable `folder`)
    col : str
        Column of .anno file to search under
    values : list of str
        Values to search for under `col`

    Variables
    ---------
    folder : str
        name of common directory amongst files in `fpaths`
    files : list of str
        filenames without trailing ".anno"
    file_data : {fname1: OD{v1: count_v1, v2: count_v2, ...},
                 fname2: OD{v1: count_v1, v2: count_v2, ...}, ...}
    """
    folder = os.path.basename(os.path.dirname(fpaths[0]))
    files = [os.path.basename(path)[:-5] for path in fpaths]
    with open(os.path.join(output_dir, folder + '-results.txt'), 'w') as file:
        filewriter = csv.writer(file, delimiter='\t')
        filewriter.writerow(['Values'] + files)
        print 'Getting counts...'
        file_data = {fname: OrderedDict() for fname in files}
        for fpath, fname in zip(fpaths, files):
            anno_file_rows = list(parse_anno_file(fpath))
            for value in values:
                file_data[fname][value] = len(list(get_occurences(anno_file_rows,
                                              col, value, fpath, exact=False)))
        for value in values:
            filewriter.writerow([value] + [file_data[fname][value]
                                           for fname in files])
        filewriter.writerow(['Total'] + [sum(file_data[fname].values())
                                         for fname in files])
    print 'Creating pie plots...'
    generate_pie_plots(file_data, values, val_colors, plots_dir)


def generate_pie_plots(file_data, values, colors, plots_dir):
    """Create pie plots for each file in `file_data.keys()`

    Parameters
    ----------
    file_data : dict
        see `generate_occurence_counts()`
    values : list of str
    colors : list of str
        hex colors for corresponding element in ordered `values`
    plots_dir : filepath (str)
        directory to save plot JPEGs
    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties

    font_props = FontProperties()
    font_props.set_size('small')

    for file in file_data.keys():
        if sorted(file_data[file].keys()) != sorted(values):
            print 'Search values do not match for {}.'.format(file)
            continue
        if sum(file_data[file].values()) is 0:
            print 'No counts for {}.'.format(file)
            continue
        ax = plt.subplot(111)
        ax.axis('equal')

        counts = [file_data[file][value] for value in values]
        plt.title(file)
        wedges, texts = plt.pie(counts, colors=colors, startangle=90)
        for w in wedges:
            w.set_linewidth(0)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        labels = ['{} ({:.1f}%)'.format(value, 100 * file_data[file][value] /
                                        float(sum(file_data[file].values())))
                  for value in values]
        ax.legend(wedges, labels, loc='center left',
                  bbox_to_anchor=(1, .5), prop=font_props)
        plt.savefig(os.path.join(plots_dir, file + '.jpg'))
        plt.gcf().clear()


def get_occurences(anno_file_rows, col, values, fpath, exact=True):
    """Return rows containing matching `values` under `col`
    Parameters
    ----------
    anno_file_rows : iterable of dict
        see `parse_anno_file`
    col : str
    values : str or list
    fpath : str
    exact : bool
        define whether occurences should partially contain
        or match `values` exactly.

    Returns
    -------
    generator of dicts
    """
    if type(values) is str:
        values = [values]
    for row in anno_file_rows:
        if exact:
            if row[col] in values:
                yield row
        else:
            if any([val in row[col] for val in values]):
                yield row


def do_anno_count():
    """Generate count files and pie plots with pre-defined parameters.
    Variables
    ---------
    fodlers : list of str
        sample folders to use (under data/Annos)
    """
    folders = ['dm6_anno']
    folder_paths = [os.path.join(BASE_DIR, 'data/Annos', f)
                    for f in folders]
    search_values = ['non-coding', 'Intergenic', 'intron', 'exon',
                     'promoter-TSS', 'TTS', "5' UTR", "3' UTR"]
    val_colors = ['#4D4D4D', '#5DA5DA', '#FAA43A', '#60BD68',
                  '#F17CB0', '#B2912F', '#B276B2', '#DECF3F']
    output_dir = create_dir(os.path.join(BASE_DIR, 'results/P53-ChIPSeq-Anno-results'))
    plots_dir = create_dir(os.path.join(output_dir, 'plots'))

    for folder_path in folder_paths:
        dir_name = os.path.basename(folder_path)
        plots_subdir = create_dir(os.path.join(plots_dir, dir_name + '_plots'))
        print ('{}: finding occurences of values under the '
               '"Annotation" column... ').format(dir_name)
        anno_fpaths = [os.path.join(folder_path, f)
                       for f in next(os.walk(folder_path))[2]
                       if '.anno' in f]
        generate_occurence_count_files(anno_fpaths, 'Annotation', search_values,
                                       output_dir, plots_subdir, val_colors)
        print 'Done. Output file is: "{}"'.format(dir_name + '-results.txt')


